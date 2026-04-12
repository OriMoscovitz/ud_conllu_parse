from __future__ import annotations

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

from datasets import Dataset


DEFAULT_TRAIN_FILE = "./data/UD_English-EWT/en_ewt-ud-train_conv.jsonl"
DEFAULT_DEV_FILE = "./data/UD_English-EWT/en_ewt-ud-dev_conv.jsonl"
DEFAULT_TEST_FILE = "./data/UD_English-EWT/en_ewt-ud-test_conv.jsonl"

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("predictions", exist_ok=True)
PRED_FILE = f"predictions/preds_{TIMESTAMP}.jsonl"


# print(f"------------- default train file set: {DEFAULT_TRAIN_FILE} -------------")


def _read_jsonl(path: str | Path) -> list[dict[str, str]]:
    # print(f"------------- starting to read from path: {path} -------------")
    # print(f"------------- current pwd is: {os.getcwd()} -------------")

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    records: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "text" not in obj or "label" not in obj:
                raise ValueError(
                    f"Expected keys 'text' and 'label' in {path} line {line_no}, got: {list(obj.keys())}"
                )
            records.append({"text": str(obj["text"]), "label": str(obj["label"])})
    return records


def load_local_jsonl_splits(
    train_file: str = DEFAULT_TRAIN_FILE,
    dev_file: str = DEFAULT_DEV_FILE,
    test_file: str = DEFAULT_TEST_FILE,
    **_: Any,
) -> dict[str, Dataset]:
    """Load local JSONL files into lm-eval-harness splits.

    The harness passes YAML `metadata` and `dataset_kwargs` into `custom_dataset`.
    This function intentionally accepts arbitrary keyword args so paths can be
    overridden via `--metadata` without breaking the call signature.
    """
    return {
        "train": Dataset.from_list(_read_jsonl(train_file)),
        "dev": Dataset.from_list(_read_jsonl(dev_file)),
        "test": Dataset.from_list(_read_jsonl(test_file)),
    }


def doc_to_text(doc: dict[str, str]) -> str:
    sentence = doc["text"].strip()
    tokens = sentence.split()
    return f"Sentence: {sentence}\nTokens: {len(tokens)}\nCoNLL-U:\n"


def doc_to_target(doc: dict[str, str]) -> str:
    return doc["label"].strip()


def _strip_wrappers(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:conllu|txt)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_conllu(text: str) -> dict[int, tuple[str, str]]:
    """Parse CoNLL-U-ish token lines into {id: (head, deprel)}.

    The gold data is whitespace-separated rather than tab-separated, so we split
    on arbitrary whitespace with maxsplit=9 to preserve the 10 CoNLL-U columns.
    Multiword tokens and empty nodes are ignored for attachment scoring.
    """
    parsed: dict[int, tuple[str, str]] = {}
    for raw_line in _strip_wrappers(text).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        cols = re.split(r"\s+", line, maxsplit=9)
        if len(cols) < 8:
            continue

        tok_id = cols[0]
        if "-" in tok_id or "." in tok_id:
            continue

        try:
            idx = int(tok_id)
        except ValueError:
            continue

        head = cols[6]
        deprel = cols[7]
        parsed[idx] = (head, deprel)

    return parsed


def _attachment_scores(gold: str, pred: str) -> tuple[float, float]:
    gold_map = _parse_conllu(gold)
    pred_map = _parse_conllu(pred)

    if not gold_map:
        return 0.0, 0.0

    total = len(gold_map)
    uas_hits = 0
    las_hits = 0

    for idx, (gold_head, gold_rel) in gold_map.items():
        pred_head, pred_rel = pred_map.get(idx, (None, None))
        if pred_head == gold_head:
            uas_hits += 1
            if pred_rel == gold_rel:
                las_hits += 1

    return uas_hits / total, las_hits / total


def process_results(doc: dict[str, str], results: list[str]) -> dict[str, float]:
    pred = results[0] if results else ""
    uas, las = _attachment_scores(doc["label"], pred)

    record = {
        "text": doc["text"],
        "gold": doc["label"],
        "prediction": pred,
        "uas": uas,
        "las": las,
    }

    with open(PRED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {"uas": uas, "las": las}
