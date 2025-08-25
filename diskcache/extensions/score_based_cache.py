from diskcache import Cache, EVICTION_POLICY
import os

class ScoreBasedCache(Cache):
    def __init__(self, directory=None, size_limit=2**30, eviction_policy='score-based',
                 alpha=0.0, beta=0.0, lam=0.0, **kwargs):
        self._alpha = alpha
        self._beta = beta
        self._lam = lam

        if eviction_policy not in EVICTION_POLICY:
            score_expr = (
                "(0.0"
                " - ? * (? - access_time)"
                " + ? * size / ?"
                " + ? * CAST(tag AS FLOAT))"
            )

            EVICTION_POLICY[eviction_policy] = {
                'init': 'SELECT key, size, tag, access_time FROM Cache',
                'cull': (
                    "SELECT key, filename FROM Cache "
                    f"WHERE filename IS NOT NULL "
                    f"ORDER BY {score_expr} ASC LIMIT ?"
                ),
                'get': None  # avoid KeyError from missing 'fields'
            }

        super().__init__(
            directory=directory,
            size_limit=size_limit,
            eviction_policy=eviction_policy,
            **kwargs
        )

    def _cull(self, now, sql, cleanup, limit=None):
        cull_limit = self.cull_limit if limit is None else limit
        if cull_limit == 0 or self.volume() < self.size_limit:
            return

        query = EVICTION_POLICY[self.eviction_policy]['cull']

        bindings = (
            self._lam,
            now,
            self._alpha,
            self.size_limit or 1,  # avoid division by zero
            self._beta,
            cull_limit,
        )

        try:
            rows = sql(query, bindings).fetchall()
        except Exception as e:
            print(f"[ERROR] During eviction SQL query: {e}")
            return

        # --- DEBUGGING: Score calculation for all cache entries ---
        for row in sql('SELECT key, size, tag, access_time, filename FROM Cache').fetchall():
            try:
                key, size, tag, access_time, filename = row
                if not filename or not os.path.exists(filename):
                    continue  # skip incomplete or evicted rows

                cost = float(tag) if tag is not None else 0.0
                age = now - access_time if access_time is not None else 0.0
                norm_size = size / (self.size_limit or 1)
                score = (
                    - self._lam * age +
                    self._alpha * norm_size +
                    self._beta * cost
                )
                print(f"[DEBUG] key={key}, size={size}, cost={cost:.2f}, age={age:.2f}, score={score:.4f}")
            except Exception as e:
                print(f"[DEBUG] Skipped row due to error: {e}")

        # --- Perform eviction ---
        for _, filename in rows:
            if filename and os.path.exists(filename):
                cleanup(filename)
                sql("DELETE FROM Cache WHERE filename = ?", (filename,))
