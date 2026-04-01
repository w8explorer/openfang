import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

# SLIM system prompt simulation (~300 tokens)
SYSTEM_PROMPT = """
You are the OpenFang Assistant. 
You are running on an ARM64 architecture (Oracle Cloud Neoverse-N1).
Your goal is to coordinate tasks.

CAPABILITIES:
- file_read, file_write, file_list, web_fetch, shell_exec.

INSTRUCTIONS:
1. Be concise.
2. Use JSON tool call format: {"tool": "name", "args": { ... }}

[SLIM CONTEXT]
""" + ("Context filler. " * 20)

def benchmark_model(model_name, prompt):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False
    }

    print(f"\n--- Benchmarking {model_name} ---")
    start_time = time.time()
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        end_time = time.time()
        duration = end_time - start_time
        
        tokens = data.get("eval_count", 0)
        tps = tokens / duration if duration > 0 else 0
        ttft = data.get("load_duration", 0) / 1e9 # Convert nanoseconds to seconds
        
        print(f"Status: SUCCESS")
        print(f"Time to First Token (est): {ttft:.2f}s")
        print(f"Generation Duration: {duration:.2f}s")
        print(f"Total Tokens: {tokens}")
        print(f"Tokens Per Second: {tps:.2f} TPS")
        print(f"Response: {data.get('response', '')[:100]}...")
        
        return {
            "model": model_name,
            "tps": tps,
            "duration": duration,
            "tokens": tokens,
            "success": True
        }
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return {"model": model_name, "success": False}

if __name__ == "__main__":
    # Test 1: Simple Reasoning
    print("Test 1: Simple Greeting")
    benchmark_model(MODEL, "Hello! Tell me who you are in one sentence.")
    
    # Test 2: Tool Call Reliability (Under pressure)
    print("\nTest 2: Tool Calling Reliability")
    test_2_prompt = "I need you to list the files in /home/ubuntu/openfang. Use the correct JSON tool call format."
    benchmark_model(MODEL, test_2_prompt)
