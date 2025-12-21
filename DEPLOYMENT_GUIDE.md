# DEPLOYMENT GUIDE - DREAMLENS AI

## Quick Deploy Options

### Option 1: Railway (Recommended) ⭐

Railway is the easiest way to deploy with automatic Ollama integration.

#### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "Create New Project"
   - Select "Deploy from GitHub"
   - Choose your dreamlens-ai repository

3. **Add Ollama Service**
   - In Railway Dashboard, click "New Service"
   - Select "Marketplace"
   - Search and add "Ollama"
   - Configure with 8GB+ RAM

4. **Connect Services**
   - In app service, go to Variables
   - Add: `OLLAMA_HOST=http://ollama:11434`

5. **Deploy**
   - Railway auto-deploys on push
   - Monitor logs in dashboard
   - Access your app URL

**Time to deploy**: ~5 minutes
**Cost**: Free tier available (0.5GB RAM) or $5/month

---

### Option 2: Heroku

Heroku is a traditional PaaS with buildpack support.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   choco install heroku-cli  # Windows
   brew install heroku/brew/heroku  # Mac
   sudo apt-get install heroku  # Linux
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create dreamlens-ai-unique-name
   ```

4. **Add Buildpack**
   ```bash
   heroku buildpacks:add heroku/python
   ```

5. **Configure Ollama** (Remote Instance)
   ```bash
   heroku config:set OLLAMA_HOST=https://your-ollama-server.com:11434
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **View Logs**
   ```bash
   heroku logs --tail
   ```

**Time to deploy**: ~10 minutes
**Cost**: Free tier (limited) or $7/month

---

### Option 3: Docker + DigitalOcean App Platform

Best for full control and scalability.

#### Steps:

1. **Create Dockerfile** (already in repo)

2. **Push to Docker Hub**
   ```bash
   docker build -t yourusername/dreamlens-ai .
   docker push yourusername/dreamlens-ai
   ```

3. **Deploy on DigitalOcean**
   - Create account at https://digitalocean.com
   - Create new App
   - Select Docker image
   - Point to your docker image
   - Deploy

**Time to deploy**: ~15 minutes
**Cost**: $5/month minimum

---

### Option 4: Local Production Server (Advanced)

For deploying on your own machine/server.

#### Steps:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install gunicorn gevent
   ```

2. **Run with Gunicorn** (production server)
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app_llm:app
   ```

3. **Setup Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
       }
   }
   ```

4. **Enable HTTPS with Let's Encrypt**
   ```bash
   certbot --nginx -d your-domain.com
   ```

5. **Auto-start with Supervisor**
   ```ini
   [program:dreamlens]
   command=/path/to/venv/bin/gunicorn -w 4 app_llm:app
   directory=/path/to/dreamlens-ai
   autostart=true
   autorestart=true
   ```

**Time to deploy**: ~30 minutes
**Cost**: ~$5-20/month (VPS)

---

## Environment Variables

All deployment options require these variables:

```env
FLASK_DEBUG=false              # Never use true in production!
PORT=5000                      # Or assigned by platform
OLLAMA_HOST=http://localhost:11434  # Local or remote Ollama
```

---

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Test chat interface
- [ ] Send test dream
- [ ] Check response time (<60 seconds)
- [ ] Verify Ollama connection status
- [ ] Monitor error logs
- [ ] Setup custom domain (optional)
- [ ] Enable HTTPS/SSL
- [ ] Setup monitoring/alerts

---

## Troubleshooting Deployment

### App won't start
```bash
# Check logs
heroku logs --tail

# Or Railway dashboard → Logs tab
```

### Ollama connection failed
- Verify `OLLAMA_HOST` environment variable
- Ensure Ollama service is running
- Check firewall rules
- Test with: `curl $OLLAMA_HOST/api/tags`

### Timeout errors
- Increase timeout in `app_llm.py` line ~130
- Upgrade server RAM
- Use faster model: `ollama pull neural-chat`

### Memory issues
- Mistral needs ~8GB RAM for inference
- Use 4GB model if needed: `ollama pull orca-mini`
- Close other applications

---

## Performance Optimization

For production:

1. **Use Gunicorn with multiple workers**
   ```bash
   gunicorn -w 4 -k gevent app_llm:app
   ```

2. **Add Redis caching** (optional)
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
   ```

3. **Setup CDN for static files**
   - CloudFlare or similar
   - Cache CSS/JS aggressively

4. **Monitor with APM tools**
   - NewRelic
   - DataDog
   - Sentry (error tracking)

---

## Scaling Guide

As traffic grows:

**Small (100 users/day)**
- Basic single server
- ~2GB RAM minimum
- Cost: ~$5/month

**Medium (1,000 users/day)**
- Load balancer + 2-3 servers
- ~8GB RAM per server
- Redis caching
- Cost: ~$50-100/month

**Large (10,000+ users/day)**
- Kubernetes cluster
- Auto-scaling
- Database caching
- CDN
- Cost: ~$500+/month

---

## Custom Domain Setup

For Railway/Heroku:

1. Buy domain (Namecheap, GoDaddy)
2. Add CNAME: `your-domain.com → your-app.railway.app`
3. Wait 24 hours for DNS propagation
4. Verify in platform dashboard
5. Optional: Auto-generate HTTPS with Let's Encrypt

---

## Backup & Monitoring

1. **Backup CSV Database**
   - Store on GitHub (included)
   - Weekly backups to S3

2. **Monitor Performance**
   - Track response times
   - Monitor error rates
   - Alert on downtime

3. **Log Rotation**
   ```bash
   # Keep logs for 30 days
   find . -name "*.log" -mtime +30 -delete
   ```

---

## Security Checklist

- [ ] Disable debug mode in production
- [ ] Use HTTPS only
- [ ] Add CORS headers if needed
- [ ] Rate limit API endpoints
- [ ] Sanitize user input (already done)
- [ ] Use strong secret key (if needed)
- [ ] Keep dependencies updated
- [ ] Monitor for security patches

---

**Ready to deploy?** Choose your platform above and get started!

Questions? Check GitHub Issues or README.md for support.
