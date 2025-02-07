# Use an official Python image as a base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Define the command to run the app
CMD ["/app/entrypoint.sh"]
