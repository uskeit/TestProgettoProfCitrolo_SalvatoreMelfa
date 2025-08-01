# Use the official Python image with a compatible version
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY main.py ./
COPY execution/ ./execution/

# Install uv and project dependencies
RUN pip install uv && \
    uv sync

# Expose the port your MCP server will use (update as needed)
EXPOSE 8080

# Set the default command to run the MCP server (update as needed)
CMD ["uv", "run", "python", "main.py"]
