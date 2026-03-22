import os
import httpx
import json

os.environ['NVIDIA_API_KEY'] = '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'

headers = {
    'Authorization': f"Bearer {os.environ['NVIDIA_API_KEY']}",
    'Content-Type': 'application/json'
}

payload = {
    'model': 'moonshotai/kimi-k2.5',
    'messages': [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Say hello in one word'}
    ],
    'max_tokens': 100,
    'temperature': 0.7,
    'stream': False
}

try:
    r = httpx.post('https://integrate.api.nvidia.com/v1/chat/completions', headers=headers, json=payload, timeout=60)
    print('Status:', r.status_code)
    data = r.json()
    print('Response:', json.dumps(data, indent=2)[:1000])
    if 'choices' in data:
        print('AI Response:', data['choices'][0].get('message', {}).get('content'))
except Exception as e:
    print('Error:', e)
