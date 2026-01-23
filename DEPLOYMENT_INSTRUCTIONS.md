# Deployment to Vercel

This repository includes a Vercel serverless handler at `api/interpret.py` and a workflow to deploy on pushes to `main`.

Follow these steps to deploy the app to Vercel:

1. Create a Vercel account (https://vercel.com/) and import this GitHub repository (use the "Import Project" UI).
2. Add environment variables to your Vercel Project Settings:
   - `HUGGINGFACE_API_TOKEN` — (your Hugging Face API token) — required for full inference with HF models. If omitted, the API falls back to a simple heuristic.
3. In Vercel, create a Deploy Token:
   - Go to Account Settings → Tokens → Create Token. Copy the token.
4. In **this GitHub repository**, add the token as a GitHub secret:
   - `VERCEL_TOKEN` → the token copied from step 3
   - (Optional) `HUGGINGFACE_API_TOKEN` → you can also add the HF token as a GitHub secret if you want it available in Actions, but it's preferable to set it in Vercel environment variables for runtime usage.
5. Push to `main` (or open a PR that merges to `main`) — the workflow `.github/workflows/deploy-vercel.yml` will deploy automatically when `VERCEL_TOKEN` is present.

Notes & troubleshooting:
- The `api/interpret.py` uses `HUGGINGFACE_API_TOKEN` at runtime to call HF Inference API. If not set, it returns a fallback response.
- Large model usage can be slow or costly. Use the HF token only if you intend to use HF hosted inference. For local testing, consider using the lazy-loaded local models in `DREAMLENS AI/app.py`.
- If you prefer manual deploys or need to link to a specific Vercel Project, run the `vercel` CLI locally and follow the interactive linking steps (`vercel` then choose link options).

If you want, I can also:
- Add a GitHub Action step that posts the deployment URL back to the PR or issue ✅
- Add a health check step that pings the deployed `/` after the deploy and fails the job if unreachable ⚠️

Tell me which of those you'd like next.