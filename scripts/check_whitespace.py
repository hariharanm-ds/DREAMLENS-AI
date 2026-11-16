content = open('e:/DreamLensAI/templates/chat.html', encoding='utf-8').read()
lines = content.split('\n')

# Print the exact bytes around tabEmotions
start_idx = content.find('id="tabEmotions"')
chunk = content[start_idx - 10 : start_idx + 100]
print(repr(chunk))
