import os
import torch
import click
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def load_model(base_model, adapter_path):
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True
    )
    if adapter_path and os.path.exists(adapter_path):
        model = PeftModel.from_pretrained(model, adapter_path)
        print(f"✅ Загружен адаптер из {adapter_path}")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model if not adapter_path else adapter_path,
        trust_remote_code=True
    )
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_tokens=512):
    messages = [
        {"role": "system", "content": "Ты — AI-ассистент, обученный на знаниях бизнес-эксперта."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "assistant" in response:
        response = response.split("assistant")[-1].strip()
    return response

@click.command()
@click.option('--adapter', '-a', default='checkpoints/final', help='Путь к адаптеру LoRA')
@click.option('--model', '-m', default='Qwen/Qwen2.5-1.5B-Instruct', help='Базовая модель')
@click.option('--prompt', '-p', default=None, help='Запрос к модели')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим чата')
def infer(adapter, model, prompt, interactive):
    print("\n" + "="*60)
    print("   ГЕНЕРАЦИЯ С ИСПОЛЬЗОВАНИЕМ ОБУЧЕННОЙ МОДЕЛИ")
    print("="*60)
    
    print("\n📥 Загрузка модели...")
    model_instance, tokenizer = load_model(model, adapter)
    
    if interactive:
        print("\n💬 Интерактивный режим (введите 'exit' для выхода)\n")
        while True:
            user_input = input("🧑 Вы: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if user_input:
                response = generate_response(model_instance, tokenizer, user_input)
                print(f"🤖 AI: {response}\n")
    elif prompt:
        response = generate_response(model_instance, tokenizer, prompt)
        print(f"\n🤖 Ответ:\n{response}")
    else:
        print("❌ Укажите --prompt или --interactive")
