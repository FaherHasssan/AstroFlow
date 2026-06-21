# Stage 1: Build dependency wheels
FROM python:3.12-slim AS builder

# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files to disk.
# This saves disk space and prevents potential issues with stale bytecode.
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED=1: Forces standard output and standard error streams to be unbuffered.
# This ensures logs are immediately visible in the Docker output, which is critical for debugging.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required to build Python packages (like psycopg2 or cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the builder
COPY requirements.txt .

# Build wheels for dependencies to optimize final image size and speed up runtime installation
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Runtime environment
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 🚀 CHANGED 'appuser' TO 'astroapp' TO AVOID THE EXIT CODE 9 CONFLICT
RUN groupadd -r astroapp && useradd -r -g astroapp astroapp

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from the builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install the Python packages from the pre-built wheels
RUN pip install --no-cache /wheels/*

# Copy the application source code into the container
COPY . /app

# 🚀 UPDATE OWNERSHIP TO THE NEW USER
RUN chown -R astroapp:astroapp /app

# 🚀 SWITCH TO THE NEW USER
USER astroapp

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]