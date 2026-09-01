import os
import torch
import click
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset
from .utils import load_jsonl

DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

def setup_quantization():
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

def create_lora_config(r=16):
    return LoraConfig(
        r=r,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

def prepare_dataset(data_path, tokenizer):
    raw_data = load_jsonl(data_path)
    if not raw_data:
        raise ValueError(f"Файл {data_path} пуст или не существует")
    
    formatted = []
    for item in raw_data:
        messages = item.get("messages", [])
        if messages:
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            formatted.append({"text": text})
    return Dataset.from_list(formatted)

@click.command()
@click.option('--data', '-d', default='data/train.jsonl', help='Путь к датасету')
@click.option('--model', '-m', default=DEFAULT_MODEL, help='Базовая модель')
@click.option('--output', '-o', default='checkpoints/final', help='Директория для сохранения')
@click.option('--epochs', '-e', default=3, help='Количество эпох обучения')
@click.option('--batch-size', '-b', default=4, help='Размер батча')
def train(data, model, output, epochs, batch_size):
    print("\n" + "="*60)
    print("   ДООБУЧЕНИЕ МОДЕЛИ (QLoRA)")
    print("="*60)
    print(f"📊 Датасет: {data}")
    print(f"🧠 Модель: {model}")
    print(f"📁 Выход: {output}\n")
    
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️  GPU не найден, используется CPU (будет медленно)")
    
    print("\n📥 Загрузка модели...")
    bnb_config = setup_quantization()
    model_instance = AutoModelForCausalLM.from_pretrained(
        model, quantization_config=bnb_config, device_map="auto", trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    model_instance = prepare_model_for_kbit_training(model_instance)
    model_instance = get_peft_model(model_instance, create_lora_config())
    model_instance.print_trainable_parameters()
    
    print("\n📚 Подготовка датасета...")
    dataset = prepare_dataset(data, tokenizer)
    print(f"   Примеров: {len(dataset)}")
    
    training_args = TrainingArguments(
        output_dir=output,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=50,
        save_total_limit=2,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported() and torch.cuda.is_available(),
        report_to="none"
    )
    
    trainer = SFTTrainer(
        model=model_instance,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        max_seq_length=2048,
        dataset_text_field="text",
        packing=False
    )
    
    print("\n🚀 Начинаем обучение...\n")
    trainer.train()
    
    print(f"\n💾 Сохранение модели в {output}")
    trainer.save_model(output)
    tokenizer.save_pretrained(output)
    print("\n✅ Обучение завершено!")
