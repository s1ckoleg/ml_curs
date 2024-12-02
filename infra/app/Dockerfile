# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the app files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install dependencies
RUN pip install flask

# Run the application
CMD ["python", "app.py"]

