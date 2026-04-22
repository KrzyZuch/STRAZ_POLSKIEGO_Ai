import os
import json
import time
import re
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin

# Import Google GenAI
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("BŁĄD: Brak biblioteki google-genai. Zainstaluj: pip install google-genai")

def load_env(env_path: Path):
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env_vars[parts[0]] = parts[1]
    return env_vars

class ICDataSupplementer:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.clients = [genai.Client(api_key=k) for k in api_keys]
        self.db_path = Path("../test_db.jsonl")
        self.model_name = "gemini-1.5-flash"
        
        self.PDF_SEARCH_SOURCES = [
            { "name": "LCSC", "url": "https://www.lcsc.com/search?keyword=", "parse": "lcsc" },
            { "name": "DigiKey", "url": "https://www.digikey.com/en/search?q=", "parse": "digikey" },
            { "name": "Mouser", "url": "https://www.mouser.com/Search?q=", "parse": "mouser" },
            { "name": "SparkFun", "url": "https://www.sparkfun.com/search/results?term=", "parse": "sparkfun" },
        ]

    def get_client(self):
        if not self.clients:
            raise Exception("Brak skonfigurowanych klientów API.")
        client = self.clients[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.clients)
        return client

    def extract_pdf_link(self, html: str, source_type: str, base_url: str) -> Optional[str]:
        if not html:
            return None

        patterns = [
            r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
            r'data-datasheet=["\']([^"\']*\.pdf[^"\']*)["\']',
            r'src=["\']([^"\']*datasheet[^"\']*\.pdf[^"\']*)["\']',
            r'a[^>]+href=["\']([^"\']*product[^"\']*\.pdf[^"\']*)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match and match.group(1):
                url = match.group(1)
                if url.startswith("//"):
                    url = "https:" + url
                elif url.startswith("/"):
                    url = urljoin(base_url, url)
                elif not url.startswith("http"):
                    continue
                
                if ".pdf" in url.lower() or "datasheet" in url.lower():
                    return url

        if source_type == "lcsc":
            lcsc_match = re.search(r'"datasheetUrl"\s*:\s*"([^"]+)"', html)
            if lcsc_match and lcsc_match.group(1):
                return lcsc_match.group(1)

        return None

    def search_datasheet_pdf(self, part_number: str) -> Optional[str]:
        normalized_part = part_number.strip().replace(" ", "+")
        headers = { "User-Agent": "Mozilla/5.0 (compatible; StrazPrzyszlosciBot/1.0)" }
        
        for source in self.PDF_SEARCH_SOURCES:
            try:
                search_url = source["url"] + quote_plus(normalized_part)
                print(f"Szukanie w {source['name']}: {search_url}")
                response = requests.get(search_url, headers=headers, timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    pdf_link = self.extract_pdf_link(response.text, source["parse"], response.url)
                    if pdf_link:
                        print(f"Znaleziono PDF ({source['name']}): {pdf_link}")
                        return pdf_link
            except Exception as e:
                print(f"Błąd w {source['name']} dla {part_number}: {e}")
        
        return self.search_general_pdf(part_number)

    def search_general_pdf(self, part_number: str) -> Optional[str]:
        query = f"{part_number} datasheet filetype:pdf"
        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36" }
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
                for link in links:
                    if "uddg=" in link:
                        link = requests.utils.unquote(link.split("uddg=")[1].split("&")[0])
                    if link.lower().endswith(".pdf") or (".pdf" in link.lower() and "datasheet" in link.lower()):
                        if not any(x in link.lower() for x in ["google", "duckduckgo", "bing", "search"]):
                            return link
        except:
            pass
        return None

    def analyze_pdf_with_gemini(self, pdf_url: str, part_number: str) -> Dict[str, Any]:
        try:
            print(f"Pobieranie i analiza: {part_number} ({pdf_url})")
            pdf_response = requests.get(pdf_url, timeout=20, headers={"User-Agent": "Mozilla/5.0 (compatible; StrazPrzyszlosciBot/1.0)"})
            if pdf_response.status_code != 200:
                return {"error": "Pobieranie nieudane"}
            
            client = self.get_client()
            prompt = f"Wyekstrahuj parametry techniczne dla {part_number} z tego PDF. Zwróć JSON: {{'part_number': '{part_number}', 'description': '...', 'parameters': {{'Voltage': '...', 'Package': '...'}}}}"
            
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    genai_types.Part.from_bytes(data=pdf_response.content, mime_type="application/pdf"),
                    genai_types.Part.from_text(text=prompt)
                ],
                config=genai_types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}

    def save_to_db(self, data: Dict[str, Any]):
        record = {
            "timestamp_db": time.strftime("%Y-%m-%d %H:%M:%S"),
            "lookup_kind": "datasheet_automation",
            "query_text": data.get("part_number"),
            "matched_part_name": data.get("description"),
            "matched_part_number": data.get("part_number"),
            "status": "approved",
            "raw_payload_json": data
        }
        with open(self.db_path, "a") as f:
            f.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    env = load_env(Path("../../../.env"))
    api_key = env.get("GOOGLE_API_KEY") or env.get("GEMINI_API_KEY")
    
    if not api_key:
        print("BŁĄD: Brak klucza API w .env")
        exit(1)
        
    supplementer = ICDataSupplementer([api_key])
    
    list_path = Path("/home/krzysiek/.gemini/antigravity/brain/4eee6366-ec84-4b2d-ad1d-49f583597f01/scratch/ic_list_gen.json")
    if list_path.exists():
        with open(list_path, "r") as f:
            mpns = json.load(f)
    else:
        mpns = ["NE555P", "LM358P", "LM7805"]

    print(f"Rozpoczynanie przetwarzania {len(mpns)} układów...")
    for mpn in mpns[:50]: # Test na pierwszych 50
        pdf = supplementer.search_datasheet_pdf(mpn)
        if pdf:
            result = supplementer.analyze_pdf_with_gemini(pdf, mpn)
            if "error" not in result:
                supplementer.save_to_db(result)
                print(f"Sukces: {mpn}")
            else:
                print(f"Błąd analizy {mpn}: {result['error']}")
        else:
            print(f"Brak PDF dla {mpn}")
        
        time.sleep(5)
