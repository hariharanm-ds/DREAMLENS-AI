with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="tabScenarios"')
idx2 = text.find('possible-outcomes-wrap', idx)
print(text[idx2:idx2+1500])
