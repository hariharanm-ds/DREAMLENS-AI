#!/bin/bash
# PUSH TO GITHUB - COPY PASTE THIS SCRIPT

# ============================================
# STEP 1: CREATE GITHUB REPO
# ============================================
# 1. Go to: https://github.com/new
# 2. Repository name: dreamlens-ai
# 3. Description: "AI-powered dream interpretation using Mistral LLM"
# 4. Visibility: Public
# 5. DO NOT initialize with README
# 6. Click "Create repository"

# ============================================
# STEP 2: COPY AND PASTE IN POWERSHELL
# ============================================

# Navigate to project
cd "e:\DreamLensAI\DREAMLENS AI"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/dreamlens-ai.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main

# ============================================
# STEP 3: VERIFY ON GITHUB
# ============================================
# Go to: https://github.com/YOUR_USERNAME/dreamlens-ai
# You should see all your files!

# ============================================
# STEP 4: DEPLOY TO RAILWAY
# ============================================
# 1. Go to: https://railway.app
# 2. Sign up with GitHub
# 3. Create new project
# 4. Select "Deploy from GitHub"
# 5. Choose your dreamlens-ai repo
# 6. Add Ollama service from marketplace
# 7. Set environment variables:
#    FLASK_DEBUG=false
#    OLLAMA_HOST=http://ollama:11434
# 8. Deploy!

# ============================================
# YOUR APP IS LIVE! 🚀
# ============================================
# Access at: https://your-app.railway.app/chat
