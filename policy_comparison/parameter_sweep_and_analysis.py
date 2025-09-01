
import os
import random
import time
import json
import matplotlib.pyplot as plt
from diskcache import Cache
from score_based_cache import ScoreBasedCache

def generate_workload(cache, n_requests=5000, key_space=2000, size_range=(5000, 50000)):
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
            cache.set(key, value, tag=random.uniform(1, 10))  # tag = cost
            misses += 1
        latencies.append(time.time() - start)

    return {
        "hit_rate": hits / n_requests,
        "avg_latency": sum(latencies) / len(latencies),
        "p95_latency": sorted(latencies)[int(0.95 * len(latencies))],
        "p99_latency": sorted(latencies)[int(0.99 * len(latencies))]
    }

def parameter_sweep(param_name, values, fixed_alpha=1.0, fixed_beta=1.0, fixed_lam=1.0):
    results = []

    for val in values:
        if param_name == "alpha":
            alpha, beta, lam = val, fixed_beta, fixed_lam
        elif param_name == "beta":
            alpha, beta, lam = fixed_alpha, val, fixed_lam
        elif param_name == "lam":
            alpha, beta, lam = fixed_alpha, fixed_beta, val

        cache = ScoreBasedCache(f"./sweep_{param_name}_{val}", size_limit=50 * 1024 * 1024,
                                alpha=alpha, beta=beta, lam=lam)
        result = generate_workload(cache)
        result[param_name] = val
        results.append(result)

    return results

def plot_sweep(results, param_name, metric):
    x = [r[param_name] for r in results]
    y = [r[metric] for r in results]

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.title(f"{metric} vs {param_name}")
    plt.xlabel(param_name)
    plt.ylabel(metric)
    plt.grid(True)
    plt.savefig(f"{metric}_vs_{param_name}.png")

def main():
    param_values = [0.0, 0.5, 1.0, 2.0, 4.0]

    all_results = {
        "alpha_sweep": parameter_sweep("alpha", param_values),
        "beta_sweep": parameter_sweep("beta", param_values),
        "lam_sweep": parameter_sweep("lam", param_values)
    }

    with open("parameter_sweep_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    for param in ["alpha", "beta", "lam"]:
        for metric in ["hit_rate", "p95_latency"]:
            plot_sweep(all_results[f"{param}_sweep"], param, metric)

    print("✅ Parameter sweep complete. Plots and data saved.")

if __name__ == "__main__":
    main()
