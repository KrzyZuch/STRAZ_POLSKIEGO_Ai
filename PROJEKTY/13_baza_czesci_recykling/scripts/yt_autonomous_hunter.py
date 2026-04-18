#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import List, Dict, Any, Optional

# Importowanie bibliotek Google GenAI
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("BŁĄD: Brak biblioteki google-genai. Zainstaluj: pip install google-genai")
    sys.exit(1)

# --- Konfiguracja ścieżek ---
BASE_DIR = Path("/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test")
RESULTS_FILE = BASE_DIR / "results" / "test_db.jsonl"
HISTORY_FILE = BASE_DIR / "processed_videos.json"
LOG_DIR = BASE_DIR / "logs"

# Słowa kluczowe i influencerzy (Priorytet: Polska Elektronika i Elektrośmieci)
KEYWORDS = [
    "Daniel Rakowiecki naprawa", "serwis elektroniki laptopy", "naprawa telewizora płyta główna",
    "elektrośmieci odzysk części", "naprawa elektroniki AGD moduł", "diagnostyka płyt głównych",
    "wymiana procesora laptop", "naprawa matrycy TV", "serwis RTV elektronika",
    "Krzysztof SQ5RIQ naprawa", "Ivanoe naprawa elektroniki", "naprawa zasilacza TV",
    "elektronika z recyklingu", "naprawa karty graficznej PL", "odzyskiwanie komponentów"
]


