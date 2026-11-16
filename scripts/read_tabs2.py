content = open('e:/DreamLensAI/templates/chat.html', encoding='utf-8').read()
lines = content.split('\n')

# Find the exact line ranges for tabEmotions and tabSymbols sections
start_e = content.find('id="tabEmotions"')
end_e = content.find('id="tabSymbols"')

start_s = content.find('id="tabSymbols"')
end_s = content.find('id="tabPsychology"')

print('EMOTIONS (lines {}-{}):'.format(content[:start_e].count('\n'), content[:end_e].count('\n')))
print(content[start_e:end_e])
print('\n\n==== SYMBOLS (lines {}-{}):'.format(content[:start_s].count('\n'), content[:end_s].count('\n')))
print(content[start_s:end_s])

# Also find the render functions
render_e_start = content.find('function renderEmotionWaveCanvas')
render_s_start = content.find('function renderSymbolNetworkCanvas')
print('\n\n==== renderEmotionWaveCanvas starts at line:', content[:render_e_start].count('\n') if render_e_start!=-1 else 'NOT FOUND')
print('==== renderSymbolNetworkCanvas starts at line:', content[:render_s_start].count('\n') if render_s_start!=-1 else 'NOT FOUND')
