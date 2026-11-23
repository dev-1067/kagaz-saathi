"""Assemble build/ (the Lambda package) from the repository: only what the app needs at runtime.

    python infra/build.py        ->  build/  (kagaz/, web/, results/*.json, lambda_handler.py, dynamo_store.py)

Then deploy with AWS SAM (see infra/DEPLOY.md). boto3 is already inside the Lambda runtime, so nothing else is bundled.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / "kagaz", OUT / "kagaz", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
shutil.copytree(ROOT / "web", OUT / "web")
(OUT / "results").mkdir()
for f in ("model_report.json", "stress_report.json"):
    shutil.copy(ROOT / "results" / f, OUT / "results" / f)
for f in ("lambda_handler.py", "dynamo_store.py"):
    shutil.copy(ROOT / "infra" / f, OUT / f)
size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
print(f"built {OUT}  ({size / 1e6:.1f} MB, limit for a direct upload is 50 MB zipped / 250 MB unzipped)")
