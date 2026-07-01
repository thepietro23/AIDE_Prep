"""
config.py
---------
All settings for the financial sentiment fine-tuning project in one place.

Project: fine-tune a small LLM (QLoRA) to classify the sentiment of a
financial tweet/headline as bearish / bullish / neutral.
"""

import os
import pathlib

# The model + dataset are already cached locally. Skip HuggingFace's network
# check on load (on a flaky/proxied network it can hang for minutes).
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

# On Windows, torch (MKL) + sklearn/datasets can load two OpenMP runtimes and
# hard-crash (exit 139). This is the standard, safe workaround.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# ---- Base model ----------------------------------------------------------
# A small instruct model so it fits a 4GB GPU. Start small (0.5B) to get the
# whole pipeline working fast; you can later try Qwen2.5-1.5B-Instruct.
# Downloaded locally (via curl/truststore) to dodge corporate-proxy HF issues.
BASE_MODEL = str(pathlib.Path(__file__).parent / "models" / "Qwen2.5-0.5B-Instruct")

# ---- Dataset -------------------------------------------------------------
DATASET = "zeroshot/twitter-financial-news-sentiment"

# The dataset stores labels as ints. Map them to words the model will say.
ID2LABEL = {0: "bearish", 1: "bullish", 2: "neutral"}
LABELS = list(ID2LABEL.values())          # ["bearish", "bullish", "neutral"]

# ---- Prompt format -------------------------------------------------------
# Same format is used for baseline, training, and evaluation (must match!).
INSTRUCTION = (
    "Classify the sentiment of this financial news/tweet as exactly one word: "
    "bearish, bullish, or neutral."
)

def build_prompt(text):
    """The user-facing part of the prompt (without the answer)."""
    return f"{INSTRUCTION}\n\nText: {text}\nSentiment:"

# ---- Paths ---------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).parent
ADAPTER_DIR = BASE_DIR / "lora_adapter"    # the trained LoRA adapter is saved here

# ---- Training hyperparameters -------------------------------------------
MAX_SEQ_LEN = 128        # tweets are short -> small length saves a lot of VRAM
BATCH_SIZE = 4           # per-device batch size (keep small for 4GB)
GRAD_ACCUM = 4           # effective batch = BATCH_SIZE * GRAD_ACCUM = 16
EPOCHS = 1               # one pass is usually enough for this task
LEARNING_RATE = 2e-4     # typical for LoRA
LORA_R = 16              # LoRA rank (size of the adapter)
LORA_ALPHA = 32          # LoRA scaling
LORA_DROPOUT = 0.05

# How many test examples to evaluate on (full test set is slow on a laptop GPU).
EVAL_SAMPLES = 300
