import json


def conllu_to_records(input_path):
    COL_SEP = "^"
    records = []

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_text = None
    current_tokens = []

    def flush():
        nonlocal current_text, current_tokens

        if current_text is not None and current_tokens:
            records.append({
                "text": current_text,
                "label": "\n".join(current_tokens),
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

            if len(cols) != 10:
                continue

            tok_id = cols[0]

            if "-" in tok_id or "." in tok_id:
                continue

            eight_cols = [
                c.replace(COL_SEP, "＾")
                for c in cols[:8]
            ]

            current_tokens.append(
                COL_SEP.join(eight_cols)
            )

    flush()

    return records

def conllu_files_to_records(input_files):
    """
    Convert multiple CoNLL-U files into one combined list of records.
    """

    records = []

    for input_file in input_files:
        records.extend(
            conllu_to_records(input_file)
        )

    return records

def conllu_to_jsonl(input_path, output_path=None):
    records = conllu_to_records(input_path)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for record in records:
                out.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )
    else:
        for record in records:
            print(json.dumps(record, ensure_ascii=False))
