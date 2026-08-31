import json
import os
import requests

LINK_AMAZON = "https://www.amazon.it/PARTE-CHE-NON-MOSTRIAMO-sullidentit%C3%A0/dp/B0DV296L7P"

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

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 5. Invia la Copertina + Caption su Telegram
if post_to_send:
    caption_completa = (
        f"\"{post_to_send['estratto']}\"\n\n"
        f"{post_to_send['prompt_ai']}\n\n"
        f"📖 **Disponibile su Amazon in formato Cartaceo ed eBook!**\n"
        f"🛒 Acquista qui: {LINK_AMAZON}\n"
        f"📌 (Link attivo anche in Bio)"
        f"{HASHTAGS}"
    )

    messaggio_telegram = (
        f"🔥 **POST PRONTO PER I SOCIAL**\n\n"
        f"📌 **Tema:** {post_to_send['tema']}\n\n"
        f"📝 **CAPTION DA COPIARE:**\n"
        f"```text\n{caption_completa}\n```"
    )

    # Controlla se la copertina esiste nella cartella
    copertina_path = None
    for ext in ['copertina.jpg', 'copertina.jpeg', 'copertina.png']:
        if os.path.exists(ext):
            copertina_path = ext
            break

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        # Se c'è l'immagine della copertina, la invia a Telegram
        if copertina_path:
            url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            with open(copertina_path, 'rb') as photo_file:
                payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": messaggio_telegram,
                    "parse_mode": "Markdown"
                }
                requests.post(url_photo, data=payload, files={"photo": photo_file})
        else:
            url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": messaggio_telegram,
                "parse_mode": "Markdown"
            }
            requests.post(url_msg, json=payload)

    post_to_send['stato'] = 'inviato'

# 6. Invia eventuale Outreach Influencer
if influencer_to_contact:
    msg_influencer = (
        f"🤝 **OUTREACH BOOK INFLUENCER ({influencer_to_contact['piattaforma']}):**\n"
        f"👤 Profilo: {influencer_to_contact['nome_profilo']}\n\n"
        f"```text\n"
        f"Ciao! Seguo con grande piacere i tuoi consigli di lettura. 📚\n"
        f"Ho pubblicato da poco il romanzo 'LA PARTE CHE NON MOSTRIAMO' di Francesco Sergi.\n"
        f"Mi farebbe davvero piacere inviarti una copia digitale gratuita (ePUB/Kindle) in anteprima!\n"
        f"Trovi il libro anche su Amazon: {LINK_AMAZON}\n"
        f"Fammi sapere se ti fa piacere leggere l'eBook! ✨\n"
        f"```"
    )
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg_influencer,
            "parse_mode": "Markdown"
        }
        requests.post(url_msg, json=payload)

    influencer_to_contact['stato'] = 'contattato'

# 7. Salva aggiornamenti nel JSON
if post_to_send:
    with open('contenuti.json', 'w', encoding='utf-8') as f:
        json.dump(contenuti, f, indent=2, ensure_ascii=False)

if influencer_to_contact:
    with open('influencer.json', 'w', encoding='utf-8') as f:
        json.dump(influencer_list, f, indent=2, ensure_ascii=False)
