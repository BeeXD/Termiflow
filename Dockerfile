# Use official Python runtime as base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY main.py .
COPY engine.py .
COPY workflow.json .

# Set the entrypoint to use python main.py
ENTRYPOINT ["python", "main.py"]

# Default command shows help
CMD ["--help"]
