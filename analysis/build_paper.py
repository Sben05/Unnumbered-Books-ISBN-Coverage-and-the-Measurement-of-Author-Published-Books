"""Compile the canonical paper from any working directory."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    tectonic = shutil.which('tectonic')
    if not tectonic:
        raise SystemExit('Install Tectonic and put it on PATH before compiling the paper.')
    subprocess.run([tectonic, '--keep-logs', '--keep-intermediates', 'UNNUMBERED_BOOKS.tex'],
                   cwd=ROOT/'deliverables', check=True)


if __name__ == '__main__':
    main()
