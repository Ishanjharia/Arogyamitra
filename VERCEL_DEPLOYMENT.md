# Vercel Deployment Notes

This repository now has two runtime surfaces:

- `app.py`: the existing Streamlit UI for local development
- `api/index.py`: a FastAPI backend that Vercel can deploy

## Why this split exists

The original app is built with Streamlit. Vercel's official Python support is for request/response functions and FastAPI or Flask style apps, not a long-lived Streamlit websocket server. Because of that, the demo backend was moved into a Vercel-compatible FastAPI entrypoint instead of trying to force the Streamlit UI into Vercel Functions.

## Required environment variables

- `OPENROUTER_API_KEY`
- `OPENROUTER_FAST_MODEL` optional, defaults to `openrouter/free`
- `OPENROUTER_COMPLEX_MODEL` optional, defaults to `openrouter/free`
- `OPENROUTER_SITE_URL` optional
- `OPENROUTER_APP_NAME` optional

## Demo caveat

This setup is intentionally optimized for a free project demo, not for production reliability. OpenRouter free models can be rate-limited, slower, or temporarily unavailable. Audio transcription is also disabled in this free configuration.

## Main API routes

- `GET /api`
- `GET /api/health`
- `POST /api/translate`
- `POST /api/analyze-symptoms`
- `POST /api/chat`
- `POST /api/prescription-translation`
- `POST /api/doctor-notes`
- `POST /api/find-hospitals`
- `POST /api/transcribe-audio`

## Deploy

1. Import the repository into Vercel.
2. Add the environment variables in the Vercel project settings.
3. Deploy. Vercel will detect `api/index.py` and serve it as a Python function.

## Local usage

- Streamlit UI: `streamlit run app.py --server.port 5000`
- Vercel-style API locally: `vercel dev`
