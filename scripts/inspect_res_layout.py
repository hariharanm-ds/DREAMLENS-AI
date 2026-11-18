with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="viewResults"')
idx_end = text.find('id="tabOverview"')
print(text[idx:idx_end+200])
