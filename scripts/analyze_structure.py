content = open('e:/DreamLensAI/templates/chat.html', encoding='utf-8').read()
lines = content.split('\n')
print(f'Total lines: {len(lines)}')

# Find all major section markers
sections = []
for i, line in enumerate(lines):
    if 'view-panel' in line or 'VIEW ' in line or '/view' in line.lower():
        sections.append((i+1, line.strip()[:100]))
    if 'id="viewResults"' in line or 'id="viewDashboard"' in line or 'id="viewLoading"' in line or 'id="viewCinema"' in line:
        sections.append((i+1, f'*** {line.strip()[:100]}'))

for s in sections:
    print(f'  L{s[0]}: {s[1]}')

# Find all <script> blocks and key JS function starts
print('\n--- Script blocks ---')
for i, line in enumerate(lines):
    if '<script' in line.lower():
        print(f'  L{i+1}: {line.strip()[:100]}')

# Count total lines of JS vs HTML
script_start = None
script_lines = 0
html_lines = 0
in_script = False
for i, line in enumerate(lines):
    if '<script' in line.lower():
        in_script = True
        if script_start is None:
            script_start = i+1
    if '</script' in line.lower():
        in_script = False
    if in_script:
        script_lines += 1
    else:
        html_lines += 1
print(f'\nHTML lines: {html_lines}, JS lines: {script_lines}')
print(f'Script starts at line: {script_start}')

# Find the end of HTML content (before <script>)
for i, line in enumerate(lines):
    if '<script>' in line or '<script ' in line:
        print(f'First <script> tag at line: {i+1}')
        break

# Find Global Sphere Modal, Aura Card, etc.
for keyword in ['globalSphereModal', 'aura-card-modal', 'viewCinema', '</main>']:
    idx = content.find(keyword)
    if idx != -1:
        print(f'{keyword}: line {content[:idx].count(chr(10))+1}')
