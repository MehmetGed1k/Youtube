import os
import random
import asyncio
from playwright.async_api import async_playwright
import socks
import socket

# Proxy ve site dosyalarının dizin yolları
OUTPUT_DIR = r"C:\\Users\\alone\\Desktop\\proxler"
sites_file = os.path.join(OUTPUT_DIR, "youtubelinkleri.txt")
proxies_file = os.path.join(OUTPUT_DIR, "sockproxy.txt")

# Proxy kullanıcı adı ve şifre
PROXY_USERNAME = "USFXUJ6OI"
PROXY_PASSWORD = "PF132wz6"

# User-Agent listesi
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Dosyadan veri okuma fonksiyonu
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

# Web sitesine bağlanmayı deneyin
async def visit_site_with_proxy(page, site, proxy_ip, proxy_port):
    try:
        # SOCKS5 proxy ayarı
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port), True, PROXY_USERNAME, PROXY_PASSWORD)
        socket.socket = socks.socksocket

        # Youtube Aç
        print(f"🔗 Siteye bağlanılıyor: {site} (Proxy: {proxy_ip}:{proxy_port})")
        await page.goto(site, timeout=60000)
        await page.wait_for_load_state("load")
        print(f"✅ {site} ziyaret edildi. 10 saniye bekleniyor...")

        # **10 saniye bekle**
        await asyncio.sleep(10)

        return True
    except Exception as e:
        print(f"❌ Proxy {proxy_ip}:{proxy_port} ile bağlantı hatası: {e}")
        return False


# Proxy ve site gezintisi
async def visit_sites_with_proxies():
    proxies = read_file(proxies_file)
    sites = read_file(sites_file)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])

        for proxy in proxies:
            proxy_ip, proxy_port = proxy.split(":")
            print(f"\n🔄 Yeni proxy kullanılıyor: {proxy}")

            # Yeni tarayıcı context'i oluştur
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)},
                locale='en-US'
            )
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Yeni bir sayfa aç
            page = await context.new_page()

            # Tüm siteleri ziyaret et
            for site in sites:
                site_visited = await visit_site_with_proxy(page, site, proxy_ip, proxy_port)
                if not site_visited:
                    print(f"🔄 Proxy değiştirilerek bir sonraki proxy'ye geçiliyor...")
                    break  # Bağlantı hatası olursa sonraki proxy'ye geç

            # Sayfayı kapat
            await page.close()

        # Tarayıcıyı kapat
        await browser.close()

# Ana fonksiyonu çalıştır
asyncio.run(visit_sites_with_proxies())
