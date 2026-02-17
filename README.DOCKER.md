# 🐳 Docker Setup Guide

## Quick Start

### Using launch.bat (Windows)
Simply run:
```bash
launch.bat
```

This will:
- Check if Docker is installed and running
- Build the Docker image if needed
- Start the container
- Open the app at http://localhost:8501

### Using Docker Compose

#### Development Mode
```bash
docker-compose -f docker-compose.dev.yml up --build
```

#### Production Mode
```bash
docker-compose up -d --build
```

## Prerequisites

- Docker Desktop installed and running
- Windows 10+ / macOS / Linux

## Manual Docker Commands

### Build the image
```bash
docker build -t amr-data-harmonizer:latest .
```

### Run the container
```bash
docker run --rm -it \
    --name amr-data-harmonizer \
    -p 8501:8501 \
    -v "$PWD/data:/app/data" \
    -v "$PWD/logs:/app/logs" \
    -v "$PWD/config:/app/config" \
    amr-data-harmonizer:latest
```

### Stop the container
```bash
docker stop amr-data-harmonizer
```

### View logs
```bash
docker logs -f amr-data-harmonizer
```

## Troubleshooting

### Docker not running
- Start Docker Desktop
- Wait for it to fully start (whale icon in system tray)

### Port already in use
- Stop any existing containers: `docker stop amr-data-harmonizer`
- Or change the port mapping in docker-compose.yml

### Permission issues (Linux/Mac)
- Ensure Docker has permissions to access the mounted volumes
- May need to adjust file permissions: `chmod -R 755 data logs config`

### Rebuild after code changes
```bash
docker-compose build --no-cache
docker-compose up
```
