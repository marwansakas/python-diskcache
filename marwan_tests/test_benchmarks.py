import time
import pytest
import sys
import os

# Ensure local diskcache is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from diskcache.extensions.score_based_cache import ScoreBasedCache
from diskcache import Cache

# 🔧 Fix 1: Move class outside to avoid pickling error
class ExpensiveValue:
    def __init__(self, sleep_time):
        self.sleep_time = sleep_time

    def __repr__(self):
        time.sleep(self.sleep_time)
        return f"<ExpensiveValue {self.sleep_time}s>"


@pytest.mark.benchmark(group="get")
def test_cache_get_latency(benchmark):
    cache = ScoreBasedCache(size_limit=100_000, alpha=1.0, beta=1.0, lam=0.0)
    cache["hot"] = "value"

    def fetch():
        return cache["hot"]

    result = benchmark(fetch)
    assert result == "value"


@pytest.mark.benchmark(group="set")
def test_cache_set_latency(benchmark):
    cache = ScoreBasedCache(size_limit=100_000, alpha=0.5, beta=0.5, lam=0.0)

    def insert():
        cache.set("key", "value")

    benchmark(insert)
    assert "key" in cache


@pytest.mark.benchmark(group="eviction")
def test_cache_eviction_under_pressure(benchmark):
    cache = ScoreBasedCache(size_limit=1024, alpha=1.0, beta=1.0, lam=0.0)

    def fill_cache():
        for i in range(200):
            cache.set(f"key{i}", "x" * 64)

    benchmark(fill_cache)


@pytest.mark.parametrize("alpha,beta,lam", [
    (1.0, 0.0, 0.0),  # size-only
    (0.0, 1.0, 0.0),  # cost-only
    (0.0, 0.0, 1.0),  # age-only
    (0.5, 0.5, 0.0),  # hybrid
])
def test_eviction_sensitivity(benchmark, alpha, beta, lam):
    cache = ScoreBasedCache(size_limit=2048, alpha=alpha, beta=beta, lam=lam)

    def fill():
        for i in range(100):
            cache.set(f"k{i}", "x" * 128)

    benchmark(fill)


@pytest.mark.benchmark(group="set-variable")
def test_variable_size_eviction(benchmark):
    cache = ScoreBasedCache(size_limit=8192)
    sizes = [32, 128, 512, 2048]

    def insert():
        for i, s in enumerate(sizes):
            cache.set(f"key{i}", "x" * s)

    benchmark(insert)


@pytest.mark.benchmark(group="cost-aware")
def test_miss_cost_eviction(benchmark):
    cache = ScoreBasedCache(size_limit=2048)

    def insert():
        for i in range(20):
            cache.set(f"key{i}", ExpensiveValue(0.01))  # 10ms simulated cost

    benchmark(insert)


# 🔧 Fix 2: Split into 2 benchmark functions for baseline vs scored
@pytest.mark.benchmark(group="baseline-compare")
def test_regular_cache_insert(benchmark):
    baseline = Cache(size_limit=2048)

    def insert_baseline():
        for i in range(50):
            baseline.set(f"b{i}", "x" * 64)

    benchmark(insert_baseline)


@pytest.mark.benchmark(group="baseline-compare")
def test_scored_cache_insert(benchmark):
    scored = ScoreBasedCache(size_limit=2048)

    def insert_scored():
        for i in range(50):
            scored.set(f"s{i}", "x" * 64)

    benchmark(insert_scored)
