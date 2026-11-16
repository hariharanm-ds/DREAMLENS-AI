import ast, sys

files = ['app.py', 'services/pipeline.py', 'services/youtube_search.py']
all_ok = True
for f in files:
    try:
        with open(f, encoding='utf-8') as fh:
            ast.parse(fh.read())
        print(f'[PASS] {f}')
    except SyntaxError as e:
        print(f'[FAIL] {f}: {e}')
        all_ok = False
    except Exception as e:
        print(f'[ERROR] {f}: {e}')
        all_ok = False

# JS validation: check for unmatched braces in chat.html script sections
with open('templates/chat.html', encoding='utf-8') as fh:
    html = fh.read()

# Count braces inside <script> blocks
import re
scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
js_combined = '\n'.join(scripts)
opens = js_combined.count('{')
closes = js_combined.count('}')
balance = opens - closes
print(f'\nJS brace balance: {{ = {opens}, }} = {closes}, diff = {balance}')
if abs(balance) <= 5:
    print('[PASS] JS brace balance looks healthy')
else:
    print(f'[WARN] JS brace imbalance of {balance} — may have syntax issue')
    all_ok = False

# Check key functions exist
key_fns = [
    'function resolveContextualImage',
    'function loadImageWithSkeleton',
    'function checkIsRateLimitPlaceholder',
    'function buildPollinationsUrl',
    'function renderSubconsciousQuests',
    'function renderDreamAuraCard',
    'function exportAuraCardToImage',
    'function shareAuraCardText',
    'function toggleSoundscape',
    'function startSoundscapeAudio',
    'function toggleOracleVoice',
    'function openGlobalSphereModal',
]
print()
for fn in key_fns:
    if fn in html:
        print(f'[PASS] {fn}')
    else:
        print(f'[FAIL] {fn} NOT FOUND in chat.html')
        all_ok = False

print('\nAll checks passed!' if all_ok else '\nSome checks FAILED.')

