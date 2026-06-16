# Deployment to Vercel

DreamLens AI is configured for Vercel with `app.py` as the Python entrypoint and Groq as the hosted interpretation provider.

## Required Vercel Environment Variables

Set these in Vercel Project Settings -> Environment Variables:

```txt
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

`GROQ_MODEL` is optional. If omitted, the app uses `llama-3.3-70b-versatile`.

## Deploy

1. Import this repository in Vercel.
2. Add `GROQ_API_KEY` and optionally `GROQ_MODEL`.
3. Deploy.

Vercel uses:

- `vercel.json` for routing and build settings.
- `vercel_requirements.txt` for production dependencies.
- `app.py` for the Flask app.
- `groq_client.py` for Groq API calls.

## Verify

After deployment, check:

```txt
https://your-project.vercel.app/_health
https://your-project.vercel.app/_model_status
https://your-project.vercel.app/_env_check
```

Then test the main endpoint:

```bash
curl -X POST https://your-project.vercel.app/interpret \
  -H "Content-Type: application/json" \
  -d "{\"dream\":\"I was flying over a city and felt free\",\"force_model\":true}"
```

The response metadata should include:

```json
{"method": "groq"}
```
