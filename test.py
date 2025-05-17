from seleniumbase import SB
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, Future

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_proxies(file_path):
    proxies = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                    proxy = f"socks5://{proxy}"
                proxies.append(proxy)
        logger.info(f"Loaded {len(proxies)} proxies")
    except FileNotFoundError:
        logger.error(f"Proxy file not found: {file_path}")
    return proxies

def run_with_proxy(proxy, urls, port_offset):
    port = 9222 + port_offset
    try:
        logger.info(f"[{proxy}] Starting session on port {port}...")
        with SB(uc=True, test=True, locale="en", proxy=proxy, undetectable=True,
                chromium_arg=f'--remote-debugging-port={port}') as sb:
            try:
                initial_url = urls[0]
                logger.info(f"[{proxy}] Visiting {initial_url}")
                sb.activate_cdp_mode(initial_url)
                start_time = time.time()
                while time.time() - start_time < 30:
                    time.sleep(2)
                    sb.uc_gui_click_captcha()
                    title = sb.get_title()
                    logger.info(f"[{proxy}] Page title: {title}")
                    if time.time() - start_time > 10:
                        raise Exception("Proxy not stable")
                    if title and "Cikgu Mall" in title:
                        time.sleep(7)
                        logger.info(f"[{proxy}] Title matched. Moving to next URL.")
                        break
                else:
                    raise Exception("Title did not contain 'Cikgu Mall' within 30 seconds.")
                for url in urls:
                    sb.open(url)
                    sb.sleep(5)
                logger.info(f"[{proxy}] Finished cleanly.")
            except Exception as e:
                logger.error(f"[{proxy}] Error during execution: {e}")
    except Exception as e:
        logger.error(f"[{proxy}] Failed to start session: {e}")

# Load proxies
proxies = load_proxies('proxies.txt')
if not proxies:
    logger.error("No proxies available. Exiting.")
    exit()

# Target URLs
urls = [
    'https://cikgumall.com/aff/4717',
    'https://cikgumall.com/product/estana-kunafa-pistacio-bar-coklat-viral-108g-with-cooler-box/aff/B032320025',
    'https://cikgumall.com/aff/B032320066',
    'https://cikgumall.com/product/premium-lite-edition-brownies-cookies-cocoa-bakes/aff/utemB032320026',
    'https://cikgumall.com/product/ryverra-panned-chocolate-40g/aff/B032320028'
]

# Settings
TIMEOUT_PER_SESSION = 90
batch_size = 15

logger.info("=== Starting adaptive proxy loading ===")

proxy_index = 0
completed_count = 0
port_base = 0

with ThreadPoolExecutor(max_workers=batch_size) as executor:
    future_to_proxy: dict[Future, tuple[str, int]] = {}
    
    # Launch initial batch
    while proxy_index < min(batch_size, len(proxies)):
        proxy = proxies[proxy_index]
        future = executor.submit(run_with_proxy, proxy, urls, port_base + proxy_index)
        future_to_proxy[future] = (proxy, port_base + proxy_index)
        proxy_index += 1

    # As each proxy finishes, launch a new one
    while future_to_proxy:
        done_futures = []
        for future in as_completed(future_to_proxy, timeout=TIMEOUT_PER_SESSION):
            proxy, port = future_to_proxy[future]
            try:
                future.result(timeout=TIMEOUT_PER_SESSION)
                completed_count += 1
                logger.info(f"[{proxy}] Finished and counted.")
            except TimeoutError:
                logger.error(f"[{proxy}] Timed out after {TIMEOUT_PER_SESSION} seconds")
            except Exception as e:
                logger.error(f"[{proxy}] Error: {str(e)}")
            done_futures.append(future)

            # Start next proxy if available
            if proxy_index < len(proxies):
                next_proxy = proxies[proxy_index]
                next_port = port_base + proxy_index
                next_future = executor.submit(run_with_proxy, next_proxy, urls, next_port)
                future_to_proxy[next_future] = (next_proxy, next_port)
                logger.info(f"[{next_proxy}] Launched after slot freed")
                proxy_index += 1

        # Remove completed futures
        for f in done_futures:
            del future_to_proxy[f]

logger.info(f"\n=== All proxies completed: {completed_count}/{len(proxies)} successful ===")
