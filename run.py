
#!/usr/bin/env python3
import os
import time
import threading
import random
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from seleniumbase import SB
import time
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cikgumall_access.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "PROXIES_FILE": "proxies.txt",
    "BATCH_SIZE": 10,            # Reduced from 10 to 5
    "MAX_RETRIES": 3,
    "DELAY_BETWEEN_BATCHES": 1, # Increased from 5 to 10
    "HEADLESS": False,
    "URL_LIST": [
        'https://cikgumall.com/aff/4717',
        'https://cikgumall.com/product/estana-kunafa-pistacio-bar-coklat-viral-108g-with-cooler-box/aff/B032320025',
        'https://cikgumall.com/aff/B032320066',
        'https://cikgumall.com/product/premium-lite-edition-brownies-cookies-cocoa-bakes/aff/utemB032320026',
        'https://cikgumall.com/product/ryverra-panned-chocolate-40g/aff/B032320028'

    ]
}

# Dictionary to track proxy success rates
proxy_stats = {}
proxy_lock = threading.Lock()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Access CikguMall URLs using proxies")
    parser.add_argument("--proxies", type=str, default=DEFAULT_CONFIG["PROXIES_FILE"], help="File containing proxies")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_CONFIG["BATCH_SIZE"], help="Number of proxies per batch")
    parser.add_argument("--retries", type=int, default=DEFAULT_CONFIG["MAX_RETRIES"], help="Maximum retry attempts for each proxy")
    parser.add_argument("--delay", type=int, default=DEFAULT_CONFIG["DELAY_BETWEEN_BATCHES"], help="Delay between batches in seconds")
    parser.add_argument("--headless", action="store_true", default=DEFAULT_CONFIG["HEADLESS"], help="Run in headless mode")
    parser.add_argument("--urls", type=str, help="Comma-separated list of URLs to access")
    return parser.parse_args()

def load_proxies(file_path):
    """Load proxies from a text file into a list."""
    proxies = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    # Ensure scheme
                    if not proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                        proxy = f"socks5://{proxy}"
                    proxies.append(proxy)
        logger.info(f"Loaded {len(proxies)} proxies from {file_path}")
    except FileNotFoundError:
        logger.error(f"Proxy file not found: {file_path}")
    return proxies

