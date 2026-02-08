"""Enable coverage subprocess collection when COVERAGE_PROCESS_START is set.

This file is imported automatically on Python startup when on the sys.path.
It will attempt to call coverage.process_startup() so worker processes
started by multiprocessing will also record coverage data into parallel
.coverage.* files.
"""
import os

if os.environ.get("COVERAGE_PROCESS_START"):
    try:
        # coverage may not be available in minimal environments; guard import
        import coverage

        coverage.process_startup()
    except Exception:
        pass
