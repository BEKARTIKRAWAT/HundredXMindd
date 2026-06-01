import requests
import json
response = requests.post('http://127.0.0.1:8000/ask_stream', json={'question':'What is AI?'}, stream=True)
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]
            if data == '[DONE]':
                break
            try:
                obj = json.loads(data)
                print(obj.get('response', ''), end='', flush=True)
            except:
                pass
