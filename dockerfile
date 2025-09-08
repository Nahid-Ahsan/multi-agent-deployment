# Use an official Python base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code into the container (main.py and other directories)
COPY ./main.py ./main.py
COPY ./endpoints ./endpoints
COPY ./schemas ./schemas
COPY ./services ./services

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
