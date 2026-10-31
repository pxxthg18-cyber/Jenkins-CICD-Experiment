# ==============================================================================
# Dockerfile: jenkins-cicd-flask-app
# Purpose: Containerize the beginner Flask application for CI/CD pipeline automation
# ==============================================================================

# 1. Official lightweight Python runtime
FROM python:3.10-slim

# 2. Set environment variables to optimize Python for containerized environments
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# - PYTHONUNBUFFERED: Keeps Python from buffering stdout/stderr for immediate log streaming
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# 3. Create and set the working directory inside the container
WORKDIR /app

# 4. Copy dependency file first to leverage Docker layer caching
COPY requirements.txt /app/

# 5. Install Python dependencies without saving wheel cache to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application source code into the container
COPY . /app/

# 7. Expose the port on which the Flask app will listen
EXPOSE 5000

# 8. Define a container health check using Python standard library (no extra tools required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# 9. Specify default command to run the application
# Use "python app.py" for development / lab simplicity, or "gunicorn -b 0.0.0.0:5000 app:app" for production
CMD ["python", "app.py"]
