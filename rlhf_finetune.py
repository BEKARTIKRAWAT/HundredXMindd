import json
import torch
from unsloth import FastLanguageModel
from trl import DPOTrainer, DPOConfig
from datasets import Dataset
# Load model in 4-bit (CPU mode)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3.2-1b-Instruct-bnb-4bit",
    max_seq_length = 512,
    load_in_4bit = True,
    device_map = "cpu",  # use CPU (slow but works)
    dtype = torch.float32,
)
# Add LoRA adapter
model = FastLanguageModel.get_peft_model(
    model,
    r = 8,
    lora_alpha = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_dropout = 0,
    bias = "none",
)
# Load preference dataset
with open("data/preference_data.json", "r") as f:
    data = json.load(f)
dataset = Dataset.from_list([
    {"prompt": item["prompt"], "chosen": item["chosen"], "rejected": item["rejected"]}
    for item in data
])
# Format for DPO
def format_dpo(example):
    return {
        "prompt": f"User: {example['prompt']}\nAssistant:",
        "chosen": example["chosen"],
        "rejected": example["rejected"]
    }
dataset = dataset.map(format_dpo)
# Train
config = DPOConfig(
    output_dir = "dpo_output",
    per_device_train_batch_size = 1,
    gradient_accumulation_steps = 4,
    num_train_epochs = 5,
    learning_rate = 5e-6,
    logging_steps = 10,
    save_steps = 50,
    max_length = 512,
    remove_unused_columns = False,
)
trainer = DPOTrainer(
    model = model,
    ref_model = None,
    args = config,
    train_dataset = dataset,
    tokenizer = tokenizer,
)
trainer.train()
# Save model
model.save_pretrained("dpo_finetuned_model")
tokenizer.save_pretrained("dpo_finetuned_model")
print("✅ RLHF fine‑tuning complete!")
