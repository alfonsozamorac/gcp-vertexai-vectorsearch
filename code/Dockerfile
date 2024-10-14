# Use the official Python base image
FROM python:3.12-slim

# Step 1: Define build arguments
ARG project_id
ARG index_id
ARG index_endpoint_id
ARG confluence_url
ARG company
ARG support_mail

# Step 2: Set environment variables from the build arguments
ENV PROJECT_ID=$project_id
ENV INDEX_ID=$index_id
ENV INDEX_ENDPOINT_ID=$index_endpoint_id
ENV CONFLUENCE_URL=$confluence_url
ENV COMPANY=$company
ENV SUPPORT_MAIL=$support_mail
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the work directory
WORKDIR /app

# Step 3: Copy the project files to the container
COPY . /app/

# Step 4: Install Python dependencies
RUN pip install -r requirements.txt

# Step 5: Expose the port for Cloud Run
EXPOSE 8080

# Step 6: Run FastAPI
CMD ["uvicorn", "app:app", "--reload", "--port", "8080", "--host", "0.0.0.0"]