# ==========================================
# KLASA: YTPartsExtractor (Logika pobierania i AI)
# ==========================================
class YTPartsExtractor:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.clients = [genai.Client(api_key=k) for k in api_keys]
        
        # Używamy modeli określonych w poprzednich iteracjach
        self.MODEL_ANALYSIS = "gemma-4-31b-it" 
        self.MODEL_VERIFICATION = "gemma-4-31b-it" 
        
    def get_client(self):
        client = self.clients[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.clients)
        return client

    def get_video_duration(self, video_path: str) -> float:
        """Pobiera długość wideo w sekundach przy pomocy ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"⚠ Nie udało się pobrać długości wideo: {e}")
            return 0.0

    def verify_with_frame(self, high_res_video_path: str, timestamp: int, expected_part_number: str):
        """Faza 2: Wycięcie klatki z LOKALNEGO pliku wideo WYSOKIEJ JAKOŚCI."""
        frame_path = f"temp_frame_{timestamp}.jpg"
        print(f"📸 Wycinam klatkę HQ z lokalnego pliku ({timestamp}s)...")
        
        try:
            # Błyskawiczne wycięcie klatki z pobranego wideo
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
            
            try:
                # Czyszczenie odpowiedzi na wypadek gdyby model dokleił znaczniki markdown
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                return json.loads(clean_text), None
            except json.JSONDecodeError:
                return {"verified": False, "observed_text": f"Błąd parsowania odpowiedzi modelu: {response.text}"}, "Błąd JSON"
                
        except Exception as e:
            return {"verified": False, "observed_text": f"Błąd API: {str(e)}"}, "Błąd"

    def analyze_video_context(self, video_path: str, youtube_url: str):
        if not os.path.exists(video_path) or os.path.getsize(video_path) < 1000:
            raise Exception(f"BŁĄD: Plik wideo {video_path} nie istnieje lub jest uszkodzony.")
            
        client = self.get_client()
        print(f"🚀 Przesyłam wideo do File API: {video_path}")
        video_file = client.files.upload(file=video_path)
        
        # Czekanie na przetworzenie...
        print("⏳ Oczekuję na przetworzenie wideo w chmurze Google...")
        while video_file.state.name == "PROCESSING":
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception("Błąd przetwarzania wideo przez Google File API.")

        system_instruction = """
        Jesteś ekspertem inżynierii odwrotnej i serwisantem AGD/RTV/IT. 
        Twoim zadaniem jest analiza WYCISZONEGO filmu z naprawy w celu zidentyfikowania konkretnych części zamiennych.
        
        ZASADY ANTY-HALUCYNACYJNE:
        1. Otrzymujesz wideo BEZ DŹWIĘKU. Podawaj numery części TYLKO jeśli widnieją na wyraźnie widocznych naklejkach, grawerach lub nadrukach PCB.
        2. Musisz podać DOKŁADNY CZAS (timestamp w sekundach), w którym dana część lub jej numer jest NAJLEPIEJ WIDOCZNA na zbliżeniu.
        3. Jeśli widzisz część, ale numer jest niewyraźny lub nie możesz go odczytać - oznacz go ZAWSZE jako "UNCERTAIN".
        4. Rozróżniaj model całego urządzenia od numeru konkretnej części.
        
        FORMAT WYJŚCIOWY (JSON):
        {
          "device_model": "Dokładny model urządzenia",
          "detected_parts": [
            {
              "part_name": "Nazwa części (np. pompa odpływowa / zasilacz / płyta główna)",
              "part_number": "Numer seryjny/katalogowy (lub UNCERTAIN)",
              "timestamp_seconds": 124,
              "confidence": 0.0-1.0,
              "context_note": "Dlaczego uważasz, że to ta część?"
            }
          ]
        }
        """
        
        prompt = f"Przeanalizuj ten film z YouTube ({youtube_url}). Skup się na identyfikacji części z ich numerami. Podaj precyzyjne czasy dla każdej znalezionej części."
        
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
        
        # ZWALNIANIE MIEJSCA - Usunięcie wideo z Google File API po dokonanej analizie
        try:
            client.files.delete(name=video_file.name)
        except Exception as e:
            print(f"⚠ Nie udało się usunąć pliku z API (możliwy brak uprawnień): {e}")
            
        return json.loads(response.text)

    def process_url(self, youtube_url: str):
        base_time = int(time.time())
        video_low = f"temp_low_{base_time}.mp4"
        video_high = f"temp_high_{base_time}.mp4"
        high_res_downloaded = False
        
        # --- 1. POBIERANIE LOW-RES DO ANALIZY API (Max 360p) ---
        print(f"📥 Pobieram wideo (low-res) do analizy wstępnej: {youtube_url}...")
        subprocess.run([
            "yt-dlp",
            "--cookies-from-browser", "firefox",
            "--remote-components", "ejs:github",
            "--js-runtimes", "node:/home/krzysiek/.nvm/versions/node/v24.13.1/bin/node",
            "-f", "best[height<=360]", 
            "-o", video_low, 
            youtube_url
        ], capture_output=True)
        
        if not os.path.exists(video_low):
            print(f"❌ Błąd: yt-dlp nie mógł pobrać filmu (odrzucony / zablokowany).")
            return None

        # --- 2. OMINIĘCIE LIMITU API (TIME-LAPSE MAX 15 MINUT) ---
        duration = self.get_video_duration(video_low)
        speed_factor = 1.0
        
        # Ograniczamy wideo do max 900 sekund (15 minut), co daje ok. 230 tys. tokenów (bezpiecznie < 262k)
        TARGET_MAX_SECONDS = 900.0 
        
        if duration > TARGET_MAX_SECONDS:
            speed_factor = duration / TARGET_MAX_SECONDS
            print(f"⏱️ Wideo przekracza limit ({duration:.0f}s). Przyspieszam algorytm Time-Lapse {speed_factor:.2f}x (do 15 min)...")
            processed_low = f"processed_{video_low}"
            
            subprocess.run([
                "ffmpeg", "-y", "-i", video_low, 
                "-filter:v", f"setpts=PTS/{speed_factor}", 
                "-c:v", "libx264", "-preset", "ultrafast", "-an", processed_low
            ], capture_output=True)
            
            if os.path.exists(processed_low):
                os.replace(processed_low, video_low)
        else:
            print("🔇 Usuwam ścieżkę dźwiękową (Gemma/Gemini w Google API odrzuca wideo z audio)...")
            silent_low = f"silent_{video_low}"
            subprocess.run([
                "ffmpeg", "-y", "-i", video_low, 
                "-c:v", "copy", "-an", silent_low
            ], capture_output=True)
            
            if os.path.exists(silent_low):
                os.replace(silent_low, video_low)

        try:
            # 3. Analiza kontekstowa przez Google GenAI
            analysis = self.analyze_video_context(video_low, youtube_url)
            
            final_results = []
            parts_to_verify = [p for p in analysis.get("detected_parts", []) if p["part_number"] != "UNCERTAIN"]
            
            # --- 4. POBIERAMY HIGH-RES TYLKO JEŚLI ZNALEZIONO KONKRETNE NUMERY ---
            if parts_to_verify:
                print(f"🌟 Znaleziono {len(parts_to_verify)} części do weryfikacji! Pobieram plik High-Res (Tylko Video)...")
                subprocess.run([
                    "yt-dlp",
                    "--cookies-from-browser", "firefox",
                    "--remote-components", "ejs:github",
                    "--js-runtimes", "node:/home/krzysiek/.nvm/versions/node/v24.13.1/bin/node",
                    "-f", "bestvideo[height<=720][ext=mp4]/best[height<=720][ext=mp4]", 
                    "--merge-output-format", "mp4", 
                    "-o", video_high, 
                    youtube_url
                ], capture_output=True)
                high_res_downloaded = os.path.exists(video_high)
            else:
                print("⏭ AI nie znalazło na filmie żadnych wyraźnych numerów seryjnych. Pomijam pobieranie High-Res.")

            # --- 5. WERYFIKACJA (Z KOREKTĄ CZASU) ---
            for part in analysis.get("detected_parts", []):
                
                # PRZYWRÓCENIE ORYGINALNEGO CZASU
                original_ts = int(part["timestamp_seconds"] * speed_factor)
                part["timestamp_seconds"] = original_ts
                
                if part["part_number"] != "UNCERTAIN":
                    if high_res_downloaded:
                        ver, err = self.verify_with_frame(video_high, original_ts, part["part_number"])
                        part["verification"] = ver
                    else:
                        part["verification"] = {"verified": False, "observed_text": "Brak pliku High-Res do weryfikacji"}
                else:
                    part["verification"] = {"verified": False, "observed_text": "Brak numeru do weryfikacji"}
                
                part["yt_link_with_time"] = f"{youtube_url}&t={original_ts}s"
                final_results.append(part)
                
            return {
                "url": youtube_url,
                "device": analysis.get("device_model", "Nieznany Model"),
                "results": final_results
            }
            
        finally:
            # --- SPRZĄTANIE LOKALNE ---
            if os.path.exists(video_low):
                os.remove(video_low)
            if high_res_downloaded and os.path.exists(video_high):
                os.remove(video_high)


# ==========================================
# KLASA: YTHunter (Orkiestrator API i Przeszukiwania)
# ==========================================
class YTHunter:
    def __init__(self, yt_api_key: str, gemini_api_keys: list):
        self.yt_api_key = yt_api_key
        self.extractor = YTPartsExtractor(gemini_api_keys)
        self.history = self.load_history()

    def load_history(self):
        # Upewniamy się, że folder na wyniki istnieje
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
            try:
                with open(HISTORY_FILE, "r") as f:
                    return set(json.load(f))
            except json.JSONDecodeError:
                return set()
        return set()

    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(self.history), f)

    def search_videos(self, query: str, max_results=5):
        print(f"🔍 Szukam: {query}")
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.yt_api_key,
            "relevanceLanguage": "pl" if any(c in query.lower() for c in "ąćęłńóśźż") else "en"
        }
        url = f"https://www.googleapis.com/youtube/v3/search?{urlencode(params)}"
        req = Request(url, headers={"Accept": "application/json"})
        
        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("items", [])
        except Exception as e:
            print(f"❌ Błąd wyszukiwania YouTube: {e}")
            return []

    def hunt(self):
        for kw in KEYWORDS:
            videos = self.search_videos(kw)
            for v in videos:
                vid_id = v["id"]["videoId"]
                if vid_id in self.history:
                    print(f"⏭️ Pomijam (już w bazie): {vid_id}")
                    continue
                
                # Naprawiony ucięty kod tworzenia URLa z oryginalnego skryptu
                yt_url = f"https://www.youtube.com/watch?v={vid_id}"
                print(f"🎯 Atakuję film: {v['snippet']['title']} ({yt_url})")
                
                try:
                    # Przetwarzanie przez multimodalne API
                    result = self.extractor.process_url(yt_url)
                    
                    if result and result.get("results"):
                        self.save_result(result)
                        print(f"✨ Sukces! Wyciągnięto {len(result['results'])} części.")
                    
                    self.history.add(vid_id)
                    self.save_history()
                    
                except Exception as e:
                    print(f"⚠️ Błąd podczas przetwarzania {vid_id}: {e}")
                
                # Pauza między filmami, żeby nie przegrzać API/systemu
                time.sleep(10)

    def save_result(self, result):
        # Zapisujemy każdą wykrytą część jako osobny wiersz (prawdziwa baza części)
        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            device = result.get("device", "Unknown")
            url = result.get("url", "")
            
            for part in result.get("results", []):
                # Tworzymy płaski rekord dla lepszej czytelności wierszami
                record = {
                    "timestamp_db": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "device": device,
                    "part_name": part.get("part_name"),
                    "part_number": part.get("part_number"),
                    "confidence": part.get("confidence"),
                    "yt_link": part.get("yt_link_with_time"),
                    "verification": part.get("verification", {}),
                    "source_video": url
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ==========================================
# MAIN ROUTINE
# ==========================================
if __name__ == "__main__":
    # Automatyczne pobieranie kluczy
    YT_KEY = os.environ.get("YOUTUBE_API_KEY")
    GEMINI_KEYS = [os.environ.get("GEMINI_API_KEY")]

    if not YT_KEY or not GEMINI_KEYS[0]:
        print("❌ Brak kluczy API (YOUTUBE_API_KEY / GEMINI_API_KEY)!")
        sys.exit(1)

    hunter = YTHunter(YT_KEY, GEMINI_KEYS)
    print("🚦 Start Autonomicznego Łowcy Części (Test Mode)...")
    hunter.hunt()