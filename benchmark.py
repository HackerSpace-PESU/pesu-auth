import os
import time

import requests
import argparse
import logging
from tqdm.auto import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()


def make_request():
    data = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
    }
    start_time = time.time()
    response = requests.post("http://localhost:5000/authenticate", json=data)
    elapsed_time = time.time() - start_time
    return response.json(), elapsed_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark the authentication endpoint."
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Maximum number of concurrent workers (default: 10)",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=10,
        help="Number of threads to use for the benchmark (default: 10)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run the benchmark in parallel using threads",
    )
    args = parser.parse_args()

    max_workers = args.max_workers
    num_threads = args.num_threads
    parallel = args.parallel

    success = []
    times = []
    if parallel:
        logging.info(
            f"Running benchmark with max {max_workers} workers and {num_threads} threads in parallel..."
        )
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_threads)]
            for future in as_completed(futures):
                try:
                    response, elapsed = future.result()
                    times.append(elapsed)
                    logging.debug(response)
                    if response.get("status"):
                        success.append(1)
                    else:
                        success.append(0)
                except Exception as e:
                    logging.error(f"Request failed: {e}")
    else:
        logging.info(f"Running benchmark with {num_threads} threads sequentially...")
        for _ in tqdm(range(num_threads), desc="Processing requests"):
            response, elapsed = make_request()
            times.append(elapsed)
            logging.debug(response)
            if response.get("status"):
                success.append(1)
            else:
                success.append(0)

    with open("benchmark.csv", "w") as f:
        f.write("status,time\n")
        for s, t in zip(success, times):
            f.write(f"{s},{t}\n")

    print(
        f"Benchmark completed. Successful requests: {sum(success)} out of {len(success)}"
    )
    print(f"Average time per request: {sum(times) / len(times):.2f} seconds")
    print(f"Total time taken: {sum(times):.2f} seconds")
