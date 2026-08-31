import json
import os
import requests
from openai import OpenAI

# 1. Inizializza i client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.environ.get("BUFFER_PROFILE_ID")

# 2. Leggi il database JSON
with open('contenuti.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 3. Seleziona il primo post da pubblicare
post_data = None
for item in data:
    if item.get('stato') == 'da_pubblicare':
        post_data = item
        break

if not post_data:
    print("Nessun post da pubblicare.")
    exit(0)

# 4. Genera il testo completo (Caption + Hashtag) via GPT-4o
gpt_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Sei un social media manager esperto per romanzi."},
        {"role": "user", "content": f"{post_data['prompt_ai']}. Estratto: '{post_data['estratto']}'."}
    ]
)
caption_finale = gpt_response.choices[0].message.content

# 5. Genera la grafica via DALL-E 3
dalle_response = client.images.generate(
    model="dall-e-3",
    prompt=f"A cinematic book promo image: {post_data['prompt_grafico']}. Overlay text: '{post_data['estratto']}'",
    size="1024x1024",
    quality="standard",
    n=1,
)
image_url = dalle_response.data[0].url

# 6. Pubblica automaticamente sui social via Buffer API
buffer_url = "https://api.bufferapp.com/1/updates/create.json"
payload = {
    'access_token': BUFFER_ACCESS_TOKEN,
    'profile_ids[]': BUFFER_PROFILE_ID,
    'text': caption_finale,
    'media[picture]': image_url,
    'now': 'true'
}

response = requests.post(buffer_url, data=payload)

if response.status_code == 200:
    print(f"Post {post_data['id']} pubblicato in automatico!")
    post_data['stato'] = 'inviato'
    with open('contenuti.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
else:
    print("Errore pubblicazione:", response.text)
