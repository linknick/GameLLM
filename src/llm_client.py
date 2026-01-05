"""LLM adapter: supports Ollama (requests.post) and OpenAI (openai lib).
Provides a simple unified interface: generate(messages, model=None)
"""
import os
import requests
import json
from typing import List, Dict


PREFERRED = os.getenv("PREFERRED_LLM", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# Optional: import openai only if fallback
try:
    import openai
    openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None




def call_ollama(messages: List[Dict], model: str = None) -> str:
    model = model or OLLAMA_MODEL
    url = f"{OLLAMA_URL}/api/chat"
    payload = {"model": model, "messages": messages}
    r = requests.post(url, json=payload, stream = False)
    
    output = ""
    for line in r.iter_lines():
        
        if line:
            obj = json.loads(line)
            if "message" in obj and "content" in obj["message"]:
                output += obj["message"]["content"]
    
    return output
    


def call_openai(messages: List[Dict], model: str = None) -> str:
    model = model or OPENAI_MODEL
    if openai is None:
        raise RuntimeError("openai package not installed or OPENAI_API_KEY missing")
        
    resp = openai.ChatCompletion.create(model=model, messages=messages)
    
    return resp.choices[0].message.content




class LLMClient:
    def __init__(self, prefer=PREFERRED):
        self.prefer = prefer


    def generate(self, messages: List[Dict], model: str = None) -> str:
        
        if self.prefer == "ollama":
            try:
                return call_ollama(messages, model=model)
            except Exception as e:
                print("Ollama call failed, falling back to OpenAI:", e)
            return call_openai(messages, model=model)
        """else:
            try:
                return call_openai(messages, model=model)
            except Exception:
                return call_ollama(messages, model=model)
        """