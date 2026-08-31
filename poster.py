import json
import os
import requests

LINK_AMAZON = "https://www.amazon.it/PARTE-CHE-NON-MOSTRIAMO-sullidentit%C3%A0/dp/B0DV296L7P"

# Hashtag ad alta conversione per nicchia libri / BookTok / BookStagram
HASHTAGS = (
    "\n\n.#LaParteCheNonMostriamo #FrancescoSergi #BookStagramItalia "
    "#BookTokItalia #ConsigliDiLettura #RomanzoPsicologico #LettureConsigliate "
    "#LibriDaLeggere #AmazonKDP #NarrativaContemporanea"
)

# 1. Carica i dati dei post
with open('contenuti.json', 'r', encoding='utf-8') as f:
    contenuti = json.load(f)

# 2. Carica i contatti influencer
influencer_list = []
if os.path.exists('influencer.json'):
    with open('influencer.json', 'r', encoding='utf-8') as f:
        influencer_list = json.load(f)

# 3. Seleziona il post corrente
post_to_send = None
for item in contenuti:
    if item.get('stato') == 'da_pubblicare':
        post_to_send = item
        break

# 4. Seleziona l'influencer corrente
influencer_to_contact = None
for inf in influencer_list:
    if inf.get('stato') == 'da_contattare':
        influencer_to_contact = inf
        break

if not post_to_send and not influencer_to_contact:
    print("Nessun contenuto da elaborare!")
    exit(0)

messaggio = "🔥 **PROMOZIONE AD ALTA CONVERSIONE - LA PARTE CHE NON MOSTRIAMO**\n\n"

if post_to_send:
    caption_vendita = (
        f"\"{post_to_send['estratto']}\"\n\n"
        f"{post_to_send['prompt_ai']}\n\n"
        f"📖 **Disponibile ora su Amazon in versione Cartacea ed eBook!**\n"
        f"🛒 Acquista la tua copia qui: {LINK_AMAZON}\n"
        f"📌 (Oppure clicca sul link in Bio per accedere subito al libro)"
        f"{HASHTAGS}"
    )
    
    messaggio += (
        f"📲 **CAPTION INSTAGRAM / TIKTOK PRONTA DA PUBBLICARE:**\n"
        f"```text\n{caption_vendita}\n```\n\n"
        f"🎨 **PROMPT IMMAGINE/GRAFICA (Copilot / Bing Creator):**\n"
        f"`{post_to_send['prompt_grafico']}`\n"
        f"-----------------------------------------\n\n"
    )
    post_to_send['stato'] = 'inviato'

if influencer_to_contact:
    messaggio += (
        f"🤝 **DM BOOK INFLUENCER ({influencer_to_contact['piattaforma']}):**\n"
        f"👤 Profilo: {influencer_to_contact['nome_profilo']}\n"
        f"```text\n"
        f"Ciao! Seguo con grande piacere i tuoi consigli di lettura. 📚\n"
        f"Ho pubblicato da poco il romanzo 'LA PARTE CHE NON MOSTRIAMO' di Francesco Sergi.\n"
        f"Mi farebbe davvero piacere inviarti una copia digitale gratuita (ePUB/Kindle) in anteprima!\n"
        f"Trovi il libro anche su Amazon: {LINK_AMAZON}\n"
        f"Dimmi pure se ti fa piacere leggere l'eBook! ✨\n"
        f"```"
    )
    influencer_to_contact['stato'] = 'contattato'

# 5. Invio Telegram
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
    print("Notifica inviata con successo!")

# 6. Salva aggiornamenti
if post_to_send:
    with open('contenuti.json', 'w', encoding='utf-8') as f:
        json.dump(contenuti, f, indent=2, ensure_ascii=False)

if influencer_to_contact:
    with open('influencer.json', 'w', encoding='utf-8') as f:
        json.dump(influencer_list, f, indent=2, ensure_ascii=False)
