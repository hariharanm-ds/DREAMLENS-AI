import requests

BASE = 'http://127.0.0.1:5000'

print('Checking /_health...')
r = requests.get(BASE + '/_health', timeout=5)
print(r.status_code, r.json())

print('Checking /_model_status...')
r = requests.get(BASE + '/_model_status', timeout=30)
print(r.status_code, r.json())

print('Checking /_env_check...')
r = requests.get(BASE + '/_env_check', timeout=30)
print(r.status_code)
print(r.json())

print('Checking /interpret with sample dream...')
r = requests.post(BASE + '/interpret', json={'dream': 'I fell into an ocean and felt anxious'}, timeout=60)
print(r.status_code)
print(r.json())

print('Checking /interpret with force_model=true...')
r = requests.post(BASE + '/interpret', json={'dream':'I dream of a neon dragon playing chess with a fox in space','force_model':True}, timeout=60)
print(r.status_code)
print(r.json())
