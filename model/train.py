"""Train and test the Kagaz Saathi notice classifier, then export it for pure-Python inference.

TF-IDF (char_wb 2-5 + word 1-2) + multinomial logistic regression trained by SGD, epoch by epoch.
Settings are chosen on data/dev.jsonl only; data/fresh_test.jsonl is reported once, never used for selection.

    python model/train.py
"""
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import FeatureUnion

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data"
EXPORT = ROOT / "kagaz" / "notice_model.json"
REPORT = ROOT / "results" / "model_report.json"

SCAM = ["digital_arrest", "kyc_block", "otp_theft", "prize_lottery", "job_fraud", "parcel_customs", "bill_cutoff", "refund_fraud",
        "investment_loan", "impersonation_advance"]


def load(name):
    rows = [json.loads(l) for l in (DATA / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r["text"] for r in rows], [r["label"] for r in rows]


def main():
    Xtr, ytr = load("train")
    Xdev, ydev = load("dev")
    Xte, yte = load("fresh_test")
    classes = sorted(set(ytr))
    feats = FeatureUnion([
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True, lowercase=True, max_features=14000)),
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True,
                                 token_pattern=r"(?u)\b\w+\b", max_features=7000)),
    ])
    Ttr, Tdev, Tte = feats.fit_transform(Xtr), None, None
    Tdev, Tte = feats.transform(Xdev), feats.transform(Xte)
    ya = np.array(ytr)
    best = None
    for alpha in (1e-5, 3e-5, 1e-4):
        clf = SGDClassifier(loss="log_loss", alpha=alpha, learning_rate="optimal", random_state=0)
        rng = np.random.RandomState(0)
        hist = []
        for ep in range(1, 31):
            o = rng.permutation(Ttr.shape[0])
            clf.partial_fit(Ttr[o], ya[o], classes=classes)
            hist.append({"epoch": ep, "train_acc": round(accuracy_score(ytr, clf.predict(Ttr)), 4),
                         "dev_acc": round(accuracy_score(ydev, clf.predict(Tdev)), 4)})
            if best is None or hist[-1]["dev_acc"] > best[0] + 1e-9:
                best = (hist[-1]["dev_acc"], ep, alpha, clf.coef_.copy(), clf.intercept_.copy(), list(hist))
        print(f"alpha {alpha:g}: best dev so far {best[0]:.4f} (epoch {best[1]}, alpha {best[2]:g})")
    _, ep, alpha, coef, icpt, hist = best
    clf.coef_, clf.intercept_ = coef, icpt
    pred = clf.predict(Tte)
    acc = accuracy_score(yte, pred)
    verdict = lambda l: "scam" if l in SCAM else "genuine"
    vacc = float(np.mean([verdict(a) == verdict(b) for a, b in zip(yte, pred)]))
    report = {"classes": classes, "train_size": len(Xtr), "dev_size": len(Xdev), "test_size": len(Xte), "alpha": alpha, "best_epoch": ep,
              "history": hist, "dev_accuracy": round(accuracy_score(ydev, clf.predict(Tdev)), 4),
              "test_accuracy": round(acc, 4), "test_scam_vs_genuine_accuracy": round(vacc, 4),
              "per_class": classification_report(yte, pred, labels=classes, output_dict=True, zero_division=0),
              "confusion": confusion_matrix(yte, pred, labels=classes).tolist(),
              "errors": [{"text": t, "true": a, "pred": b} for t, a, b in zip(Xte, yte, pred) if a != b]}
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    ch, wd = feats.transformer_list[0][1], feats.transformer_list[1][1]
    EXPORT.write_text(json.dumps({
        "classes": classes, "n_char": len(ch.vocabulary_),
        "char": {"vocab": {k: int(v) for k, v in ch.vocabulary_.items()}, "idf": [round(float(x), 5) for x in ch.idf_], "ngram": [2, 5]},
        "word": {"vocab": {k: int(v) for k, v in wd.vocabulary_.items()}, "idf": [round(float(x), 5) for x in wd.idf_], "ngram": [1, 2]},
        "coef": [[round(float(x), 5) for x in r] for r in clf.coef_], "intercept": [round(float(x), 5) for x in clf.intercept_]},
        separators=(",", ":")), encoding="utf-8")
    print(f"dev {report['dev_accuracy']:.4f}  FRESH TEST {acc:.4f} ({len(Xte)} msgs)  scam-vs-genuine {vacc:.4f}  -> {EXPORT.name}")
    for e in report["errors"]:
        print("  miss:", e["true"], "->", e["pred"], "|", e["text"][:80])


if __name__ == "__main__":
    main()
