from seleniumbase import SB
import logging
import time
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, Future
from concurrent.futures import wait, FIRST_COMPLETED
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_proxies(file_path):
    proxies = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                # if proxy and not proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                #     proxy = f"socks5://{proxy}"
                #     # proxy2 = f"http://{proxy}"
                #     # proxies.append(proxy2)
                
                proxies.append(proxy)
        logger.info(f"Loaded {len(proxies)} proxies")
    except FileNotFoundError:
        logger.error(f"Proxy file not found: {file_path}")

    return proxies

def load_urls(file_path):
    urls = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
               
                urls.append(url)
       
    except FileNotFoundError:
        logger.error(f"Url file not found: {file_path}")
    # unique_proxies_set = set(proxies)
    # proxies = list(unique_proxies_set)
    return urls

def close_all_browsers():
    logger.info("Closing all browser instances...")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in ('chrome', 'chrome.exe', 'Chromium', 'Chromium.exe'):
                cmdline = " ".join(proc.info['cmdline'])
                # Optional: only kill ones with `--remote-debugging-port=` to be safer
                if '--remote-debugging-port=' in cmdline:
                    logger.info(f"Terminating browser process PID={proc.pid}")
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def run(urls, port_offset):
    port = 9222 + port_offset

    profile_dir = f"user_data/profile_{port}"  # Unique per port to avoid conflict

    os.makedirs(profile_dir, exist_ok=True)

    chrome_args = [
        f"--remote-debugging-port={port}",
       # f"--proxy-server={proxy}",
        f"--user-data-dir={os.path.abspath(profile_dir)}",
        # "--no-first-run",
        # "--no-default-browser-check",
        # "--disable-background-networking",
        # "--disable-default-apps",
        # "--disable-extensions",
        # "--disable-sync"
    ]
    try:
        logger.info(f"[No proxy] Starting session on port {port}...")
        with SB(uc=True, test=True, locale="en",  undetectable=True,
                #block_images=True,
                headless= False,
               #proxy=proxy,
                chromium_arg=chrome_args) as sb:

            try:
                initial_url = urls[0]
                logger.info(f"[No proxy] Visiting {initial_url}")
                sb.activate_cdp_mode(initial_url)
                start_time = time.time()
               
                inCloudflare = False
                success = False
                while time.time() - start_time < (30 + (30 if inCloudflare else 0)):
                    time.sleep(2)
                   
                    title = sb.get_title()
                    if title:
                        logger.info(f"[No proxy] Page title: {title}")
                        if time.time() - start_time > 15 and "cikgumall.com" in title:
                            logger.warning(f"[No proxy] Proxy may not be stable")
                            return False
                        if "Just a moment" in title:
                       
                            sb.uc_gui_click_captcha()
                            inCloudflare = True
                        if title and "Cikgu Mall" in title:
                            logger.info(f"[No proxy] Title matched. Moving to next URL.")
                            success = True
                            break
                
                if success == False:
                     return False
                
                
                # Continue with URLs even if initial check fails
                for url in urls:
                    try:
                        sb.open(url)

                        logger.info(f"[No proxy] Successfully visited: {url}")
                    except Exception as e:
                        logger.error(f"[No proxy] Error visiting {url}: {e}")
                        # Continue with next URL instead of failing completely
                        continue
                
                logger.info(f"[No proxy] Finished cleanly.")
               
                return True
            except Exception as e:
                logger.error(f"[No proxy] Error during execution: {e}")
                return False
    except Exception as e:
        logger.error(f"[No proxy] Failed to start session: {e}")
        return False


