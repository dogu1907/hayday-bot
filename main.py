import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUPERCELL_URL = "https://store.supercell.com/tr/hayday"

def send_telegram_message(text):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("HATA: BOT_TOKEN veya CHANNEL_ID tanımlanmamış!")
        return

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    response = requests.post(api_url, data=payload)
    if response.status_code == 200:
        print("Mesaj kanala başarıyla gönderildi!")
    else:
        print(f"Telegram Hatası: {response.text}")

def main():
    print("Supercell Mağazası kontrol ediliyor...")
    gift_info = f"🎁 **Günün Hay Day Ücretsiz Hediyesi!**\n\nHediyenizi almak için hemen mağazayı ziyaret edin:\n{SUPERCELL_URL}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(SUPERCELL_URL, wait_until="networkidle")
            page.wait_for_timeout(5000)

            free_element = page.query_selector("text=Ücretsiz") or page.query_selector("text=Free")
            if free_element:
                print("Ücretsiz hediye mağazada bulundu!")
            else:
                print("Spesifik etiket bulunamadı, genel bildirim gönderiliyor.")

            browser.close()
    except Exception as e:
        print(f"Tarayıcı hatası oluştu: {e}")

    send_telegram_message(gift_info)

if __name__ == "__main__":
    main()
