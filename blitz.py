import argparse
import requests
import threading
import time
from colorama import Fore, Style, init

# Initialize colors
init(autoreset=True)

# Global counters
success_count = 0
fail_count = 0
lock = threading.Lock() # Prevents threads from fighting over the counters

def send_request(url, method, payload=None):
    """Function that a single thread will run."""
    global success_count, fail_count

    try:
        if method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=5)
        else:
            response = requests.get(url, timeout=5)

        # Thread-safe counter update
        with lock:
            if 200 <= response.status_code < 300:
                print(f"{Fore.GREEN}[SUCCESS] {response.status_code} received from {url}")
                success_count += 1
            else:
                print(f"{Fore.YELLOW}[WARNING] {response.status_code} received")
                fail_count += 1

    except Exception as e:
        with lock:
            print(f"{Fore.RED}[ERROR] Request failed: {e}")
            fail_count += 1

def start_blitz(url, count, concurrency, method):
    print(f"{Fore.CYAN}--- Starting Blitz on {url} ---")
    print(f"Total Requests: {count} | Threads: {concurrency} | Method: {method}\n")

    threads = []
    start_time = time.time()

    # Launch threads in batches
    for i in range(count):
        t = threading.Thread(target=send_request, args=(url, method))
        threads.append(t)
        t.start()
        
        # Simple concurrency control: 
        # If we have too many active threads, wait for some to finish
        if len(threads) >= concurrency:
            for t in threads:
                t.join()
            threads = []

    # Cleanup remaining threads
    for t in threads:
        t.join()

    duration = time.time() - start_time

    print(f"\n{Fore.CYAN}--- Blitz Complete ---")
    print(f"Time Taken: {duration:.2f} seconds")
    print(f"{Fore.GREEN}Successful: {success_count}")
    print(f"{Fore.RED}Failed:     {fail_count}")

if __name__ == "__main__":
    # Set up CLI Arguments
    parser = argparse.ArgumentParser(description="HTTP Request Repeater & Load Tester")
    parser.add_argument("url", help="The target URL (e.g., https://google.com)")
    parser.add_argument("-n", "--number", type=int, default=10, help="Number of requests to send")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("-m", "--method", type=str, default="GET", choices=["GET", "POST"], help="HTTP Method")

    args = parser.parse_args()

    start_blitz(args.url, args.number, args.concurrency, args.method)
