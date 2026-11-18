with open('static/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('.overview-grid')
print(text[idx:idx+400])
