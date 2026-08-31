"""Compatibility entry point; delegates to the standard-library runner."""

from .run_tests import main

if __name__ == "__main__":
    raise SystemExit(main())
