# DREAMLENS AI - RAILWAY DEPLOYMENT (5 MINUTES)

## What is Railway?

Railway is a modern cloud platform that auto-detects Python apps and deploys them instantly. Perfect for DreamLens AI!

---

## Prerequisites

✅ GitHub account (free at github.com)
✅ Railway account (free at railway.app)
✅ This code pushed to GitHub

---

## STEP-BY-STEP DEPLOYMENT

### STEP 1: Push Code to GitHub

If you haven't already:

```bash
cd "e:\DreamLensAI\DREAMLENS AI"
git remote add origin https://github.com/YOUR_USERNAME/dreamlens-ai.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

### STEP 2: Create Railway Account

1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize GitHub access
4. Accept terms

---

### STEP 3: Create New Project

1. Click "Create New Project"
2. Select "Deploy from GitHub"
3. Search for "dreamlens-ai"
4. Click to select your repository
5. Grant Railway access to repository

---

### STEP 4: Add Ollama Service

Railway will automatically create the main app service. Now add Ollama:

1. In your Railway project, click "New Service"
2. Click "Marketplace"
3. Search for "Ollama"
4. Click "Ollama" (by community)
5. Click "Deploy"

Railway will start downloading the Ollama service (~2 minutes).

---

### STEP 5: Configure Environment Variables

#### For DreamLens App Service:

1. Click on "app" service
2. Go to "Variables" tab
3. Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_DEBUG` | `false` |
| `OLLAMA_HOST` | `http://ollama:11434` |
| `PORT` | `5000` |

Replace `ollama` with the actual Ollama service name if different.

#### For Ollama Service:

1. Click on "ollama" service
2. Go to "Variables" tab
3. Add:

| Key | Value |
|-----|-------|
| `OLLAMA_MODEL` | `mistral` |
| `OLLAMA_HOST` | `0.0.0.0:11434` |

---

### STEP 6: Deploy

1. Railway auto-deploys when you push to GitHub
2. Or manually trigger:
   - Click "Deployments" tab
   - Click the latest deployment
   - Click "Redeploy"

3. Check deployment logs:
   - Click on "app" service
   - Go to "Logs" tab
   - Wait for "Running on" message

---

### STEP 7: Access Your App

1. Click on "app" service
2. Look for "Domains" section
3. Click on the domain: `your-app.railway.app`
4. Add `/chat` to access chat interface

**Example**: `https://dreamlens-ai-xyz.railway.app/chat`

---

## WHAT RAILWAY DOES AUTOMATICALLY

✅ Detects Python app from Procfile
✅ Installs dependencies from requirements.txt
✅ Configures Gunicorn web server
✅ Sets up SSL/HTTPS
✅ Provides custom domain
✅ Auto-deploys on GitHub push
✅ Handles scaling automatically

---

## MONITORING & TROUBLESHOOTING

### View Logs

```bash
# If using Railway CLI
railway logs --service app

# Or use dashboard:
# Dashboard → project → app → Logs
```

### Common Issues

**App won't start**
- Check logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` is correct

**Can't connect to Ollama**
- Verify `OLLAMA_HOST=http://ollama:11434`
- Wait 2-3 minutes for Ollama to start
- Check Ollama service logs

**Timeout errors**
- First request takes 30-60 seconds (model loading)
- Subsequent requests are faster
- This is normal

**Out of memory**
- Mistral needs 8GB+ RAM
- Upgrade Railway plan ($5-10/month)
- Or use smaller model: `neural-chat` (4GB)

---

## PERFORMANCE TIPS

1. **First Request**: 30-60 seconds (model loads into memory)
2. **Subsequent Requests**: 15-30 seconds (model cached)
3. **Multiple Users**: May take longer due to queue
4. **Upgrade RAM**: If responses slow, upgrade Railway plan

---

## CUSTOM DOMAIN

To use your own domain (optional):

1. Buy domain at Namecheap.com or GoDaddy.com
2. In domain provider, find DNS settings
3. Add CNAME record:
   - Name: `www`
   - Value: `your-app.railway.app`
4. In Railway dashboard:
   - Service → app → Domains
   - Click "Add Domain"
   - Enter your domain
5. Wait 24 hours for DNS to propagate

---

## AUTO-DEPLOY ON PUSH

Railway automatically redeploys whenever you push to GitHub:

```bash
git add .
git commit -m "Fix dream interpretation"
git push origin main
```

Deployment starts automatically in ~30 seconds!

---

## ROLLBACK (If Something Breaks)

1. Dashboard → Deployments
2. Click previous successful deployment
3. Click "Redeploy"
4. Or fix code and push again

---

## SHARE YOUR APP

Once deployed, share link with friends:

```
Check out my AI dream interpreter:
https://your-app.railway.app/chat
```

---

## NEXT STEPS

- [x] Deploy to Railway ✅
- [ ] Test with sample dream
- [ ] Share with friends
- [ ] Get feedback
- [ ] Improve based on usage
- [ ] Add more features

---

## SUPPORT

- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: https://github.com/YOUR_USERNAME/dreamlens-ai/issues
- **Ollama Docs**: https://ollama.ai

---

## COST BREAKDOWN

| Item | Cost |
|------|------|
| DreamLens App | Free tier (0.5GB) |
| Ollama Service | Free tier (0.5GB) |
| **Total** | **FREE** ✅ |

Paid options:
- $5/month per 1GB RAM
- Recommended: $5-10/month total

---

## WHAT NOW?

1. **Go to Railway**: https://railway.app
2. **Click "Create New Project"**
3. **Deploy this repository**
4. **Wait 5 minutes**
5. **Share your dream AI with the world!**

🎉 **You're now live on the internet!**

---

Made with ❤️ for dreamers everywhere
