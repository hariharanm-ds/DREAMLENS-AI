with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('<div class="overview-grid">')
print(text[idx:idx+1500])
