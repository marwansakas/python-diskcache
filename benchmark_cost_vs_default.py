import time
import random
import string
from diskcache import Cache
from diskcache.extensions.score_based_cache import CostAwareCache


NUM_ITEMS = 5000
VALUE_SIZE = 2048  # 2 KB
KEY_LENGTH = 10



def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def generate_data():
    for _ in range(NUM_ITEMS):
        key = random_string(KEY_LENGTH)
        value = random_string(VALUE_SIZE).encode()
        compute_time = random.uniform(0.01, 0.3)
        yield key, value, compute_time




def run_benchmark(CacheClass, label):
    if CacheClass is CostAwareCache:
        cache = CacheClass(size_limit=1 * 1024 * 1024, alpha=1.0, beta=20.0)  # try 20, 50, 100
    else:
        cache = CacheClass(size_limit=1 * 1024 * 1024)
    hits = 0
    misses = 0
    start = time.time()

    # Save items to re-test them later
    items = list(generate_data())

    # Insert items into the cache
    for key, value, compute_time in items:
        if isinstance(cache, CostAwareCache):
            cache.set(key, value, compute_time=compute_time)
        else:
            cache.set(key, value)

    # Try reading all keys again to see which ones remain in cache
    for key, _, _ in items:
        if cache.get(key) is not None:
            hits += 1
        else:
            misses += 1

    end = time.time()
    total_time = end - start

    print(f"--- {label} ---")
    print(f"Hits: {hits}, Misses: {misses}")
    print(f"Hit rate: {hits / (hits + misses):.2f}")
    print(f"Elapsed time: {total_time:.2f} seconds\n")

    cache.clear()
    cache.close()




if __name__ == '__main__':
    run_benchmark(Cache, "Default Cache")
    run_benchmark(CostAwareCache, "Cost-Aware Cache")

