with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function generateRichRevelationClient(')
print(text[idx:idx+1200])
