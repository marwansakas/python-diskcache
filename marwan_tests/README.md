# 📊 Benchmark Suite for Score-Based Cache (DiskCache Extension)

This README provides concise instructions for setting up, running performance tests, and collecting benchmarking logs for the ScoreBasedCache system.

## ⚙️ Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `pytest`, `pytest-benchmark`, and `psutil` are installed:
   ```bash
   pip install pytest pytest-benchmark psutil
   ```

## 🧪 Run All Tests

Run all unit and benchmark tests:
```bash
pytest
```

Run only regular (non-benchmark) tests:
```bash
pytest --benchmark-disable
```

## 🚀 Run Benchmarks

Run the benchmark tests:
```bash
pytest marwan_tests/test_benchmarks.py --benchmark-only
```

Run with no output capture (useful for debugging):
```bash
pytest marwan_tests/test_benchmarks.py --benchmark-only --capture=no
```

## 📉 Collect Metrics & JSON Logs

To collect detailed benchmark results (including mean, p95, p99, throughput, etc.):

1. Run benchmarks with output saved to a JSON file:
   ```bash
   pytest marwan_tests/test_benchmarks.py --benchmark-only --benchmark-save=score_cache_run
   ```

2. Export results to a JSON file:
   ```bash
   pytest-benchmark export score_cache_run --output benchmark_result.json
   ```

3. The `benchmark_result.json` will appear in your project root or working directory.

---

For additional metrics like memory and CPU utilization, see `marwan_tests/test_metrics.py`.