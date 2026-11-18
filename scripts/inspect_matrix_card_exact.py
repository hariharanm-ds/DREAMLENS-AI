with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('alt-timeline-card full-card matrix-card')
print(text[idx:idx+1500])
