"""Pure-Python inference for the Kagaz Saathi notice classifier (no numpy, no scikit-learn).

Reproduces scikit-learn's TfidfVectorizer (char_wb 2-5-grams + word 1-2-grams, sublinear tf, l2 norm)
and the trained linear layer from model/train_classifier.py, so the seller runs with the standard
library only. The label only chooses wording and audit flags; it never changes a price.
"""
import json
import math
import re
from pathlib import Path

_WORD = re.compile(r"(?u)\b\w+\b")
_WS = re.compile(r"\s\s+")


class TacticModel:
    def __init__(self, path=Path(__file__).with_name("notice_model.json")):
        m = json.loads(Path(path).read_text(encoding="utf-8"))
        self.classes = m["classes"]
        self.cv, self.cidf = m["char"]["vocab"], m["char"]["idf"]
        self.wv, self.widf = m["word"]["vocab"], m["word"]["idf"]
        self.coef, self.b, self.n_char = m["coef"], m["intercept"], m["n_char"]

    @staticmethod
    def _char_wb(text, lo=2, hi=5):
        text = _WS.sub(" ", text.lower())
        for w in text.split():
            w = f" {w} "
            for n in range(lo, hi + 1):
                if len(w) < n:
                    continue
                for i in range(len(w) - n + 1):
                    yield w[i:i + n]

    @staticmethod
    def _words(text):
        toks = _WORD.findall(text.lower())
        yield from toks
        for a, b in zip(toks, toks[1:]):
            yield f"{a} {b}"

    @staticmethod
    def _tfidf(grams, vocab, idf):
        counts = {}
        for g in grams:
            j = vocab.get(g)
            if j is not None:
                counts[j] = counts.get(j, 0) + 1
        vec = {j: (1 + math.log(c)) * idf[j] for j, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {j: v / norm for j, v in vec.items()}

    def proba(self, text):
        """{label: probability} for one message."""
        if not isinstance(text, str) or not text.strip():
            return {"general": 1.0}
        feats = self._tfidf(self._char_wb(text), self.cv, self.cidf)
        words = self._tfidf(self._words(text), self.wv, self.widf)
        feats.update({self.n_char + j: v for j, v in words.items()})
        scores = [b + sum(row[j] * v for j, v in feats.items()) for row, b in zip(self.coef, self.b)]
        top = max(scores)
        exps = [math.exp(s - top) for s in scores]
        tot = sum(exps)
        return {c: e / tot for c, e in zip(self.classes, exps)}

    def predict(self, text):
        """(label, probability) for one message."""
        p = self.proba(text)
        k = max(p, key=p.get)
        return k, p[k]
