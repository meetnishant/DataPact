"""
Coverage check module.
Runs pytest with coverage and reports total line coverage percentage.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _run_pytest(cov_xml: Path) -> int:
    """
    Run pytest with coverage output to the given XML file path.
    Returns the pytest exit code.
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src/datapact",
        f"--cov-report=xml:{cov_xml}",
        "--cov-report=term-missing",
        "-q",
    ]
    return subprocess.call(cmd)


def _read_coverage_percent(cov_xml: Path) -> float:
    """
    Read total line coverage percent from coverage XML.
    Returns a percentage between 0 and 100.
    """
    tree = ET.parse(cov_xml)
    root = tree.getroot()
    line_rate = root.attrib.get("line-rate")
    if line_rate is None:
        raise ValueError("coverage.xml missing line-rate attribute")
    return float(line_rate) * 100.0


def main() -> int:
    """
    CLI entry point for coverage checks.
    Runs tests with coverage and prints the total percentage.
    """
    parser = argparse.ArgumentParser(
        description="Run coverage check and report total coverage."
    )
    parser.add_argument(
        "--cov-file",
        default="coverage.xml",
        help="Path to write coverage XML output (default: coverage.xml)",
    )
    parser.add_argument(
        "--min",
        type=float,
        default=None,
        help="Minimum required coverage percent (fail if below)",
    )
    args = parser.parse_args()

    cov_xml = Path(args.cov_file)
    exit_code = _run_pytest(cov_xml)
    if exit_code != 0:
        print("Coverage run failed; see pytest output for details.")
        return exit_code

    percent = _read_coverage_percent(cov_xml)
    print(f"Total coverage: {percent:.2f}%")

    if args.min is not None and percent < args.min:
        print(f"Coverage {percent:.2f}% is below minimum {args.min:.2f}%")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
