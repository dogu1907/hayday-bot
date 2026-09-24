import os
import json
import html
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
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            print("Supercell mağazasına bağlanılıyor...")
            page.goto("https://store.supercell.com/tr/hayday", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            
            # Çerez uyarısı varsa kapatmayı dene
            try:
                cookie_btn = page.locator("button:has-text('Kabul'), button:has-text('Accept')").first
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # Sayfayı görsellerin yüklenmesi için hafifçe kaydır
            page.evaluate("window.scrollBy(0, 400)")
            page.wait_for_timeout(2000)

            # "Ücretsiz" yazısını içeren kartı bul
            free_element = page.locator("text='Ücretsiz'").first
            if free_element.is_visible():
                card = free_element.locator("xpath=./ancestor::div[contains(@class, 'product') or contains(@class, 'card') or contains(@class, 'item') or @class][1]").first
                
                # Hediye ismini al
                card_text = card.inner_text()
                lines = [line.strip() for line in card_text.split("\n") if line.strip() and "Ücretsiz" not in line and "Al" not in line]
                if lines:
                    gift_name = lines[0]

                # Ekran görüntüsünü kart üzerinden yakala
                img_elem = card.locator("img").first
                if img_elem.is_visible():
                    img_bytes = img_elem.screenshot()
                else:
                    img_bytes = card.screenshot()
        except Exception as e:
            print(f"Playwright tarama uyarısı: {e}")
        finally:
            browser.close()
            
    return gift_name, img_bytes

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("HATA: BOT_TOKEN veya CHANNEL_ID eksik!")
        return

    now_tr = datetime.utcnow() + timedelta(hours=3)
    date_str = now_tr.strftime("%d.%m.%Y")
    
    gift_name, img_bytes = get_daily_gift()
    
    # HTML hata vermesin diye özel karakterleri temizle
    safe_gift_name = html.escape(gift_name)
    print(f"Çekilen Hediye: {gift_name}")

    caption = f"""🎁 <b>{safe_gift_name}</b>

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
    
    payload_data = {
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(reply_markup)
    }

    if img_bytes:
        print("Görsel Telegram'a dosyayla yükleniyor...")
        files = {"photo": ("gift.png", img_bytes, "image/png")}
        res = requests.post(telegram_url, data=payload_data, files=files)
    else:
        print("Görsel yakalanamadı, varsayılan görsel kullanılıyor...")
        payload_data["photo"] = "https://play-lh.googleusercontent.com/tG_A01qT3-w4_Vmsq02E40d-HnK1Hn_eTcl_mKhyLzV3q_V0m-B6fRifb5H9QZt5L6s"
        res = requests.post(telegram_url, data=payload_data)

    print(f"Telegram Yanıtı: {res.text}")

    if res.status_code != 200:
        print("Fotoğraf gönderiminde sorun oluştu, metin olarak gönderiliyor...")
        msg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        msg_payload = {
            "chat_id": CHANNEL_ID,
            "text": caption,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        }
        requests.post(msg_url, json=msg_payload)

if __name__ == "__main__":
    main()
