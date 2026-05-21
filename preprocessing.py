from pathlib import Path
from conllu import parse_incr
import json
import sys


def conllu_to_json(conllu_path: Path, output_path: Path):
    sentences = []

    with conllu_path.open("r", encoding="utf-8") as f:
        for tokenlist in parse_incr(f):
            sentences.append({
                "sent_id": tokenlist.metadata.get("sent_id"),
                "text": tokenlist.metadata.get("text"),
                "tokens": [
                    {
                        "id": token["id"],
                        "form": token["form"],
                        "lemma": token.get("lemma"),
                        "upos": token.get("upos"),
                        "xpos": token.get("xpos"),
                        "head": token.get("head"),
                        "deprel": token.get("deprel"),
                        "feats": token.get("feats"),
                        "deps": token.get("deps"),
                        "misc": token.get("misc"),
                    }
                    for token in tokenlist
                ]
            })

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2, default=str)


def create_yaml_file(converted_folder: Path):
    json_files = list(converted_folder.glob("*.json"))

    split_map = {
        "train": None,
        "test": None,
        "validation": None,
    }

    for json_file in json_files:
        name = json_file.stem.lower()

        if "train" in name:
            split_map["train"] = json_file.resolve()
        elif "test" in name:
            split_map["test"] = json_file.resolve()
        elif "dev" in name or "valid" in name or "validation" in name:
            split_map["validation"] = json_file.resolve()

    yaml_lines = [
        "dataset_path: json",
        "dataset_kwargs:",
        "  data_files:",
    ]

    for split in ["train", "test", "validation"]:
        if split_map[split] is not None:
            yaml_lines.append(f"    {split}: {split_map[split]}")

    yaml_content = "\n".join(yaml_lines) + "\n"

    yaml_path = converted_folder / f"{converted_folder.name}.yaml"
    with yaml_path.open("w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"Created YAML: {yaml_path}")


def convert_all_folders(base_dir: str | Path):
    base_dir = Path(base_dir)

    for folder in base_dir.iterdir():
        if folder.name == "UD_Basque-BDT":
            break

        if folder.is_dir():
            converted_folder = folder.parent / f"{folder.name}_converted"
            converted_folder.mkdir(exist_ok=True)

            for conllu_file in folder.glob("*.conllu"):
                output_file = converted_folder / (conllu_file.stem + ".json")
                conllu_to_json(conllu_file, output_file)
                print(f"Converted: {conllu_file} → {output_file}")

            create_yaml_file(converted_folder)


def conllu_to_jsonl(input_path, output_path=None):
    """Convert a CoNLL-U file to JSONL with ^ -delimited 8-column labels.

    Changes vs the original:
    - Multi-word token lines (ID like "19-20") are skipped — they are surface
      contractions, not dependency nodes, and confuse the model.
    - Empty-node lines (ID like "8.1") are skipped for the same reason.
    - Columns are joined with "^" instead of " " so the model can split them
      unambiguously (FEATS uses "|" and "="; no UD field ever contains "^",
      except the ^_^ emoticon which is handled by escaping below).
    - DEPS (col 9) and MISC (col 10) are dropped — they are not needed for
      UAS/LAS scoring and only waste context tokens.
    """
    COL_SEP = "^"

    records = []

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_text = None
    current_tokens = []

    def flush():
        nonlocal current_text, current_tokens
        if current_text is not None and current_tokens:
            label = "\n".join(current_tokens)
            records.append({
                "text": current_text,
                "label": label,
            })
        current_text = None
        current_tokens = []

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")

        if stripped.startswith("# text = "):
            current_text = stripped[len("# text = "):]

        elif stripped.startswith("#"):
            continue

        elif stripped == "":
            flush()

        else:
            cols = stripped.split("\t")
            if len(cols) < 8:
                continue  # malformed line

            tok_id = cols[0]

            # Skip multi-word tokens (e.g. "19-20") and empty nodes (e.g. "8.1")
            if "-" in tok_id or "." in tok_id:
                continue

            # Keep only the 8 columns needed: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL
            # Replace any literal "^" inside field values with the fullwidth
            # lookalike "＾" (U+FF3E) so that plain split("^") is always safe.
            # This affects only the ^_^ emoticon (4 sentences in EWT train).
            eight_cols = [c.replace(COL_SEP, "＾") for c in cols[:8]]
            current_tokens.append(COL_SEP.join(eight_cols))

    flush()

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for record in records:
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        for record in records:
            print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py input.conllu [output.jsonl]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    conllu_to_jsonl(input_file, output_file)
