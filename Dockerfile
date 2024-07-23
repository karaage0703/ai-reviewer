# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY scripts/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY scripts /app/scripts

# Set environment variables
ENV OPENAI_API_KEY=""
ENV GITHUB_TOKEN=""
ENV GITHUB_REPOSITORY=""
ENV PULL_REQUEST_NUMBER=""

# Run the application
CMD ["python", "scripts/review_pr.py"]
