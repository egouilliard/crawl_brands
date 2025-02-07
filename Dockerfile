# Use Playwright's Python image (includes browsers)
FROM mcr.microsoft.com/playwright/python:v1.50.0-jammy

# Set the working directory inside the container
WORKDIR /app

# Increase shared memory size (fix Chrome crashes)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN mkdir -p /ms-playwright && chmod -R 777 /ms-playwright

# Copy only requirements first (to leverage Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Define the command to run the app
CMD ["/app/entrypoint.sh"]
