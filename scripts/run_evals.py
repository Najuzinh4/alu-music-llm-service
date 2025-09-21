from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.services.llm import classificar_texto


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def evaluate(dataset_path: Path) -> dict:
    data = load_jsonl(dataset_path)
    y_true = []
    y_pred = []

    for row in data:
        texto = row["texto"]
        y_true.append(row["categoria"])  # ground truth
        pred = classificar_texto(texto)
        y_pred.append(pred["categoria"])

    labels = sorted(list({*y_true, *y_pred}))
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    return {
        "labels": labels,
        "accuracy": acc,
        "classification_report": report,
        "confusion_matrix": cm,
        "n_samples": len(y_true),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/evals.jsonl", help="JSONL com campos: texto, categoria")
    parser.add_argument("--out", required=True, help="Caminho do relatório JSON de saída")
    args = parser.parse_args(argv)

    dataset_path = Path(args.data)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    result = evaluate(dataset_path)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": int(time.time()),
        "dataset": str(dataset_path),
        **result,
    }
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved evals to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

