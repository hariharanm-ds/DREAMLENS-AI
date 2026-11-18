with open('services/pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def simulate_scenario_pipeline(')
print(text[idx:idx+3500])
