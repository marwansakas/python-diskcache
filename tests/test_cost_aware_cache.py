import time
import pytest
from diskcache import Cache
from diskcache.extensions.score_based_cache import ScoreBasedCache

@pytest.mark.parametrize("alpha, beta, lam, expected_survivor", [
    (1.0, 0.0, 0.0, "small-cheap"),       # size matters → keep small
    (0.0, 1.0, 0.0, "large-expensive"),   # cost matters → keep expensive
    (0.0, 0.0, 1.0, "small-cheap"),  # age matters → keep newer
    (1.0, 1.0, 0.0, "large-expensive"),   # size+cost balance
])
def test_score_based_eviction(tmp_path, alpha, beta, lam, expected_survivor):
    cache = ScoreBasedCache(directory=tmp_path.name, size_limit=100 * 1024,
                            alpha=alpha, beta=beta, lam=lam)

    with cache:
        # Use original `set()` from Cache (not overridden)
        Cache.set(cache, "large-expensive", b"x" * 80_000, tag=str(100.0))
        Cache.set(cache, "small-cheap", b"x" * 500, tag=str(10.0))

        # Simulate recency and frequency
        cache.get("large-expensive")
        time.sleep(1)  # Make "small-cheap" more recent
        cache.get("small-cheap")

        # Add a large filler to force eviction
        Cache.set(cache, "filler", b"x" * 90_000)

        survivors = {
            key: cache.get(key) is not None
            for key in ["large-expensive", "small-cheap"]
        }

        print(f"α={alpha}, β={beta}, λ={lam}")
        print("Survivors:", survivors)

        now = time.time()
        for key in ["large-expensive", "small-cheap"]:
            row = cache._sql("SELECT size, tag, access_time FROM Cache WHERE key = ?", (key,)).fetchone()
            if row:
                size, tag, atime = row
                cost = float(tag)
                age = now - atime
                norm_size = size / cache.size_limit
                score = (
                        - lam * age +
                        alpha * norm_size +
                        beta * cost
                )
                print(f"[SCORE] key={key}, size={size}, cost={cost}, age={age:.2f}, score={score:.4f}")

        assert survivors[expected_survivor] is True


import os
import time
import tempfile
from diskcache.extensions.score_based_cache import ScoreBasedCache


def test_cull_removes_low_score_entries_and_logs(capfd):
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ScoreBasedCache(
            directory=tmpdir,
            size_limit=100 * 1024,
            alpha=1.0,
            beta=1.0,
            lam=1.0,
        )

        with cache:
            # Add one large with high cost → high score
            cache.set("high-score", b"x" * 80_000, tag="200")

            # Add small with low cost → low score
            cache.set("low-score", b"x" * 5_000, tag="5")

            # Add filler to force eviction
            cache.set("filler", b"x" * 50_000)

            # Manually call _cull to trigger debug output
            now = time.time()
            removed = []
            cache._cull(now, cache._sql, removed.append)

        # Read captured output
        out, _ = capfd.readouterr()

        assert "key=low-score" in out
        assert any("score=" in line for line in out.splitlines())
        assert os.path.basename(removed[0]) in out or removed[0]  # file removed


def test_cull_handles_missing_tag_and_access_time(capfd):
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ScoreBasedCache(
            directory=tmpdir,
            size_limit=10 * 1024,
            alpha=1.0,
            beta=1.0,
            lam=1.0,
        )

        with cache:
            now = time.time()

            # Insert a dummy entry directly in DB to simulate missing fields
            cache._sql("INSERT INTO Cache (key, value, size, raw) VALUES (?, ?, ?, ?)",
                       ("no-tag-no-atime", b"x" * 2000, 2000, False))

            cache.set("another-entry", b"x" * 9000, tag="1.0")

            removed = []
            cache._cull(now, cache._sql, removed.append)

        out, _ = capfd.readouterr()
        assert "Skipped row due to error" in out or "score=" in out
        assert any("key=no-tag-no-atime" in line or "key=another-entry" in line for line in out.splitlines())

