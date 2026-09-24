import os
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# Kendi kanalınızın davet linkini buraya yazın
KANAL_LINKI = "https://t.me/hdtest33" 

def get_daily_gift():
    gift_name = "Sürpriz Hediye"
    img_url = "https://play-lh.googleusercontent.com/tG_A01qT3-w4_Vmsq02E40d-HnK1Hn_eTcl_mKhyLzV3q_V0m-B6fRifb5H9QZt5L6s"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://store.supercell.com/tr/hayday", timeout=45000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            
            free_elements = page.locator("text='Ücretsiz'")
            
            if free_elements.count() > 0:
                free_element = free_elements.first
                card = free_element.locator("xpath=./ancestor::div[contains(@class, 'product') or contains(@class, 'card') or contains(@class, 'item') or @class]").first
                
                img_locator = card.locator("img").first
                if img_locator.is_visible():
                    img_src = img_locator.get_attribute("src")
                    if img_src:
                        if img_src.startswith("/"):
                            img_url = "https://store.supercell.com" + img_src
                        else:
                            img_url = img_src
                
                title_locator = card.locator("xpath=.//*[not(contains(text(), 'Ücretsiz')) and string-length(text()) > 2]").first
                if title_locator.is_visible():
                    scraped_title = title_locator.inner_text().strip()
                    if scraped_title:
                        gift_name = scraped_title
                        
        except Exception as e:
            print(f"Veri çekme hatası: {e}")
        finally:
            browser.close()
            
    return gift_name, img_url

def main():
    now_tr = datetime.utcnow() + timedelta(hours=3)
    date_str = now_tr.strftime("%d.%m.%Y")
    
    print("Siteden veriler çekiliyor...")
    gift_name, img_url = get_daily_gift()

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
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": img_url,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    
    print("Mesaj gönderiliyor...")
    response = requests.post(telegram_url, json=payload)
    
    if response.status_code == 200:
        print("Başarılı! Mesaj ve görsel Telegram'a gönderildi.")
    else:
        print(f"Hata: {response.text}")

if __name__ == "__main__":
    main()
