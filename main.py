import os
import json
import html
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# Eğer Secret ile çalışmadıysa, kopyaladığınız çerezi buradaki tırnakların arasına yapıştırabilirsiniz:
SUPERCELL_COOKIES = os.environ.get("[{"name":"OptanonConsent","value":"isGpcEnabled=0&datestamp=Thu+Sep+24+2026+17%3A00%3A56+GMT%2B0300+(T%C3%BCrkiye+Standart+Saati)&version=202401.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&genVendors=V5%3A0%2CV4%3A0%2CV1%3A0%2CV6%3A0%2CV2%3A0%2CV3%3A0%2CV7%3A0%2C&consentId=db37af2c-58ab-4933-8161-1d4d93fe3d0c&interactionCount=1&landingPath=NotLandingPage&groups=C0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=TR%3B33&AwaitingReconsent=false","domain":".supercell.com","path":"/"},{"name":"NEXT_LOCALE","value":"tr","domain":".supercell.com","path":"/"},{"name":"_twpid","value":"tw.1790257924522.226167235157086065","domain":".supercell.com","path":"/"},{"name":"_twsid","value":"1790257924523-363991534.1.1790257993013","domain":".supercell.com","path":"/"},{"name":"ttcsid","value":"1790257924836::hwmt39GFo4P8gyED9rG1.1.1790257935668.0::1.-6366.0::0.0.0.0::3041.10.0","domain":".supercell.com","path":"/"},{"name":"ttcsid_D48QDBJC77U6M9K6QO00","value":"1790257924835::_45aVMVsQpd3OInIsA3R.1.1790257935680.1","domain":".supercell.com","path":"/"},{"name":"_sp_id.fbf6","value":"976b16fa-6dc8-4137-854d-1e8f793881ea.1790257886.1.1790257928..2be137cc-dd32-4583-becc-0f40de5871aa..bb6cef51-cdd8-46b7-bde3-ecffeea7349b.1790257886169.20","domain":".supercell.com","path":"/"},{"name":"_sp_ses.fbf6","value":"*","domain":".supercell.com","path":"/"},{"name":"_fbp","value":"fb.1.1790257924782.779728495771414952","domain":".supercell.com","path":"/"},{"name":"_ga","value":"GA1.1.1330084669.1790257925","domain":".supercell.com","path":"/"},{"name":"_ga_Q1VRW6YH7K","value":"GS2.1.s1790257924$o1$g0$t1790257924$j60$l0$h1944718567","domain":".supercell.com","path":"/"},{"name":"_scid","value":"LNjbVsnFkL-HgKlTB6pIKTbtl-6ps-zR","domain":".supercell.com","path":"/"},{"name":"_scid_r","value":"LNjbVsnFkL-HgKlTB6pIKTbtl-6ps-zR","domain":".supercell.com","path":"/"},{"name":"_tt_enable_cookie","value":"1","domain":".supercell.com","path":"/"},{"name":"_ttp","value":"01M39V02Q26DEJEWP2HD5XCYKA_.tt.1.1790257924834","domain":".supercell.com","path":"/"},{"name":"_gcl_au","value":"1.1.1317782378.1790257923","domain":".supercell.com","path":"/"},{"name":"scsso_scid","value":"34-bce10729-58af-4aae-8602-e8a2263cc56c","domain":".supercell.com","path":"/"},{"name":"OptanonAlertBoxClosed","value":"2026-09-24T13:51:26.151Z","domain":".supercell.com","path":"/"}] d8nr2j39xng9h8ppm9z4p7chm "") 

KANAL_LINKI = "https://t.me/hdtest33" 

def get_daily_gift():
    gift_name = "Ücretsiz Günlük Hediye"
    img_bytes = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            locale="tr-TR"
        )
        
        # Çerezleri yükleme
        cookies_to_use = SUPERCELL_COOKIES
        if cookies_to_use:
            try:
                if isinstance(cookies_to_use, str):
                    cookies = json.loads(cookies_to_use)
                else:
                    cookies = cookies_to_use
                    
                for cookie in cookies:
                    if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie["sameSite"] = "Lax"
                context.add_cookies(cookies)
                print("Supercell ID çerezleri başarıyla yüklendi!")
            except Exception as e:
                print(f"Çerez yükleme hatası: {e}")

        page = context.new_page()
        try:
            print("Supercell mağazasına bağlanılıyor...")
            page.goto("https://store.supercell.com/tr/hayday", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(6000) # Oturumun tam oturması için bekleme süresi
            
            # Çerez onay penceresini kapat
            try:
                cookie_btn = page.locator("button:has-text('Kabul'), button:has-text('Accept'), #onetrust-accept-btn-handler").first
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # Sayfada oturum açıldıysa görünen hediye kartını veya butonunu ara
            # Giriş yapıldığında "Al" veya "Claim" butonu görünür
            claim_btn = page.locator("button:has-text('Al'), button:has-text('Claim')").first
            
            if claim_btn.is_visible():
                print("Giriş yapılmış durumda hediye/buton bulundu!")
                card = claim_btn.locator("xpath=./ancestor::div[contains(@class, 'card') or contains(@class, 'offer') or contains(@class, 'Product') or @class][2]").first
                card.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)

                # Hediye adını çek
                card_text = card.inner_text()
                lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                ignore_list = ["ücretsiz", "günlük", "hediye", "bekliyor", "sa", "dk", "bonus", "alınmayı", "al"]
                for line in lines:
                    if not any(kw in line.lower() for kw in ignore_list) and len(line) > 1:
                        gift_name = line
                        break

                img_bytes = card.screenshot()
                print(f"Hediyenin resmi başarıyla alındı! Hediye: {gift_name}")
                
                # Hediyeyi otomatik hesaba al
                try:
                    claim_btn.click()
                    print("Hediyeyi alma butonuna tıklandı!")
                except Exception:
                    pass
            else:
                print("Giriş butonu bulunamadı, ekranın üst kısmı alınıyor...")
                img_bytes = page.screenshot(clip={"x": 0, "y": 0, "width": 390, "height": 650})

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
