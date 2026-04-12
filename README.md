# UD CoNLL-U parsing task for lm-eval-harness

This task adds a generative `lm-eval-harness` benchmark that:

- loads local `train`, `dev`, and `test` JSONL files,
- uses the first 3 examples from `train` as few-shot exemplars,
- prompts the model to convert each sentence into CoNLL-U,
- scores the generated parse against gold CoNLL-U with **UAS** and **LAS**.

# UD CoNLL-U Parse — Evaluation Guide

## Setup

### 1. Create and Activate a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / Mac
# .venv\Scripts\activate   # Windows
```

### 2. Clone the UD Parsing Task Repository

```bash
git clone https://github.com/OriMoscovitz/ud_conllu_parse.git
```

### 3. Install Task Dependencies

```bash
pip install -r ud_conllu_parse/requirements.txt
```

### 4. Clone the Evaluation Harness

```bash
git clone https://github.com/EleutherAI/lm-evaluation-harness.git
cd lm-evaluation-harness
```

### 5. Copy the Task into the Harness

```bash
cp -r ../ud_conllu_parse lm_eval/tasks/
```

### 6. Install the Evaluation Harness

```bash
pip install -e ".[dev]"
```

---

[//]: # (### Option 2 — Automatic Setup &#40;Still being tested&#41;)

[//]: # ()
[//]: # (Follow steps 1 and 2 as mentioned above and then run:)

[//]: # ()
[//]: # (```bash)

[//]: # (chmod +x ud_conllu_parse/setup.sh)

[//]: # (.ud_conllu_parse/setup.sh)

[//]: # (```)

---

## Usage

Navigate to the task directory:

```bash
cd ./lm_eval/tasks/ud_conllu_parse/
```

Run evaluation with the `Qwen2.5-1.5B-Instruct` model:

```bash
lm-eval run \
  --model hf \
  --model_args pretrained=Qwen/Qwen2.5-1.5B-Instruct,device_map=cuda \
  --tasks ud_conllu_parse \
  --include_path . \
  --confirm_run_unsafe_code \
  --output_path ./results
```

## Output

Results will be saved to:

```bash
./results
```

## Expected data format

Each line in every JSONL file must be a JSON object with:

- `text`: the raw sentence
- `label`: the gold CoNLL-U parse as a newline-separated string

Example:

```json
{"text": "And he earned 112 points in 1971-1972.", "label": "1 And and CCONJ CC _ 3 cc 3:cc _\n2 he he PRON PRP Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs 3 nsubj 3:nsubj _\n..."}
```

## Files

- `ud_conllu_parse.yaml`: task definition
- `utils.py`: local dataset loader, prompt helpers, and LAS/UAS scorer
- `run_ud_conllu_eval.sh`: example runner

## Running

```bash
lm-eval validate --tasks ud_conllu_parse --include_path ./ud_conllu_lm_eval_task

lm-eval run \
  --model hf \
  --model_args pretrained=gpt2 \
  --tasks ud_conllu_parse \
  --include_path ./ud_conllu_lm_eval_task \
  --confirm_run_unsafe_code \
  --log_samples \
  --output_path ./results/ud_conllu_parse
```

## Overriding data paths

The YAML already points to the uploaded files in `/mnt/data`, but you can override them:

```bash
lm-eval run \
  --model hf \
  --model_args pretrained=gpt2 \
  --tasks ud_conllu_parse \
  --include_path ./ud_conllu_lm_eval_task \
  --confirm_run_unsafe_code \
  --metadata '{
    "train_file": "/path/to/train.jsonl",
    "dev_file": "/path/to/dev.jsonl",
    "test_file": "/path/to/test.jsonl"
  }'
```

## Notes

- The scorer ignores CoNLL-U comment lines, multiword token rows like `3-4`, and empty nodes like `5.1`.
- `UAS` checks whether `HEAD` matches.
- `LAS` checks whether both `HEAD` and `DEPREL` match.
- Missing or malformed prediction lines count as incorrect attachments.
