import os
import json
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# Kendi kanalınızın davet linkini buraya yazın
KANAL_LINKI = "https://t.me/hdtest33" 

def get_daily_gift():
    gift_name = "Ücretsiz Günlük Hediye"
    img_bytes = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://store.supercell.com/tr/hayday", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(4000)
            
            # "Ücretsiz" metninin olduğu hediye kartını bul
            free_element = page.locator("text='Ücretsiz'").first
            if free_element.is_visible():
                card = free_element.locator("xpath=./ancestor::div[contains(@class, 'product') or contains(@class, 'card') or contains(@class, 'item') or @class]").first
                
                # Hediye adını çek
                titles = card.locator("xpath=.//*[not(contains(text(), 'Ücretsiz')) and string-length(text()) > 2]").all_inner_texts()
                if titles:
                    clean_title = [t.strip() for t in titles if t.strip() and "Ücretsiz" not in t]
                    if clean_title:
                        gift_name = clean_title[0]
                
                # Resmin kendisini doğrudan sayfadan ekran görüntüsü olarak yakala
                img_elem = card.locator("img").first
                if img_elem.is_visible():
                    img_bytes = img_elem.screenshot()
        except Exception as e:
            print(f"Scraping işlemi uyarısı: {e}")
        finally:
            browser.close()
            
    return gift_name, img_bytes

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise Exception("HATA: BOT_TOKEN veya CHANNEL_ID eksik!")
        
    now_tr = datetime.utcnow() + timedelta(hours=3)
    date_str = now_tr.strftime("%d.%m.%Y")
    
    print("Siteden veriler çekiliyor...")
    gift_name, img_bytes = get_daily_gift()
    print(f"Bulunan Hediye: {gift_name}")

    caption = f"""🎁 <b>{gift_name}</b>

• 🗓 Ücretsiz Günlük Hediye!
• 👉 Mağazada "Al" butonuna bas

🔄 <i>Yenilenme: {date_str} 11:00</i>

🆓 Ücretsiz ödül yayında!"""

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🛒 Mağazada Al", "url": "https://store.supercell.com/tr/hayday"},
                {"text": "📢 Kanal", "url": KANAL_LINKI}
            ]
        ]
    }

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    data = {
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(reply_markup)
    }
    
    print("Telegram'a mesaj gönderiliyor...")
    if img_bytes:
        # Resmi doğrudan dosya yüklemesi olarak gönder
        files = {"photo": ("gift.png", img_bytes, "image/png")}
        response = requests.post(telegram_url, data=data, files=files)
    else:
        # Görsel çekilemezse varsayılan görsel ile gönder
        data["photo"] = "https://play-lh.googleusercontent.com/tG_A01qT3-w4_Vmsq02E40d-HnK1Hn_eTcl_mKhyLzV3q_V0m-B6fRifb5H9QZt5L6s"
        response = requests.post(telegram_url, data=data)
        
    print(f"Telegram Yanıtı: {response.text}")
    response.raise_for_status()

if __name__ == "__main__":
    main()
