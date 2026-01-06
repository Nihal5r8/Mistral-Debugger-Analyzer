from model_loader import load_model
tokenizer, model = load_model("C:\\Users\\ADMIN PC\\PycharmProjects\\MajorProject\\mistral_7b_instruct_v2_4bit")

prompt =  "i want a code in python to print prime numbers using the sieve of erasthanoses"

inputs = tokenizer(prompt, return_tensors="pt").to(next(model.parameters()).device)
outputs = model.generate(**inputs, max_new_tokens=128)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
