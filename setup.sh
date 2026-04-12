#!/usr/bin/env bash

set -e

echo "Creating virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Cloning UD parsing repository..."
git clone https://github.com/OriMoscovitz/ud_conllu_parse.git

echo "Installing task dependencies..."
pip install -r ud_conllu_parse/requirements.txt

echo "Cloning lm-evaluation-harness..."
git clone https://github.com/EleutherAI/lm-evaluation-harness.git

echo "Entering lm-evaluation-harness directory..."
cd lm-evaluation-harness

echo "Copying task into harness..."
cp -r ../ud_conllu_parse lm_eval/tasks/

echo "Installing evaluation harness..."
pip install -e ".[dev]"

echo "Setup complete!"
echo ""
echo "To run evaluation:"
echo ""
echo "lm-eval run \\"
echo "  --model hf \\"
echo "  --model_args pretrained=Qwen/Qwen2.5-1.5B-Instruct,device_map=cuda \\"
echo "  --tasks ud_conllu_parse \\"
echo "  --include_path . \\"
echo "  --confirm_run_unsafe_code \\"
echo "  --output_path ./results"