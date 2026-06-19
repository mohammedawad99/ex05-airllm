"""ex05-airllm: tooling for the local massive-LLM AirLLM experiment.

This package will host the layered SDK, measurement, and analysis components described in
``docs/PLAN.md``. Stage 2A provides only the package skeleton and version tracking — no
experiment, benchmark, AirLLM, or DirectML logic is implemented yet.
"""

from ex05_airllm.version import __version__

__all__ = ["__version__"]