def chunk_list(lst, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def update_proxy_stats(proxy, success):
    with proxy_lock:
        if proxy not in proxy_stats:
            proxy_stats[proxy] = {"attempts": 0, "successes": 0}
        proxy_stats[proxy]["attempts"] += 1
        if success:
            proxy_stats[proxy]["successes"] += 1

def get_random_user_agent():
    """Return a random user agent string"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)

def get_random_viewport():
    """Return random viewport dimensions"""
    viewports = [
        (1366, 768),
        (1920, 1080),
        (1536, 864),
        (1440, 900),
        (1280, 720)
    ]
    return random.choice(viewports)

def randomize_user_behavior(sb):
    """Perform random user-like behavior"""
    try:
        # Random scrolling
        scroll_amount = random.randint(300, 800)
        sb.execute_script(f"window.scrollBy(0, {scroll_amount});")
        sb.sleep(random.uniform(0.5, 1.5))
        
        # Maybe scroll back up a bit
        if random.random() > 0.7:
            scroll_back = random.randint(100, 300)
            sb.execute_script(f"window.scrollBy(0, -{scroll_back});")
            sb.sleep(random.uniform(0.3, 0.7))
        
        # Random mouse movements (simulate with JavaScript)
        try:
            sb.execute_script("""
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': arguments[0],
                    'clientY': arguments[1]
                });
                document.dispatchEvent(event);
            """, random.randint(100, 800), random.randint(100, 600))
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed (non-critical): {str(e)}")
    except Exception as e:
        logger.warning(f"Error during user behavior simulation: {str(e)}")
        # Continue execution even if behavior simulation fails

def bypass_turnstile(sb, max_attempts=3, wait_between=10):
    """
    Attempt to bypass Cloudflare Turnstile using SeleniumBase's uc_gui_click_captcha().
    Retries clicking the captcha up to max_attempts times.
    """
    # First check if Turnstile is present - without timeout parameter
    try:
        if not sb.is_element_visible('iframe[src*="turnstile"]'):
            logger.info("No Turnstile detected, continuing...")
            return True
            
        logger.info("Turnstile detected, attempting bypass...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Activate Chrome DevTools mode on the current page
                sb.activate_cdp_mode(sb.get_current_url())
                # Use SeleniumBase helper to click the Turnstile checkbox
                sb.uc_gui_click_captcha()
                sb.sleep(wait_between)
                
                # Verify if the Turnstile iframe is gone - without timeout parameter
                if not sb.is_element_visible('iframe[src*="turnstile"]'):
                    logger.info(f"Turnstile passed on attempt {attempt}.")
                    return True
                else:
                    logger.warning(f"Turnstile still present after attempt {attempt}")
            except Exception as e:
                logger.warning(f"Turnstile attempt {attempt} failed: {str(e)}")
                
            if attempt < max_attempts:
                # Add some randomness to wait time
                wait_time = wait_between + random.uniform(0.5, 2.0)
                sb.sleep(wait_time)
        
        logger.error("All Turnstile bypass attempts failed.")
        return False
    except Exception as e:
        logger.warning(f"Error in Turnstile bypass routine: {str(e)}")
        # If any error occurs in the Turnstile detection, we continue anyway
        return True

def worker(proxy_url, urls, headless, retry_count=DEFAULT_CONFIG["MAX_RETRIES"]):
    """Use a single SeleniumBase session per proxy to fetch all URLs and bypass Turnstile."""
    success = False

    try:
        viewport_width, viewport_height = get_random_viewport()

        # Configure SeleniumBase
        sb_options = {
            "uc": True,              # Undetected Chrome
            "test": False,           # Not a test run
            "locale": "en",          # English locale
            "headless": headless,    # Headless mode if specified
        }

        if proxy_url:
            sb_options["proxy"] = proxy_url

        with SB(**sb_options) as sb:
            try:
                sb.set_window_size(viewport_width, viewport_height)

                for idx, url in enumerate(urls):
                    url_success = False
                    for attempt in range(retry_count):
                        try:
                            logger.info(f"[Proxy {proxy_url}] Accessing {url} (attempt {attempt+1}/{retry_count})")
                            sb.open(url)
                            sb.sleep(random.uniform(10, 24.0))

                            current_url = sb.get_current_url()
                            if "cloudflare" in current_url.lower() or "challenge" in current_url.lower():
                                logger.warning(f"[Proxy {proxy_url}] Detected Cloudflare challenge page")
                            randomize_user_behavior(sb)
                            bypass_result = bypass_turnstile(sb, retry_count)

                            try:
                                if(bypass_result):
                                    title = sb.get_title()
                                    logger.info(f"[Proxy {proxy_url}] Success: Title='{title}' for URL {url}")
                                    url_success = True
                                    success = True
                                    break
                                else:
                                    logger.warning(f"[Proxy {proxy_url}] failed")
                            except Exception as e:
                                logger.warning(f"[Proxy {proxy_url}] Could not get page title: {str(e)}")

                        except Exception as url_error:
                            remaining = retry_count - attempt - 1
                            logger.error(f"[Proxy {proxy_url}] Error accessing {url}: {str(url_error)}")
                            if remaining > 0:
                                logger.info(f"[Proxy {proxy_url}] Will retry {remaining} more times")
                                time.sleep(random.uniform(1.0, 3.0))
                            else:
                                logger.error(f"[Proxy {proxy_url}] Failed all {retry_count} attempts for {url}")
                                break

                    if not url_success:
                        logger.error(f"[Proxy {proxy_url}] Failed to access {url} after all attempts")
                        if idx == 0:
                            logger.warning(f"[Proxy {proxy_url}] First URL failed. Skipping the rest.")
                            break

            except Exception as window_error:
                logger.error(f"[Proxy {proxy_url}] Window setup error: {str(window_error)}")

    except Exception as session_error:
        logger.error(f"[Proxy {proxy_url}] Session initialization failed: {str(session_error)}")

    # Update proxy statistics
    update_proxy_stats(proxy_url, success)
    return success


def run_batch(batch, urls, headless, max_retries):
    """Run a batch of proxies using ThreadPoolExecutor for better thread management."""
    max_workers = min(len(batch), 5)  # Limit the number of concurrent workers
    logger.info(f"Running batch with {max_workers} concurrent workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the executor
        future_to_proxy = {
            executor.submit(worker, proxy, urls, headless, max_retries): proxy 
            for proxy in batch
        }
        
        # Collect results
        results = []
        for future in future_to_proxy:
            proxy = future_to_proxy[future]
            try:
                success = future.result()
                results.append((proxy, success))
            except Exception as e:
                logger.error(f"Exception for proxy {proxy}: {str(e)}")
                results.append((proxy, False))
        
        return results

def print_stats():
    """Print statistics about proxy performance."""
    logger.info("\n--- Proxy Statistics ---")
    
    if not proxy_stats:
        logger.info("No statistics available.")
        return
        
    # Calculate success rates
    for proxy, stats in proxy_stats.items():
        attempts = stats["attempts"]
        successes = stats["successes"]
        rate = (successes / attempts * 100) if attempts > 0 else 0
        logger.info(f"Proxy {proxy}: {successes}/{attempts} successful ({rate:.1f}%)")
    
    # Overall statistics
    total_attempts = sum(stats["attempts"] for stats in proxy_stats.values())
    total_successes = sum(stats["successes"] for stats in proxy_stats.values())
    overall_rate = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
    logger.info(f"\nOverall success rate: {total_successes}/{total_attempts} ({overall_rate:.1f}%)")

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Process URL list
    url_list = DEFAULT_CONFIG["URL_LIST"]
    if args.urls:
        url_list = [url.strip() for url in args.urls.split(",")]
    
    # Load proxies
    proxies = load_proxies(args.proxies)
    if not proxies:
        logger.error("No proxies available. Exiting.")
        return 1
    
    # Split into batches
    batches = list(chunk_list(proxies, args.batch_size))
    total_batches = len(batches)
    logger.info(f"Processing {len(proxies)} proxies in {total_batches} batches")
    
  
        # Process each batch
    for idx, batch in enumerate(batches, start=1):
        logger.info(f"\n=== BATCH {idx}/{total_batches} ===")
        results = run_batch(batch, url_list, args.headless, args.retries)
        
        # Log batch results
        successes = sum(1 for _, success in results if success)
        logger.info(f"Batch {idx} completed: {successes}/{len(batch)} successful")
        
        # Wait between batches (if not the last batch)
        if idx < total_batches:
            # Randomize delay slightly
            delay = args.delay + random.uniform(-0.5, 1.0)
            logger.info(f"Waiting {delay:.1f}s before next batch...")
            time.sleep(delay)
    
    # Print final statistics
    print_stats()
        

        
    return 0

if __name__ == '__main__':
    exit(main())
