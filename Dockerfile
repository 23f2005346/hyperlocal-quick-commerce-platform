# =========================================================================
# KOMAL MART — UNIFIED PRODUCTION FULL-STACK DOCKERFILE
# Multi-stage: Builds Vite PWA Frontend + Serves via Python/Flask + Gunicorn
# =========================================================================

# --- STAGE 1: FRONTEND BUILDER ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- STAGE 2: PRODUCTION PYTHON RUNTIME ---
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application source
COPY backend/ ./backend/

# Copy compiled frontend assets from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV FLASK_ENV=production

# Expose default port
EXPOSE 5000

# Run with Gunicorn WSGI server
CMD ["sh", "-c", "gunicorn --chdir backend -w 2 --threads 4 -b 0.0.0.0:${PORT:-5000} 'app:create_app()'"]
