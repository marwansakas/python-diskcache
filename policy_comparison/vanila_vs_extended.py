import os
import random
import time
import json
import matplotlib.pyplot as plt
from diskcache import Cache
from diskcache.extensions.score_based_cache import ScoreBasedCache


def generate_workload(cache, n_requests=10000, key_space=5000, size_range=(10_000, 70_000)):
    hits, misses, latencies = 0, 0, []

    for _ in range(n_requests):
        key = random.randint(0, key_space - 1)
        start = time.time()
        if key in cache:
            _ = cache[key]
            hits += 1
        else:
            size = random.randint(*size_range)
            value = os.urandom(size)
            cache.set(key, value, tag=random.uniform(5, 15))  # high cost
            misses += 1
        latencies.append(time.time() - start)

    return {
        "hit_rate": hits / n_requests,
        "avg_latency": sum(latencies) / len(latencies),
        "p95_latency": sorted(latencies)[int(0.95 * len(latencies))],
        "p99_latency": sorted(latencies)[int(0.99 * len(latencies))]
    }


def run_experiments():
    sizes = [50, 100, 200]  # MB
    results = {"baseline": [], "score_based": []}

    for size_mb in sizes:
        size_bytes = size_mb * 1024 * 1024

        # Baseline
        baseline = Cache(f"./baseline_{size_mb}MB", size_limit=size_bytes)
        res_base = generate_workload(baseline)
        res_base["size_MB"] = size_mb
        results["baseline"].append(res_base)

        # Extended (ScoreBasedCache)
        score = ScoreBasedCache(f"./score_{size_mb}MB", size_limit=size_bytes,
                                alpha=3.0, beta=6.0, lam=1.0)  # amplified weights
        res_score = generate_workload(score)
        res_score["size_MB"] = size_mb
        results["score_based"].append(res_score)

    # Save JSON
    with open("cache_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def plot_results(results):
    sizes = [r["size_MB"] for r in results["baseline"]]

    for metric in ["p95_latency", "hit_rate"]:
        baseline_vals = [r[metric] for r in results["baseline"]]
        score_vals = [r[metric] for r in results["score_based"]]

        plt.figure()
        plt.plot(sizes, baseline_vals, label="Baseline", marker="o")
        plt.plot(sizes, score_vals, label="ScoreBased", marker="o")
        plt.title(f"{metric} vs Cache Size")
        plt.xlabel("Cache Size (MB)")
        plt.ylabel(metric)
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{metric}_comparison.png")


if __name__ == "__main__":
    results = run_experiments()
    plot_results(results)
    print("✅ Done. JSON and plots saved.")
