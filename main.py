import os
import json
import html
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# Kendi kanalınızın davet linkini yazın
KANAL_LINKI = "https://t.me/hdtest33" 

def get_daily_gift():
    gift_name = "Ücretsiz Günlük Hediye"
    img_bytes = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobil görünüm taklidi yaparak hediyeyi daha kolay yakalıyoruz
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 430, "height": 932},
            locale="tr-TR"
        )
        page = context.new_page()
        try:
            print("Supercell mağazasına bağlanılıyor...")
            page.goto("https://store.supercell.com/tr/hayday", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            
            # Çerez penceresini kapat
            try:
                cookie_btn = page.locator("button:has-text('Kabul'), button:has-text('Accept'), #onetrust-accept-btn-handler").first
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # Sayfayı kaydır ki görseller yüklensin
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(2000)

            # "Ücretsiz" yazısının olduğu hediye kartını ara
            free_btn = page.locator("text='Ücretsiz'").first
            if not free_btn.is_visible():
                free_btn = page.locator("text='ÜCRETSIZ'").first

            if free_btn.is_visible():
                # Kartı bul ve odaklan
                card = free_btn.locator("xpath=./ancestor::div[contains(@class, 'product') or contains(@class, 'card') or contains(@class, 'Item') or contains(@class, 'Offer') or @class][1]").first
                card.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)

                # Hediye ismini al
                card_text = card.inner_text()
                lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                clean_lines = [l for l in lines if not any(kw in l.lower() for kw in ["ücretsiz", "al", "mağaza", "store", "0 tl", "claim"])]
                if clean_lines:
                    gift_name = clean_lines[0]

                # Doğrudan hediye kartının resmini/görüntüsünü al
                img_bytes = card.screenshot()
                print("Hediye kartının görüntüsü başarıyla alındı!")
            else:
                print("Ücretsiz etiketi bulunamadı, genel sayfa görüntüsü alınıyor...")
                img_bytes = page.screenshot()

        except Exception as e:
            print(f"Hata oluştu: {e}")
            try:
                img_bytes = page.screenshot()
            except Exception:
                pass
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
    safe_gift_name = html.escape(gift_name)
    print(f"Çekilen Hediye Adı: {gift_name}")

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
        files = {"photo": ("gift.png", img_bytes, "image/png")}
        res = requests.post(telegram_url, data=payload_data, files=files)
        print(f"Telegram Yanıtı: {res.text}")
    else:
        print("Görsel oluşturulamadı!")

if __name__ == "__main__":
    main()
