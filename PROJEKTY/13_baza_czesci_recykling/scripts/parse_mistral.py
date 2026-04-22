import json
import re

with open('/home/krzysiek/.gemini/antigravity/brain/4eee6366-ec84-4b2d-ad1d-49f583597f01/scratch/ic_list_mistral.json', 'r') as f:
    data = json.load(f)

content = data['choices'][0]['message']['content']
# Wyciąganie JSONa z bloków ```json ... ```
match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
if match:
    json_str = match.group(1)
    mpns_dict = json.loads(json_str)
    all_mpns = []
    for v in mpns_dict.values():
        all_mpns.extend(v)
    
    with open('/home/krzysiek/.gemini/antigravity/brain/4eee6366-ec84-4b2d-ad1d-49f583597f01/scratch/ic_list_gen.json', 'w') as f:
        json.dump(all_mpns, f)
    print(f"Sukces! Wyekstrahowano {len(all_mpns)} MPNów.")
else:
    print("Nie znaleziono bloku JSON w odpowiedzi Mistrala.")
