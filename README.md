# 🌐 Universal Dependencies Parsing with LLMs

This repository implements a new task for [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness) to evaluate Large Language Models (LLMs) on **Universal Dependencies (UD) dependency parsing**.

Given a natural-language sentence, the model generates its syntactic analysis in **CoNLL-U format**. The predicted dependency structure is evaluated against gold UD annotations using **Unlabeled Attachment Score (UAS)** and **Labeled Attachment Score (LAS)**.

The project investigates dependency-parsing performance across different **LLMs, languages, and prompting configurations**.

## 📑 Table of Contents

- [Task](#-task)
- [Models and Languages](#-models-and-languages)
- [Evaluation](#-evaluation)
- [Installation](#️-installation)
- [Usage](#-usage)
- [Repository Structure](#-repository-structure)
- [Results](#-results)
  - [Cross-Model Evaluation](#-cross-model-evaluation)
  - [Multilingual Evaluation](#-multilingual-evaluation)
  - [Task Development](#-task-development)
- [References](#-references)


## 🎯 Task

The task evaluates an LLM's ability to perform **Universal Dependencies (UD) parsing** by generating a dependency structure directly in CoNLL-U format.

For each sentence, the model receives the tokenized text and is instructed to predict the following CoNLL-U fields:

`ID  FORM  LEMMA  UPOS  XPOS  FEATS  HEAD  DEPREL`

The model is prompted using **few-shot examples** together with dependency-attachment guidelines. The generated parse is compared with the gold UD annotation.

Evaluation focuses on dependency structure using **UAS** and **LAS**. Additionally, **CoNLL-U validity** is measured to distinguish errors in dependency analysis from failures to produce the required structured format.

## 🤖 Models and Languages

The task was evaluated using several LLMs with different architectures and sizes:

- DeepSeek V4 Flash
- DeepSeek Thinking
- GLM-5.2
- Kimi K3

Experiments were conducted on multiple Universal Dependencies treebanks to compare dependency-parsing performance across languages.

## 📏 Evaluation

Model predictions are evaluated against the gold Universal Dependencies annotations using two standard dependency-parsing metrics:

- **UAS (Unlabeled Attachment Score):** the percentage of tokens assigned the correct syntactic head.
- **LAS (Labeled Attachment Score):** the percentage of tokens assigned both the correct syntactic head and dependency relation.
- **CoNLL-U validity**: A prediction is considered valid only
when it contains the expected token sequence and field structure and forms a
legal dependency tree.

## ⚙️ Installation

Clone and install [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness):

```bash
git clone https://github.com/EleutherAI/lm-evaluation-harness.git
cd lm-evaluation-harness
pip install -e .
pip install -e ".[api]"
```

Clone this task into the `lm_eval/tasks/` directory:

```bash
cd lm_eval/tasks/
git clone https://github.com/OriMoscovitz/ud_conllu_parse.git
cd ud_conllu_parse
```

### API Key

The experiments use the LLM API provided by [e-INFRA CZ](https://chat.ai.e-infra.cz/). Obtain an API key from the service and export it before running the evaluation:

```bash
export OPENAI_API_KEY="<your-api-key>"
```

The API key is used by the `local-chat-completions` backend when connecting to the e-INFRA model endpoint.

## 🚀 Usage

Run the task using `lm-evaluation-harness`:

```bash
lm-eval run \
  --model local-chat-completions \
  --model_args model=kimi-k3,base_url=https://llm.ai.e-infra.cz/v1/chat/completions,tokenizer_backend=None,num_concurrent=2,max_retries=10 \
  --apply_chat_template \
  --tasks ud_conllu_parse \
  --include_path . \
  --confirm_run_unsafe_code \
  --output_path ./results \
  --log_samples \
  --metadata='{"language":"eng"}'
```

The language is selected through the `language` metadata field. The corresponding Universal Dependencies treebank is automatically downloaded according to the mapping defined in `language_map.py`.

For example, to evaluate Czech:

```bash
--metadata='{"language":"ces"}'
```

or German:

```bash
--metadata='{"language":"deu"}'
```

## 📁 Repository Structure

```text
ud_conllu_parse/
├── data/                   # Downloaded Universal Dependencies treebanks
├── predictions/            # Model predictions generated during evaluation
├── results/                # lm-eval evaluation results
├── language_map.py         # Language-to-UD-treebank mapping
├── preprocessing.py        # CoNLL-U preprocessing
├── utils.py                # Dataset loading, prompting, validation, and evaluation
├── ud_conllu_parse.yaml    # lm-evaluation-harness task configuration
└── README.md
```

UD treebanks are downloaded automatically to `data/` when a requested language is not already available locally.

## 📊 Results

### 🧪 Task Development

Selected task-development experiments on **UD English-EWT**, conducted using the baseline model **DeepSeek-v4-flash**:

| Configuration | Valid (%) | LAS (%) | UAS (%) |
|---|---:|---:|---:|
| Initial configuration | 44.6 | 50.8 | 54.1 |
| Stable 3-shot baseline | 87.1 | 71.8 | 76.2 |
| 4-column output | 93.2 | 67.7 | 73.2 |
| 4-shot | 87.9 | 72.8 | 76.9 |
| 5-shot | 90.2 | 75.0 | 78.9 |
| 6-shot | 90.3 | 74.6 | 78.4 |
| Dependency guidance | 91.6 | 75.1 | 79.0 |
| **Relation distinctions** | **94.5** | **76.8** | **81.0** |

### 🔄 Cross-Model Evaluation

The final five-shot configuration was evaluated across multiple LLMs on **UD English-EWT**.

| Model | Valid (%) | LAS (%) | UAS (%) |
|---|---:|---:|---:|
| DeepSeek-v4-flash | 94.5 | 76.8 | 81.0 |
| DeepSeek-Thinking | 2.9 | 2.7 | 2.8 |
| GLM-5.2 | 8.4 | 8.3 | 8.3 |
| **Kimi-K3** | **96.9** | **82.9** | **88.1** |

Kimi-K3 achieved the strongest performance, reaching **82.9% LAS** and **88.1% UAS** with a **96.9% validity rate**.

### 🔤 Multilingual Evaluation

Using Kimi-K3, the same five-shot configuration and language-independent dependency guidance were evaluated across ten UD languages.

| Language | Valid (%) | LAS (%) | UAS (%) |
|---|---:|---:|---:|
| English | 96.3 | 82.6 | 87.9 |
| Dutch | 91.1 | 75.8 | 82.8 |
| German | 95.5 | 77.7 | 83.1 |
| Czech | 81.4 | 80.2 | 86.3 |
| Finnish | 95.2 | 72.6 | 79.8 |
| Turkish | 97.6 | 63.6 | 82.8 |
| Basque | 98.4 | 68.9 | 77.0 |
| Georgian | 78.4 | 72.0 | 78.8 |
| Hungarian | 86.2 | 75.8 | 83.4 |
| Maltese | 92.1 | 74.5 | 81.3 |

These experiments led to the final configuration: an **eight-field CoNLL-U representation**, **five-shot prompting**, and explicit guidance for commonly confused dependency relations.

## 📚 References

- [Universal Dependencies](https://universaldependencies.org/) - Universal framework and treebanks used for dependency parsing.
- [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) - Framework used to implement and evaluate the task.
- Nivre, J. et al. (2020). [Universal Dependencies v2: An Evergrowing Multilingual Treebank Collection](https://aclanthology.org/2020.lrec-1.497/).
- Biderman, S. et al. (2024). [Lessons from the Trenches on Reproducible Evaluation of Language Models](https://arxiv.org/pdf/2405.14782).
