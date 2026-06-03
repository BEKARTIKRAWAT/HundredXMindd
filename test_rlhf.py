import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
base_model = "unsloth/llama-3.2-1b-Instruct-bnb-4bit"
adapter_path = "dpo_adapter"
# Load tokenizer and base model (CPU)
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32, device_map="cpu")
model = PeftModel.from_pretrained(model, adapter_path)
def ask(prompt: str) -> str:
    inputs = tokenizer(f"User: {prompt}\nAssistant:", return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=256)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Assistant:" in answer:
        answer = answer.split("Assistant:")[-1].strip()
    return answer
print(ask("What is the capital of France?"))
