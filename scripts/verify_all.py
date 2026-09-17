#!/usr/bin/env python3
"""Verifies all changes are correctly in place in chat.html and style.css."""

with open('templates/chat.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

checks = {
    'buildPollinationsUrl function': 'function buildPollinationsUrl' in html,
    'loadImageWithSkeleton function': 'function loadImageWithSkeleton' in html,
    'Client-side dreamscape image': 'dream_text_for_image' in html and 'loadImageWithSkeleton(dreamImg' in html,
    'Stage images loaded client-side': 'stageImg' in html and 'loadImageWithSkeleton' in html,
    'Dynamic YouTube (no static fallback)': 'fetchLiveDreamVideosForOverview' in html,
    'Scenario uses image_prompt': 'image_prompt' in html,
    'Psychology Depth Psychology badge': 'Depth Psychology' in html,
    'Psychology Analytical badge': 'Analytical Psychology' in html,
    'Psychology Neuroscience badge': 'Neuroscience' in html,
    'Psychology World Mythology badge': 'World Mythology' in html,
    'Freudian border-top red': 'border-top:3px solid #dc2626' in html,
    'Jungian border-top purple': 'border-top:3px solid #7c3aed' in html,
    'Mythological border-top amber': 'border-top:3px solid #d97706' in html,
    'Shimmer animation in CSS': 'shimmer-sweep' in css,
    'img-loading class in CSS': 'img-loading' in css,
    'No static VIDEOS fallback in cinema': 'VIDEOS.slice(0, 4)' not in html,
    'Retry backoff in pipeline': 'time.sleep' in open('services/pipeline.py').read(),
}

all_pass = True
for k, v in checks.items():
    status = 'PASS' if v else 'FAIL'
    if not v:
        all_pass = False
    print(f'  [{status}] {k}')

print()
print('All checks pass!' if all_pass else 'SOME CHECKS FAILED!')
