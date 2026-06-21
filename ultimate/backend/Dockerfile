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

# Create a dedicated non-root user and group ('appuser') for enhanced security.
# Running as a non-root user mitigates the risk of privilege escalation if the container is compromised.
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime system dependencies (e.g., PostgreSQL client libraries, curl for healthchecks)
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

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user for all subsequent commands
USER appuser

# Healthcheck to verify the FastAPI application is responsive.
# - interval=30s: Wait 30s between checks
# - timeout=5s: Fail the check if no response within 5s
# - start-period=10s: Give the app 10s to boot before starting checks
# - retries=3: Mark container as unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose the application port to the Docker network
EXPOSE 8000

# Default command to run the FastAPI application via Uvicorn.
# In production, this might be managed by gunicorn with uvicorn workers.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
