import json
import os
import requests

LINK_AMAZON_DEFAULT = "https://www.amazon.it/s?k=LA+PARTE+CHE+NON+MOSTRIAMO+Francesco+Sergi"

# 1. Carica il database dei contenuti post
with open('contenuti.json', 'r', encoding='utf-8') as f:
    contenuti = json.load(f)

# 2. Carica il database degli influencer
influencer_list = []
if os.path.exists('influencer.json'):
    with open('influencer.json', 'r', encoding='utf-8') as f:
        influencer_list = json.load(f)

# 3. Trova il primo post da pubblicare
post_to_send = None
for item in contenuti:
    if item.get('stato') == 'da_pubblicare':
        post_to_send = item
        break

# 4. Trova il primo influencer da contattare
influencer_to_contact = None
for inf in influencer_list:
    if inf.get('stato') == 'da_contattare':
        influencer_to_contact = inf
        break

if not post_to_send and not influencer_to_contact:
    print("Nessun contenuto o contatto da elaborare!")
    exit(0)

# 5. Costruisci il messaggio per Telegram
messaggio = "📢 **AGGIORNAMENTO PROMOZIONE LIBRO**\n\n"

if post_to_send:
    link_amz = post_to_send.get('link_amazon', LINK_AMAZON_DEFAULT)
    messaggio += (
        f"📲 **POST SOCIAL PRONTO**\n"
        f"📌 **Tema:** {post_to_send['tema']}\n\n"
        f"📝 **CAPTION DA COPIARE:**\n"
        f"\"{post_to_send['estratto']}\"\n\n"
        f"{post_to_send['prompt_ai']}\n\n"
        f"🛒 **Link Amazon:**\n{link_amz}\n\n"
        f"🎨 **PROMPT IMMAGINE (Copilot/Bing Creator):**\n"
        f"`{post_to_send['prompt_grafico']}`\n"
        f"-----------------------------------------\n\n"
    )
    post_to_send['stato'] = 'inviato'

if influencer_to_contact:
    link_amz = post_to_send.get('link_amazon', LINK_AMAZON_DEFAULT) if post_to_send else LINK_AMAZON_DEFAULT
    messaggio += (
        f"🤝 **OUTREACH BOOK INFLUENCER DEL GIORNO**\n"
        f"👤 **Profilo:** {influencer_to_contact['nome_profilo']} ({influencer_to_contact['piattaforma']})\n\n"
        f"💬 **MESSAGGIO DM DA COPIARE E INVIARE:**\n"
        f"\"Ciao! Seguo la tua pagina e amo i tuoi consigli di lettura. 📚\n"
        f"Ho pubblicato da poco il mio romanzo 'LA PARTE CHE NON MOSTRIAMO: Un romanzo corale sull'identità e sul destino' di Francesco Sergi.\n"
        f"Mi farebbe davvero piacere inviarti una copia digitale gratuita (ePUB/Kindle) senza alcun impegno!\n"
        f"Se ti va di darci un'occhiata, lo trovi anche qui su Amazon: {link_amz}\n"
        f"Fammi sapere se ti fa piacere ricevere il file! ✨\""
    )
    influencer_to_contact['stato'] = 'contattato'

# 6. Invia la notifica via Telegram
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
    print("Notifica inviata a Telegram con successo!")

# 7. Salva i file aggiornati
if post_to_send:
    with open('contenuti.json', 'w', encoding='utf-8') as f:
        json.dump(contenuti, f, indent=2, ensure_ascii=False)

if influencer_to_contact:
    with open('influencer.json', 'w', encoding='utf-8') as f:
        json.dump(influencer_list, f, indent=2, ensure_ascii=False)
