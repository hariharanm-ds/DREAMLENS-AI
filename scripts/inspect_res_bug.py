with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="viewResults"')
print("Snippet around viewResults:")
print(text[idx:idx+1500])
