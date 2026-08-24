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


# correcting the parsing of the label, so it will treat punctuation as a token as well
def doc_to_text(doc: dict[str, str]) -> str:
    sentence = doc["text"].strip()

    forms = []
    for line in doc["label"].splitlines():
        cols = line.split("^")
        if len(cols) >= 2:
            forms.append(cols[1])

    token_list = " | ".join(forms)

    return (
        f"Sentence: {sentence}\n"
        f"Tokens ({len(forms)}): {token_list}\n"
        f"CoNLL-U:\n"
    )

# def doc_to_target(doc: dict[str, str]) -> str:
#     return doc["label"].strip()

# changed to focus on the columns ID^FORM^HEAD^DEPREL only
def doc_to_target(doc: dict[str, str]) -> str:
    rows = []

    for raw_line in doc["label"].splitlines():
        cols = raw_line.split("^")

        if len(cols) != 8:
            continue

        token_id = cols[0]
        form = cols[1]
        head = cols[6]
        deprel = cols[7]

        rows.append(f"{token_id}^{form}^{head}^{deprel}")

    return "\n".join(rows)


def _strip_wrappers(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:conllu|txt)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


UD_UPOS = {
    "ADJ",
    "ADP",
    "ADV",
    "AUX",
    "CCONJ",
    "DET",
    "INTJ",
    "NOUN",
    "NUM",
    "PART",
    "PRON",
    "PROPN",
    "PUNCT",
    "SCONJ",
    "SYM",
    "VERB",
    "X",
}

UD_DEPRELS = {
    "acl",
    "advcl",
    "advmod",
    "amod",
    "appos",
    "aux",
    "case",
    "cc",
    "ccomp",
    "clf",
    "compound",
    "conj",
    "cop",
    "csubj",
    "dep",
    "det",
    "discourse",
    "dislocated",
    "expl",
    "fixed",
    "flat",
    "goeswith",
    "iobj",
    "list",
    "mark",
    "nmod",
    "nsubj",
    "nummod",
    "obj",
    "obl",
    "orphan",
    "parataxis",
    "punct",
    "reparandum",
    "root",
    "vocative",
    "xcomp",
}

_DEPREL_RE = re.compile(r"^[a-z]+(?::[a-z]+)?$")
_FEAT_RE = re.compile(
    r"^[A-Za-z][A-Za-z0-9]*(?:\[[A-Za-z0-9]+\])?"
    r"=[^|=\s]+(?:,[^|=\s]+)*$"
)


def _expected_word_ids(gold: str) -> list[int]:
    """Return the integer word IDs expected by the evaluation example."""
    ids: list[int] = []

    for raw_line in gold.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        cols = line.split("^")
        if not cols:
            continue

        token_id = cols[0]

        # The current task evaluates ordinary word rows only.
        if "-" in token_id or "." in token_id:
            continue

        try:
            ids.append(int(token_id))
        except ValueError:
            continue

    return ids


def _valid_feats(value: str) -> bool:
    """Check basic CoNLL-U FEATS field syntax."""
    if value == "_":
        return True

    parts = value.split("|")

    if not parts or len(parts) != len(set(parts)):
        return False

    return all(_FEAT_RE.fullmatch(part) is not None for part in parts)


def _has_valid_dependency_tree(
    ids: list[int],
    heads: dict[int, int],
    deprels: dict[int, str],
) -> bool:
    """Check that HEAD/DEPREL define one rooted, acyclic dependency tree."""
    id_set = set(ids)

    roots = [idx for idx in ids if heads[idx] == 0]

    if len(roots) != 1:
        return False

    root = roots[0]

    if deprels[root] != "root":
        return False

    for idx in ids:
        head = heads[idx]
        relation = deprels[idx]

        if idx == root:
            if head != 0 or relation != "root":
                return False
        else:
            if head == 0:
                return False
            if relation == "root":
                return False

        if head == idx:
            return False

        if head != 0 and head not in id_set:
            return False

    # Every token must eventually reach the single root.
    for start in ids:
        seen: set[int] = set()
        current = start

        while current != 0:
            if current in seen:
                return False

            seen.add(current)

            if current not in heads:
                return False

            current = heads[current]

    return True


