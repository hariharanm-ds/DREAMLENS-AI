#!/usr/bin/env python3
"""Patches psychology cards in chat.html with gradient icons and source badges."""
import sys
import re

with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # Freudian card - add gradient border and gradient icon
    (
        'class="dash-card psych-lens-card">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill">🧠</span>',
        'class="dash-card psych-lens-card" style="border-top:3px solid #dc2626;">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill" style="background:linear-gradient(135deg,#dc2626,#9333ea)">🧠</span>'
    ),
    # Freudian - add footer badge
    (
        'id="lensFreudianText">\n              Subconscious drives and emotional desires seeking expression.\n            </p>\n          </div>\n\n          <!-- JUNGIAN',
        'id="lensFreudianText">\n              Subconscious drives and emotional desires seeking expression.\n            </p>\n            <div class="psych-card-footer"><span class="psych-lens-badge" style="background:rgba(220,38,38,0.15);color:#f87171;">Depth Psychology</span></div>\n          </div>\n\n          <!-- JUNGIAN'
    ),
    # Jungian card 
    (
        'class="dash-card psych-lens-card">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill">🌌</span>',
        'class="dash-card psych-lens-card" style="border-top:3px solid #7c3aed;">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill" style="background:linear-gradient(135deg,#7c3aed,#06b6d4)">🌌</span>'
    ),
    # Jungian footer
    (
        'id="lensJungianText">\n              Archetypal integration of the Shadow and the emergence of the Self.\n            </p>\n          </div>\n\n          <!-- MODERN',
        'id="lensJungianText">\n              Archetypal integration of the Shadow and the emergence of the Self.\n            </p>\n            <div class="psych-card-footer"><span class="psych-lens-badge" style="background:rgba(124,58,237,0.15);color:#c084fc;">Analytical Psychology</span></div>\n          </div>\n\n          <!-- MODERN'
    ),
    # Modern card
    (
        'class="dash-card psych-lens-card">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill">🔬</span>',
        'class="dash-card psych-lens-card" style="border-top:3px solid #0891b2;">\n            <div class="psych-card-head">\n              <span class="psych-icon-pill" style="background:linear-gradient(135deg,#0891b2,#10b981)">🔬</span>'
    ),
    # Modern footer
    (
        'id="lensModernText">\n              Active problem solving and neural memory consolidation for waking challenges.\n            </p>\n          </div>\n\n        </div><!-- /psychology-3col-grid -->',
        'id="lensModernText">\n              Active problem solving and neural memory consolidation for waking challenges.\n            </p>\n            <div class="psych-card-footer"><span class="psych-lens-badge" style="background:rgba(8,145,178,0.15);color:#22d3ee;">Neuroscience</span></div>\n          </div>\n\n        </div><!-- /psychology-3col-grid -->'
    ),
    # Mythological card border + icon
    (
        'class="dash-card mythological-card" id="mythologicalCard">\n          <div class="psych-card-head">\n            <span class="psych-icon-pill">🕉️</span>',
        'class="dash-card mythological-card" id="mythologicalCard" style="border-top:3px solid #d97706;">\n          <div class="psych-card-head">\n            <span class="psych-icon-pill" style="background:linear-gradient(135deg,#d97706,#f59e0b)">🕉️</span>'
    ),
    # Mythological footer
    (
        'id="lensMythologicalText">\n            Echoes ancient sacred folklore and mythic transformations.\n          </p>\n        </div>',
        'id="lensMythologicalText">\n            Echoes ancient sacred folklore and mythic transformations.\n          </p>\n          <div class="psych-card-footer"><span class="psych-lens-badge" style="background:rgba(217,119,6,0.15);color:#fbbf24;">World Mythology</span></div>\n        </div>'
    ),
]

changed = 0
for old, new in replacements:
    # Normalize line endings
    old_n = old.replace('\r\n', '\n')
    new_n = new.replace('\r\n', '\n')
    content_n = content.replace('\r\n', '\n')
    if old_n in content_n:
        content = content_n.replace(old_n, new_n, 1)
        changed += 1
        print(f"  Applied: {old_n[:60].strip()!r}...")
    else:
        print(f"  WARNING NOT FOUND: {old_n[:60].strip()!r}...")

print(f"\nTotal replacements applied: {changed}/{len(replacements)}")

with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved.")
