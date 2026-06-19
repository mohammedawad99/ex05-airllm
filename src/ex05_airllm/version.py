"""Single source of truth for the runtime package version.

Kept in sync with ``[project].version`` in ``pyproject.toml``; the consistency is enforced
by ``tests/unit/test_version.py`` (requirement R-VERSION — versioning starts at 1.0.0).
"""

__version__ = "1.0.0"