def run_with_proxy(proxy, urls, port_offset):
    port = 9222 + port_offset

    profile_dir = f"user_data/profile_{port}"  # Unique per port to avoid conflict

    os.makedirs(profile_dir, exist_ok=True)

    chrome_args = [
        f"--remote-debugging-port={port}",
       # f"--proxy-server={proxy}",
        f"--user-data-dir={os.path.abspath(profile_dir)}",
        # "--no-first-run",
        # "--no-default-browser-check",
        # "--disable-background-networking",
        # "--disable-default-apps",
        # "--disable-extensions",
        # "--disable-sync"
    ]
    try:
        logger.info(f"[{proxy}] Starting session on port {port}...")
        with SB(uc=True, test=True, locale="en",  undetectable=True,
                #block_images=True,
                headless= False,
               proxy=proxy,
                chromium_arg=chrome_args) as sb:

            try:
                initial_url = urls[0]
                logger.info(f"[{proxy}] Visiting {initial_url}")
                sb.activate_cdp_mode(initial_url)
                start_time = time.time()
               
                inCloudflare = False
                success = False
                while time.time() - start_time < (30 + (30 if inCloudflare else 0)):
                    time.sleep(2)
                   
                    title = sb.get_title()
                    if title:
                        logger.info(f"[{proxy}] Page title: {title}")
                        if time.time() - start_time > 15 and "cikgumall.com" in title:
                            logger.warning(f"[{proxy}] Proxy may not be stable")
                            return False
                        if "Just a moment" in title:
                       
                            sb.uc_gui_click_captcha()
                            inCloudflare = True
                        if title and "Cikgu Mall" in title:
                            logger.info(f"[{proxy}] Title matched. Moving to next URL.")
                            success = True
                            break
                
                if success == False:
                     return False
                
                
                # Continue with URLs even if initial check fails
                for url in urls:
                    try:
                        sb.open(url)

                        logger.info(f"[{proxy}] Successfully visited: {url}")
                    except Exception as e:
                        logger.error(f"[{proxy}] Error visiting {url}: {e}")
                        # Continue with next URL instead of failing completely
                        continue
                
                logger.info(f"[{proxy}] Finished cleanly.")
                with open("working_proxies.txt", "a") as wp:
                    wp.write(proxy + "\n")
                return True
            except Exception as e:
                logger.error(f"[{proxy}] Error during execution: {e}")
                return False
    except Exception as e:
        logger.error(f"[{proxy}] Failed to start session: {e}")
        return False

# Load proxies
proxies = load_proxies('proxies.txt')
if not proxies:
    logger.error("No proxies available. Exiting.")
    exit()

urls = load_urls('urls.txt')


# Settings
TIMEOUT_PER_SESSION = 60
batch_size = 5
MAX_WAIT_PER_BATCH = 60  # Maximum time to wait for a batch before moving on

logger.info("=== Starting adaptive proxy loading ===")

index=0
proxy_index = 0
completed_count = 0
port_base = 0
close_all_browsers()


for loop_num in range(1):  # Loop 10 times
    with ThreadPoolExecutor(max_workers=batch_size) as executor:

        for i in range(batch_size):
            future = executor.submit(run, urls, index %batch_size )
            index += 1
        

        while proxy_index < len(proxies):
            # Launch a batch of proxies
        
            current_batch_size = min(batch_size,  len(proxies) - proxy_index)
            logger.info(f"Starting batch of {current_batch_size} proxies")
            future_to_proxy = {}
            for i in range(current_batch_size):
                current_proxy = proxies[proxy_index]
                future = executor.submit(run_with_proxy, current_proxy, urls, proxy_index %batch_size )
                future_to_proxy[future] = (current_proxy, port_base + i)
                proxy_index += 1
            
            # Process the batch with a timeout
            batch_start_time = time.time()
            remaining_futures = list(future_to_proxy.keys())
            
            while remaining_futures and time.time() - batch_start_time < MAX_WAIT_PER_BATCH:
                # Get completed futures with a short timeout to avoid blocking
                try:
                    done_futures, remaining_futures = wait(remaining_futures, timeout=5, return_when=FIRST_COMPLETED)
                except AttributeError:
                    # If _waiters is not accessible, use alternative approach
                    done_futures = set()
                    new_remaining = []
                    for f in list(remaining_futures):
                        if f.done():
                            done_futures.add(f)
                        else:
                            new_remaining.append(f)
                    remaining_futures = new_remaining
                
                for future in done_futures:
                    proxy, port = future_to_proxy[future]
                    try:
                        result = future.result(timeout=1)
                        if result:
                            completed_count += 1
                            logger.info(f"[{proxy}] Finished successfully and counted.")
                        else:
                            logger.warning(f"[{proxy}] Finished but reported failure.")
                    except TimeoutError:
                        logger.error(f"[{proxy}] Timed out during result retrieval")
                    except Exception as e:
                        logger.error(f"[{proxy}] Error retrieving result: {str(e)}")
            
            # Handle remaining futures that didn't complete in time
            if remaining_futures:
                logger.warning(f"{len(remaining_futures)} proxies did not complete within the timeout and will be skipped")
                for future in remaining_futures:
                    proxy, port = future_to_proxy[future]
                    logger.warning(f"[{proxy}] Cancelling due to timeout")
                    future.cancel()
                
            
            # Increment port base for next batch to avoid port conflicts
            port_base += batch_size
            
            logger.info(f"Batch completed. Progress: {proxy_index}/{len(proxies)} proxies processed")

    logger.info(f"\n=== All proxies completed: {completed_count}/{len(proxies)} successful ===")
close_all_browsers()