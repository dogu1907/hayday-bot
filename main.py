import os
import json
import html
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

KANAL_LINKI = "https://t.me/hdtest33" 

def get_daily_gift():
    gift_name = "Ücretsiz Günlük Hediye"
    img_bytes = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # iPhone görünümü ile en üstteki alan doğrudan taranır
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            locale="tr-TR"
        )

        page = context.new_page()
        try:
            print("Supercell mağazasına bağlanılıyor...")
            page.goto("https://store.supercell.com/tr/hayday", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            
            # Çerez onay penceresini kapat
            try:
                cookie_btn = page.locator("button:has-text('Kabul'), button:has-text('Accept'), #onetrust-accept-btn-handler").first
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # "ÜCRET SİZ GÜNLÜK HEDİYE" başlığını bul
            free_header = page.locator("text=/ÜCRET SİZ GÜNLÜK HEDİYE|Ücretsiz Günlük Hediye/i").first
            
            if free_header.is_visible():
                print("En üstteki ücretsiz hediye alanı bulundu!")
                # Başlığın ait olduğu ana kart kutusunu seç
                card = free_header.locator("xpath=./ancestor::div[contains(@class, 'card') or contains(@class, 'offer') or contains(@class, 'Product') or @class][2]").first
                card.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)

                # O anki güncel hediye adını metinden filtrele
                card_text = card.inner_text()
                lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                
                ignore_list = ["ücretsiz", "günlük", "hediye", "bekliyor", "sa", "dk", "bonus", "alınmayı"]
                for line in lines:
                    if not any(kw in line.lower() for kw in ignore_list) and len(line) > 1:
                        gift_name = line
                        break

                # O günkü hediyenin anlık fotoğrafını al
                img_bytes = card.screenshot()
                print(f"Görsel başarıyla çekildi! O günkü hediye: {gift_name}")
            else:
                print("Başlık bulunamadı, üst bölgenin genel ekran görüntüsü alınıyor...")
                img_bytes = page.screenshot(clip={"x": 0, "y": 100, "width": 390, "height": 500})

        except Exception as e:
            print(f"Hata oluştu: {e}")
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
        print("HATA: Görsel oluşturulamadı!")

if __name__ == "__main__":
    main()
