"""Scores the full analyzer pipeline on the stress sets. Writes results/stress_report.json.

    python model/eval_stress.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kagaz.analyzer import analyze  # noqa: E402


def run(name):
    rows = [json.loads(l) for l in (ROOT / "model" / "data" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    c = {"scam_called_scam": 0, "scam_called_suspicious": 0, "scam_called_genuine": 0,
         "genuine_called_genuine": 0, "genuine_called_suspicious": 0, "genuine_called_scam": 0}
    miss = []
    for r in rows:
        v = analyze(r["text"])["verdict"]
        c[f"{r['label']}_called_{v}"] += 1
        if (r["label"] == "scam") != (v == "scam") and not (r["label"] == "scam" and v == "suspicious"):
            miss.append({"label": r["label"], "verdict": v, "text": r["text"]})
        elif r["label"] == "genuine" and v != "genuine":
            miss.append({"label": r["label"], "verdict": v, "text": r["text"]})
    n_s = sum(r["label"] == "scam" for r in rows)
    n_g = len(rows) - n_s
    return {"n": len(rows), **c, "scam_flagged_rate": round((c["scam_called_scam"] + c["scam_called_suspicious"]) / n_s, 3),
            "scam_caught_as_scam_rate": round(c["scam_called_scam"] / n_s, 3), "genuine_clean_rate": round(c["genuine_called_genuine"] / n_g, 3),
            "genuine_false_scam_rate": round(c["genuine_called_scam"] / n_g, 3), "misses": miss}


out = {"stress": run("stress"), "stress2": run("stress2")}
(ROOT / "results" / "stress_report.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
for k, v in out.items():
    print(k, {x: v[x] for x in v if x != "misses"})
    for m in v["misses"]:
        print("   ", m["label"], "->", m["verdict"], "|", m["text"][:90])
