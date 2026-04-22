# Vercel Deployment Notes

This repository now has two runtime surfaces:

- `app.py`: the existing Streamlit UI for local development
- `api/index.py`: a FastAPI backend that Vercel can deploy

## Why this split exists

The original app is built with Streamlit. Vercel's official Python support is for request/response functions and FastAPI or Flask style apps, not a long-lived Streamlit websocket server. Because of that, the demo backend was moved into a Vercel-compatible FastAPI entrypoint instead of trying to force the Streamlit UI into Vercel Functions.

## Required environment variables

- `GROQ_API_KEY`
- `GROQ_FAST_MODEL` optional, defaults to `llama-3.1-8b-instant`
- `GROQ_COMPLEX_MODEL` optional, defaults to `llama-3.1-8b-instant`

## Demo caveat

This setup is intentionally optimized for a free project demo, not for production reliability. Groq developer-tier access can still hit limits or temporary capacity issues. Audio transcription is also disabled in this configuration.

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
