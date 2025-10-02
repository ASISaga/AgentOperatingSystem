import os, argparse, json
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--legend", required=True)
    ap.add_argument("--dataset_path", required=True)
    return ap.parse_args()

def main():
    args = parse_args()
    tok = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(args.base_model)
    lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["q_proj","v_proj"])
    model = get_peft_model(model, lora)

    ds = load_dataset("json", data_files=args.dataset_path)["train"]
    def tokenize(batch): return tok(batch["text"], truncation=True, padding="max_length", max_length=1024)
    ds = ds.map(tokenize, batched=True)

    targs = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=50,
        save_steps=500
    )
    trainer = Trainer(model=model, args=targs, train_dataset=ds)
    trainer.train()
    model.save_pretrained(args.output_dir)
    tok.save_pretrained(args.output_dir)
    with open(os.path.join(args.output_dir, "legend.json"), "w") as f:
        json.dump({"legend": args.legend}, f)

if __name__ == "__main__":
    main()
