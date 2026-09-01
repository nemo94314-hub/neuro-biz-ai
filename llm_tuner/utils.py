import json
import os
from typing import List, Dict, Any

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(filepath: str, data: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def format_chat_template(instruction: str, response: str) -> Dict[str, str]:
    return {
        "messages": [
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": response}
        ]
    }