def is_valid_conllu_prediction(gold: str, prediction: str) -> bool:
    """Validate a generated dependency parse.

    The task generates an 4-column '^'-delimited projection of basic
    CoNLL-U:
        ID^FORM^HEAD^DEPREL
        # before: ID^FORM^LEMMA^UPOS^XPOS^FEATS^HEAD^DEPREL

    DEPS and MISC are omitted by design and can be reconstructed as '_'.

    This validates format/structural correctness only. Dependency agreement
    with the gold HEAD/DEPREL values is intentionally not checked.
    """
    try:
        if not isinstance(prediction, str):
            return False

        text = prediction.strip()

        if not text:
            return False

        # Wrappers or prose are not part of the requested output format.
        if "```" in text:
            return False

        lines = text.splitlines()

        # The task explicitly requests one uninterrupted block of token rows.
        if not lines or any(not line.strip() for line in lines):
            return False

        expected_ids = _expected_word_ids(gold)

        if not expected_ids:
            return False

        ids: list[int] = []
        heads: dict[int, int] = {}
        deprels: dict[int, str] = {}

        for raw_line in lines:
            # Do not silently normalize explanatory prose or comments.
            if raw_line.lstrip().startswith("#"):
                return False

            cols = raw_line.split("^")

            if len(cols) != 4:
                return False

            token_id, form, head, deprel = cols



            # # The generated task representation has exactly eight columns.
            # if len(cols) != 8:
            #     return False

            if any(col == "" for col in cols):
                return False

            # Tabs would indicate accidental canonical/mixed formatting.
            if any("\t" in col for col in cols):
                return False

            # (
            #     token_id,
            #     form,
            #     lemma,
            #     upos,
            #     xpos,
            #     feats,
            #     head,
            #     deprel,
            # ) = cols

            # In the task representation all rows are ordinary word rows.
            if not token_id.isdigit():
                return False

            idx = int(token_id)

            if idx <= 0:
                return False

            ids.append(idx)

            # # CoNLL-U fields other than FORM/LEMMA/MISC may not contain spaces.
            # for value in (token_id, upos, xpos, feats, head, deprel):
            #     if any(char.isspace() for char in value):
            #         return False

            for value in (token_id, head, deprel):
                if any(char.isspace() for char in value):
                    return False

            # FORM and LEMMA still may not contain tabs/newlines or be empty.
            # if not form or not lemma:
            #     return False

            if not form:
                return False

            # # Basic UD word rows require UPOS, HEAD and DEPREL.
            # if upos == "_" or upos not in UD_UPOS:
            #     return False

            if head == "_" or not head.isdigit():
                return False

            head_id = int(head)

            if head_id < 0:
                return False

            if deprel == "_" or not _DEPREL_RE.fullmatch(deprel):
                return False

            base_deprel = deprel.split(":", 1)[0]

            if base_deprel not in UD_DEPRELS:
                return False

            # if not _valid_feats(feats):
            #     return False

            heads[idx] = head_id
            deprels[idx] = deprel

        # IDs must match the sentence that was actually requested.
        # This detects missing, duplicated, added or reordered token rows
        # without checking dependency accuracy.
        if ids != expected_ids:
            return False

        if len(ids) != len(set(ids)):
            return False

        if not _has_valid_dependency_tree(ids, heads, deprels):
            return False

        return True

    except Exception:
        # Validation errors must never abort lm-eval.
        return False


def sum_metric(items: list[float]) -> int:
    """Aggregation used for conllu_invalid_count."""
    return int(sum(items))


def _parse_conllu(text: str) -> dict[int, tuple[str, str]]:
    """Parse ^-delimited token lines into {id: (head, deprel)}."""

    parsed: dict[int, tuple[str, str]] = {}

    for raw_line in _strip_wrappers(text).splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        cols = line.split("^")

        if len(cols) != 4:
            continue

        tok_id = cols[0]

        if "-" in tok_id or "." in tok_id:
            continue

        try:
            idx = int(tok_id)
        except ValueError:
            continue

        head = cols[2]
        deprel = cols[3]
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

    # for 8 columns
    # uas, las = _attachment_scores(doc["label"], pred)

    # fixed to fit 4 columns
    uas, las = _attachment_scores(doc_to_target(doc), pred)

    is_valid = is_valid_conllu_prediction(doc["label"], pred)

    invalid = int(not is_valid)
    valid = int(is_valid)

    record = {
        "text": doc["text"],
        # "gold": doc["label"],
        "gold": doc_to_target(doc),
        "prediction": pred,
        "uas": uas,
        "las": las,
        "conllu_valid": valid,
    }

    with open(PRED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "uas": uas,
        "las": las,
        # "conllu_invalid_rate": invalid,
        "conllu_valid_rate": valid,
        # "conllu_invalid_count": invalid,
    }
