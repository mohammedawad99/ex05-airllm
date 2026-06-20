"""MetricsCollector — timing + memory metrics for a single inference run.

Pure and testable: the clock and the RSS source are injectable, so unit tests exercise the
metric math with a controlled clock and **no** model inference, network, or real timing. See
``docs/PRD_measurement.md``. Memory is sampled via ``psutil`` by default.
"""

from __future__ import annotations

from collections.abc import Callable


def _default_rss_bytes() -> int:
    import psutil

    return int(psutil.Process().memory_info().rss)


class MetricsCollector:
    """Collect TTFT / TPOT / throughput / runtime / peak-RAM for one run."""

    def __init__(
        self,
        clock: Callable[[], float],
        rss_bytes: Callable[[], int] = _default_rss_bytes,
    ) -> None:
        self._clock = clock
        self._rss_bytes = rss_bytes
        self._start: float | None = None
        self._first_token: float | None = None
        self._end: float | None = None
        self._output_tokens: int | None = None
        self._peak_rss_mb: float = 0.0

    def start(self) -> None:
        self._start = self._clock()
        self._first_token = None
        self._end = None
        self._output_tokens = None
        self.sample_memory()

    def mark_first_token(self) -> None:
        if self._start is None:
            raise RuntimeError("mark_first_token() called before start()")
        if self._first_token is None:
            self._first_token = self._clock()

    def finish(self, output_tokens: int) -> dict[str, float | None]:
        if self._start is None:
            raise RuntimeError("finish() called before start()")
        self._end = self._clock()
        self._output_tokens = int(output_tokens)
        self.sample_memory()
        return self.metrics()

    def sample_memory(self) -> None:
        mb = self._rss_bytes() / 1_000_000
        self._peak_rss_mb = max(self._peak_rss_mb, mb)

    def metrics(self) -> dict[str, float | None]:
        total = self._delta(self._start, self._end)
        ttft = self._delta(self._start, self._first_token)
        generation = self._delta(self._first_token, self._end)
        tokens = self._output_tokens
        return {
            "total_runtime_seconds": _round(total),
            "ttft_seconds": _round(ttft),
            "generation_seconds": _round(generation),
            "tpot_seconds": _round(self._tpot(generation, tokens)),
            "tokens_per_second": _round(self._throughput(generation, total, tokens)),
            "peak_ram_mb": round(self._peak_rss_mb, 1) if self._peak_rss_mb else None,
        }

    @staticmethod
    def _delta(a: float | None, b: float | None) -> float | None:
        return None if a is None or b is None else b - a

    @staticmethod
    def _tpot(generation: float | None, tokens: int | None) -> float | None:
        if generation is None or not tokens or tokens <= 1:
            return None
        return generation / (tokens - 1)

    @staticmethod
    def _throughput(
        generation: float | None, total: float | None, tokens: int | None
    ) -> float | None:
        if not tokens or tokens <= 0:
            return None
        window = generation if generation and generation > 0 else total
        if not window or window <= 0:
            return None
        return tokens / window


def _round(value: float | None, ndigits: int = 4) -> float | None:
    return None if value is None else round(value, ndigits)
