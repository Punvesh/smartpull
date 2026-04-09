FROM python:3.11-slim

LABEL maintainer="smartpull"
LABEL description="Hardware-aware LLM orchestration for local models"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY *.py .

# Default command
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]