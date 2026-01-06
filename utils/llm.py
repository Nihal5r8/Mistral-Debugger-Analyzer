from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Load model once at startup
model_id = r"C:\Users\NIHAL 2\PycharmProjects\MajorProject\mistral_7b_instruct_v2_4bit"

print("[INFO] Loading Mistral 7B Instruct (4-bit)...")

bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=bnb_config,
    dtype=torch.float16
)

def generate_response(prompt, max_new_tokens=1024):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=max_new_tokens)
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text
