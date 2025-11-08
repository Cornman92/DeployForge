FROM python:3.11-slim

LABEL org.opencontainers.image.title="DeployForge"
LABEL org.opencontainers.image.description="Windows Deployment Suite for customizing images and packages"
LABEL org.opencontainers.image.source="https://github.com/Cornman92/DeployForge"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wimtools \
    fuse \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./

# Install DeployForge
RUN pip install --no-cache-dir -e .

# Create mount points
RUN mkdir -p /mounts /images

# Set environment variables
ENV DEPLOYFORGE_MOUNT_DIR=/mounts
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 deployforge && \
    chown -R deployforge:deployforge /app /mounts /images

USER deployforge

ENTRYPOINT ["deployforge"]
CMD ["--help"]
