import json
import os
import requests

# 1. Carica il database JSON
with open('contenuti.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. Trova il primo post da pubblicare
post_to_send = None
for item in data:
    if item.get('stato') == 'da_pubblicare':
        post_to_send = item
        break

if not post_to_send:
    print("Nessun nuovo post da pubblicare!")
    exit(0)

# 3. Formatta il messaggio per Telegram
messaggio = (
    f"📲 **POST PRONTO PER I SOCIAL**\n\n"
    f"📌 **Tema:** {post_to_send['tema']}\n\n"
    f"📝 **CAPTION DA COPIARE E INCOLLARE:**\n"
    f"\"{post_to_send['estratto']}\"\n\n"
    f"{post_to_send['prompt_ai']}\n\n"
    f"-------------------------------\n"
    f"🎨 **PROMPT PER CREARE L'IMMAGINE (Copia su Copilot/Bing Creator):**\n"
    f"`{post_to_send['prompt_grafico']}`"
)

# 4. Invia via Telegram
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)
    print(f"Post {post_to_send['id']} inviato a Telegram!")

# 5. Aggiorna lo stato nel JSON
post_to_send['stato'] = 'inviato'

with open('contenuti.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
