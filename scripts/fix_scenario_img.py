#!/usr/bin/env python3
"""Patches scenario simulation JS to use client-side image generation."""

with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize to \n for easier manipulation
content = content.replace('\r\n', '\n')

# Fix the image loading in runScenarioSimulation - use image_prompt for client-side generation
old_img_block = """        const scImg = document.getElementById('scenarioArtImg');
        const scCanvas = document.getElementById('scenarioCanvas');
        if (data.image_url && scImg) {
          scImg.src = data.image_url;
          scImg.style.display = 'block';
          scImg.onload = () => { if (scCanvas) scCanvas.style.display = 'none'; };
          scImg.onerror = () => {
            scImg.style.display = 'none';
            if (scCanvas) { scCanvas.style.display = 'block'; renderScenarioCanvas(); }
          };
        } else {
          if (scImg) scImg.style.display = 'none';
          if (scCanvas) { scCanvas.style.display = 'block'; renderScenarioCanvas(); }
        }"""

new_img_block = """        const scImg = document.getElementById('scenarioArtImg');
        const scCanvas = document.getElementById('scenarioCanvas');
        // Generate image client-side using the image_prompt or visual_theme from server
        const scPrompt = data.image_prompt || data.visual_theme || choice + ' empowering golden breakthrough';
        loadImageWithSkeleton(scImg, scCanvas, scPrompt.substring(0,150), 'scenario');"""

if old_img_block in content:
    content = content.replace(old_img_block, new_img_block, 1)
    print("Applied: scenario image block fixed")
else:
    print("WARNING: scenario image block not found!")

with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done.")
