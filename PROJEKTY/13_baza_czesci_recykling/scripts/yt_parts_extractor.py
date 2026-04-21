import os
import sys
import json
import time
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Importowanie bibliotek Google GenAI (zakładając obecność w środowisku)
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("BŁĄD: Brak biblioteki google-genai. Zainstaluj: pip install google-genai")
    sys.exit(1)

class YTPartsExtractor:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.clients = [genai.Client(api_key=k) for k in api_keys]
        
        # Modele zgodnie z dyspozycją użytkownika - Faza 1 i 2 na Gemma 4
        self.MODEL_ANALYSIS = "gemma-4-31b-it" 
        self.MODEL_VERIFICATION = "gemma-4-31b-it" 

    @staticmethod
    def normalize_part_number(value: str) -> str:
        return re.sub(r"[^A-Z0-9._+\-/]", "", str(value or "").strip().upper())

    @staticmethod
    def slugify(value: str, fallback: str = "unknown-part") -> str:
        normalized = str(value or "").strip().lower()
        normalized = (
            normalized.replace("ą", "a").replace("ć", "c").replace("ę", "e")
            .replace("ł", "l").replace("ń", "n").replace("ó", "o")
            .replace("ś", "s").replace("ź", "z").replace("ż", "z")
        )
        slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
        return slug or fallback

    def to_submission_records(self, process_result: Dict[str, Any], ingest_source: str = "youtube_gemma") -> List[Dict[str, Any]]:
        """
        Konwertuje wynik `process_url()` do tego samego kontraktu kolejki,
        z którego korzysta bot Telegram i pipeline sync_recycled_queue.py.
        """
        device_model = str(process_result.get("device") or "").strip()
        records: List[Dict[str, Any]] = []
        for item in process_result.get("results", []):
            part_name = str(item.get("part_name") or "").strip() or "Unknown Part"
            part_number = str(item.get("part_number") or "").strip() or part_name
            confidence = float(item.get("confidence") or 0.5)
            evidence_timecode = item.get("timestamp_seconds")
            source_url = str(item.get("yt_link_with_time") or process_result.get("url") or "").strip()
            normalized_part_number = self.normalize_part_number(part_number)
            records.append(
                {
                    "lookup_kind": "youtube_part_ingest",
                    "query_text": device_model,
                    "recognized_brand": "",
                    "recognized_model": device_model,
                    "matched_part_name": part_name,
                    "matched_part_number": part_number,
                    "master_part_key": normalized_part_number or self.slugify(part_name),
                    "status": "approved",
                    "ingest_source": ingest_source,
                    "evidence_url": source_url,
                    "evidence_timecode": str(evidence_timecode) if evidence_timecode is not None else "",
                    "raw_payload_json": {
                        "device_model": device_model,
                        "part_name": part_name,
                        "part_number": part_number,
                        "normalized_part_number": normalized_part_number,
                        "confidence": confidence,
                        "source_url": source_url,
                        "timestamp_seconds": evidence_timecode,
                        "context_note": item.get("context_note", ""),
                        "verification": item.get("verification", {}),
                    },
                }
            )
        return records
        
    def get_client(self):
        client = self.clients[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.clients)
        return client

    def verify_with_frame(self, high_res_video_path: str, timestamp: int, expected_part_number: str):
        """
        Faza 2: Wycięcie klatki z LOKALNEGO pliku wideo WYSOKIEJ JAKOŚCI.
        """
        frame_path = f"temp_frame_{timestamp}.jpg"
        print(f"📸 Wycinam klatkę HQ z lokalnego pliku ({timestamp}s)...")
        
        try:
            # Błyskawiczne wycięcie klatki z pobranego wideo (bez YT-DLP)
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(timestamp), "-i", high_res_video_path,
                "-vframes", "1", "-q:v", "2", frame_path
            ], capture_output=True)
            
            if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
                return {"verified": False, "observed_text": "Błąd wycinania klatki (pusty plik)"}, "Błąd"

            client = self.get_client()
            with open(frame_path, "rb") as f:
                img_data = f.read()

            prompt = f"Spójrz na to zdjęcie. Czy widzisz na nim wyraźnie numer: '{expected_part_number}'? Odpowiedz TYLKO JSON: {{\"verified\": true/false, \"observed_text\": \"co widzisz\"}}"
            
            response = client.models.generate_content(
                model=self.MODEL_VERIFICATION,
                contents=[
                    genai_types.Part.from_bytes(data=img_data, mime_type="image/jpeg"),
                    genai_types.Part.from_text(text=prompt)
                ]
            )
            
            os.remove(frame_path)
            return json.loads(response.text), None
        except Exception as e:
            return {"verified": False, "observed_text": f"Błąd: {str(e)}"}, "Błąd"

    def analyze_video_context(self, video_path: str, youtube_url: str):
        if not os.path.exists(video_path) or os.path.getsize(video_path) < 1000:
            raise Exception(f"BŁĄD: Plik wideo {video_path} nie istnieje lub jest uszkodzony (blokada bota?).")
            
        client = self.get_client()
        print(f"🚀 Przesyłam wideo do File API: {video_path}")
        video_file = client.files.upload(file=video_path)
        
        # Czekanie na przetworzenie...
        while video_file.state.name == "PROCESSING":
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception("Błąd przetwarzania wideo przez Google File API.")

        system_instruction = """
        Jesteś ekspertem inżynierii odwrotnej i serwisantem AGD/RTV. 
        Twoim zadaniem jest analiza filmu z naprawy w celu zidentyfikowania konkretnych części zamiennych.
        
        ZASADY ANTY-HALUCYNACYJNE:
        1. Podawaj numery części TYLKO jeśli widnieją na naklejkach, grawerach lub są wyraźnie wypowiedziane w kontekście pokazywanego elementu.
        2. Musisz podać DOKŁADNY CZAS (timestamp w sekundach), w którym dana część lub jej numer jest najlepiej widoczna.
        3. Jeśli nie jesteś pewien numeru - oznacz go jako "UNCERTAIN".
        4. Rozróżniaj model całego urządzenia od numeru konkretnej części.
        
        FORMAT WYJŚCIOWY (JSON):
        {
          "device_model": "Dokładny model urządzenia",
          "detected_parts": [
            {
              "part_name": "Nazwa części (np. pompa odpływowa)",
              "part_number": "Numer seryjny/katalogowy",
              "timestamp_seconds": 124,
              "confidence": 0.0-1.0,
              "context_note": "Dlaczego uważasz, że to ta część?"
            }
          ]
        }
        """
        
        prompt = f"Przeanalizuj ten film z YouTube ({youtube_url}). Skup się na identyfikacji części. Podaj precyzyjne czasy dla każdej znalezionej części."
        
        print("🧠 Analiza multimodalna w toku...")
        response = client.models.generate_content(
            model=self.MODEL_ANALYSIS,
            contents=[
                genai_types.Content(role="user", parts=[
                    genai_types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    genai_types.Part.from_text(text=prompt)
                ])
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)

    def process_url(self, youtube_url: str):
        base_time = int(time.time())
        video_low = f"temp_low_{base_time}.mp4"
        video_high = f"temp_high_{base_time}.mp4"
        high_res_downloaded = False
        
        # --- 1. POBIERANIE LOW-RES DO ANALIZY API (Max 360p) ---
        print(f"📥 Pobieram wideo (low-res) do File API: {youtube_url}...")
        subprocess.run([
            "yt-dlp",
            "--cookies-from-browser", "firefox",
            "--remote-components", "ejs:github",
            "--js-runtimes", "node:/home/krzysiek/.nvm/versions/node/v24.13.1/bin/node",
            "-f", "best[height<=360]", # Zmniejszono do 360p dla oszczędności transferu
            "-o", video_low, 
            youtube_url
        ])
        
        print("🔇 Usuwam ścieżkę dźwiękową z low-res...")
        silent_low = f"silent_{video_low}"
        subprocess.run([
            "ffmpeg", "-y", "-i", video_low, 
            "-c:v", "copy", "-an", silent_low
        ], capture_output=True)
        
        if os.path.exists(silent_low):
            os.replace(silent_low, video_low)

        try:
            # 2. Analiza kontekstowa (wysyłamy szybki plik LOW-RES)
            analysis = self.analyze_video_context(video_low, youtube_url)
            
            final_results = []
            parts_to_verify = [p for p in analysis.get("detected_parts", []) if p["part_number"] != "UNCERTAIN"]
            
            # --- 3. POBIERAMY HIGH-RES TYLKO JEŚLI JEST CO WERYFIKOWAĆ ---
            if parts_to_verify:
                print(f"🌟 Znaleziono {len(parts_to_verify)} części do weryfikacji! Pobieram plik High-Res (Video Only)...")
                subprocess.run([
                    "yt-dlp",
                    "--cookies-from-browser", "firefox",
                    "--remote-components", "ejs:github",
                    "--js-runtimes", "node:/home/krzysiek/.nvm/versions/node/v24.13.1/bin/node",
                    # Format: Tylko wideo (bez audio), max 720p, wymuś MP4
                    "-f", "bestvideo[height<=720][ext=mp4]/best[height<=720][ext=mp4]", 
                    "--merge-output-format", "mp4", # Zapobiega tworzeniu plików .mkv
                    "-o", video_high, 
                    youtube_url
                ])
                high_res_downloaded = os.path.exists(video_high)
            else:
                print("⏭ Brak konkretnych numerów części. Pomijam pobieranie High-Res.")

            # 4. Weryfikacja ze stopklatek
            for part in analysis.get("detected_parts", []):
                if part["part_number"] != "UNCERTAIN":
                    if high_res_downloaded:
                        ver, err = self.verify_with_frame(video_high, part["timestamp_seconds"], part["part_number"])
                        part["verification"] = ver
                    else:
                        part["verification"] = {"verified": False, "observed_text": "Nie pobrano High-Res ze względu na błąd"}
                
                part["yt_link_with_time"] = f"{youtube_url}&t={part['timestamp_seconds']}s"
                final_results.append(part)
                
            return {
                "url": youtube_url,
                "device": analysis.get("device_model"),
                "results": final_results
            }
            
        finally:
            # Niezależnie od wszystkiego - sprzątamy po sobie oba pliki
            if os.path.exists(video_low):
                os.remove(video_low)
            if high_res_downloaded and os.path.exists(video_high):
                os.remove(video_high)
