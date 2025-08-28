import os
import random
import time
from diskcache import Cache
from diskcache.extensions.score_based_cache import ScoreBasedCache


def generate_workload(cache, n_requests=10000, key_space=1000, size_range=(1_000, 50_000)):
    hits, misses, latencies = 0, 0, []

    for _ in range(n_requests):
        key = random.randint(0, key_space - 1)
        start = time.time()
        if key in cache:
            _ = cache[key]  # cache hit
            hits += 1
        else:
            size = random.randint(*size_range)
            value = os.urandom(size)
            cache.set(key, value, tag=random.uniform(1, 10))  # tag = cost
            misses += 1
        latencies.append(time.time() - start)

    return {
        "hit_rate": hits / n_requests,
        "avg_latency": sum(latencies) / len(latencies),
        "p95_latency": sorted(latencies)[int(0.95 * len(latencies))],
        "p99_latency": sorted(latencies)[int(0.99 * len(latencies))]
    }

if __name__ == "__main__":
    # Example: run benchmark on baseline DiskCache
    baseline_cache = Cache("./baseline_cache", size_limit=50 * 1024 * 1024)  # 50MB
    result = generate_workload(baseline_cache)
    print("Baseline results:", result)

    # Example: run benchmark on your ScoreBasedCache
    score_cache = ScoreBasedCache("./score_cache", size_limit=50 * 1024 * 1024,
                                  alpha=1.0, beta=2.0, lam=0.5)
    result = generate_workload(score_cache)
    print("ScoreBasedCache results:", result)
