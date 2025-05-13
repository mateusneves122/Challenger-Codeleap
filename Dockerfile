# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt . 
RUN python -m pip install -r requirements.txt

# Set the working directory to /app/src (since your code is under src/)
WORKDIR /app/src

# Copy the entire src directory into the container
COPY src/ /app/src/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# CMD to run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi"]
