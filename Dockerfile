# Stage 1: Base build stage
FROM python:3.12-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Upgrade pip
RUN pip install --upgrade pip 

# Copy the Django project  and install dependencies
COPY requirements.txt  /app/

# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Production stage
FROM python:3.12-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 6091 

CMD ["python", "-m", "gunicorn", "criterionchallenge.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:6091"]