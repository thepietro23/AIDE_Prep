"""
train.py
--------
FINE-TUNING Step 4: QLoRA fine-tuning of the base model on financial sentiment.

QLoRA here:
  - load the base model in 4-bit       (the "Q" -> bitsandbytes)
  - attach LoRA adapters, train ONLY those  (the "LoRA" -> peft)

NOTE (Windows): we build + tokenize the data FIRST, using a plain PyTorch
Dataset (NOT datasets' pyarrow `.map`), because pyarrow ops crash once torch's
threading is initialized. This sidesteps that crash entirely.
"""

import config   # FIRST: sets HF offline env before anything loads
from prepare_data import build_datasets


def main():
    # 1. Build the text examples BEFORE importing torch ---------------------
    train_records, _ = build_datasets()
    texts = [r["sft_text"] for r in train_records]
    print(f"Training examples: {len(texts)}")

    # 2. Now import torch + the training stack -----------------------------
    import torch
    from torch.utils.data import Dataset
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig, Trainer, TrainingArguments,
                              DataCollatorForLanguageModeling)
    from peft import (LoraConfig, get_peft_model,
                      prepare_model_for_kbit_training)

    tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 3. Pre-tokenize into a plain PyTorch Dataset (no pyarrow .map) --------
    class TextDataset(Dataset):
        def __init__(self, texts):
            self.items = [tokenizer(t, truncation=True,
                                    max_length=config.MAX_SEQ_LEN) for t in texts]
        def __len__(self):
            return len(self.items)
        def __getitem__(self, i):
            return self.items[i]

    train_ds = TextDataset(texts)

    # 4. Load base model in 4-bit (the "Q" in QLoRA) -----------------------
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        config.BASE_MODEL, quantization_config=bnb, device_map="cuda"
    )
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False

    # 5. Attach LoRA adapters (only these are trained) ---------------------
    lora = LoraConfig(
        r=config.LORA_R, lora_alpha=config.LORA_ALPHA,
        lora_dropout=config.LORA_DROPOUT, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()      # shows how few params we train

    # 6. Train with a plain Trainer (DataLoader -> no pyarrow) -------------
    collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
    args = TrainingArguments(
        output_dir=str(config.ADAPTER_DIR / "_checkpoints"),
        per_device_train_batch_size=config.BATCH_SIZE,
        gradient_accumulation_steps=config.GRAD_ACCUM,
        num_train_epochs=config.EPOCHS,
        learning_rate=config.LEARNING_RATE,
        fp16=True,
        logging_steps=20,
        save_strategy="no",
        report_to="none",
        optim="paged_adamw_8bit",
    )
    trainer = Trainer(model=model, args=args,
                      train_dataset=train_ds, data_collator=collator)
    trainer.train()

    # 7. Save just the LoRA adapter (a few MB) -----------------------------
    model.save_pretrained(str(config.ADAPTER_DIR))
    tokenizer.save_pretrained(str(config.ADAPTER_DIR))
    print(f"\nSaved LoRA adapter to: {config.ADAPTER_DIR}")


if __name__ == "__main__":
    main()
