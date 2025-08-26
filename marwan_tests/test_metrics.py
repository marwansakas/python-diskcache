import time
import os
import sys
import psutil
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from diskcache.extensions.score_based_cache import ScoreBasedCache

# 📊 Cache Hit Rate
def test_cache_hit_rate():
    cache = ScoreBasedCache(size_limit=1024)
    total = 100
    hits = 0

    for i in range(50):
        cache.set(f"key{i}", f"val{i}")

    for i in range(total):
        key = f"key{i % 60}"  # 50 known keys, 10 misses
        if key in cache:
            _ = cache[key]
            hits += 1

    hit_rate = hits / total
    print(f"Cache Hit Rate: {hit_rate:.2%}")
    assert hit_rate > 0.75  # Example expectation


# 📈 Memory & CPU Utilization
def test_resource_usage():
    cache = ScoreBasedCache(size_limit=10_000_000)
    process = psutil.Process(os.getpid())

    cpu_start = psutil.cpu_percent(interval=None)
    mem_start = process.memory_info().rss

    for i in range(1000):
        cache.set(f"key{i}", "x" * 1024)

    time.sleep(0.2)  # Let CPU settle
    cpu_end = psutil.cpu_percent(interval=0.1)
    mem_end = process.memory_info().rss

    print(f"Memory Used: {(mem_end - mem_start) / 1024:.2f} KB")
    print(f"CPU % Used: {cpu_end - cpu_start:.2f}%")

    assert mem_end > mem_start


# 📦 Throughput: requests per second
def test_throughput():
    cache = ScoreBasedCache(size_limit=100_000)

    start = time.time()
    for i in range(5000):
        cache.set(f"key{i}", "value")
        _ = cache.get(f"key{i}")
    end = time.time()

    duration = end - start
    throughput = 5000 * 2 / duration  # sets + gets
    print(f"Throughput: {throughput:.2f} ops/sec")
    assert throughput > 500  # Example lower bound
