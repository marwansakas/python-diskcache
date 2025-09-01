# 📦 Score-Based Cache – DiskCache Extension

This repository introduces a **cost-aware, score-based caching policy** as an extension to [DiskCache](https://grantjenks.com/docs/diskcache/). It includes benchmarking tools, synthetic workload generation, and testing suites for evaluating the performance of the new caching strategy.


---

## ⚙️ Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/marwansakas/python-diskcache.git

   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate         # On Linux/macOS
   .venv\Scripts\activate          # On Windows
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements-devs.txt
   ```

---

## 🧪 Run Tests

Run **all tests**, including unit and benchmark tests:
```bash
pytest
```

Run only unit tests (excluding benchmarks):
```bash
pytest --benchmark-disable
```

Run only the unit tests for the new policy
```bash
pytest .\marwan_tests
```


Run a specific test file (e.g., `test_score_based_cache.py`):
```bash
pytest marwan_tests/test_score_based_cache.py
```



## 🚀 Benchmark the Score-Based Cache

Run benchmark suite:
```bash
pytest marwan_tests/test_benchmarks.py --benchmark-only
```

Run with debug logging (no output capture):
```bash
pytest marwan_tests/test_benchmarks.py --benchmark-only --capture=no
```

---

## 📊 Collect Benchmark Results

1. Save benchmark results to file:
   ```bash
   pytest marwan_tests/test_benchmarks.py --benchmark-only --benchmark-save=score_cache_run
   ```

2. Export results as JSON:
   ```bash
   pytest-benchmark export score_cache_run --output benchmark_result.json
   ```

---

## 📈 Parameter Sweeps and Analysis

Generate graphs to analyze `alpha`, `beta`, and `lambda` parameter effects:

```bash
python policy_comparison/parameter_sweep_and_analysis.py
```

This script runs synthetic workloads using varying parameters and produces plots:
- `hit_rate_vs_alpha.png`
- `p95_latency_vs_beta.png`
- etc.

The script also saves detailed logs to:
- `parameter_sweep_results.json`

---

## 📊 Compare Score-Based vs. Vanilla LRU

To run a head-to-head comparison between the baseline (LRU) and the Score-Based policy:
```bash
python policy_comparison/vanilla_vs_extended.py
```

This script will:
- Execute a common workload on both policies
- Report and compare hit rates and latency metrics
- Optionally generate visual comparisons

---

## 📁 Additional Notes

- The custom cache logic is implemented in `diskcache/extensions/score_based_cache.py`
- All tests assume DiskCache is installed and discoverable
- Make sure to clean old `__pycache__` directories between changes if needed