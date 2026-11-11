"""Compile the canonical paper from any working directory."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    tectonic = shutil.which('tectonic')
    if not tectonic:
        raise SystemExit('Install Tectonic and put it on PATH before compiling the paper.')
    build = ROOT/'results/build'
    build.mkdir(parents=True, exist_ok=True)
    # Keep the reading/editing folder free of transient TeX files from earlier builds.
    for extension in ['aux', 'log', 'out']:
        old = ROOT/'deliverables'/f'UNNUMBERED_BOOKS.{extension}'
        if old.exists():
            shutil.move(str(old), str(build/old.name))
    subprocess.run([tectonic, '--keep-logs', '--outdir', str(build), 'UNNUMBERED_BOOKS.tex'],
                   cwd=ROOT/'deliverables', check=True)
    shutil.copy2(build/'UNNUMBERED_BOOKS.pdf', ROOT/'deliverables/UNNUMBERED_BOOKS.pdf')


if __name__ == '__main__':
    main()
