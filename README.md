# vLLM Celery

A Celery worker that processes batches of text prompts through a vLLM inference server.

## Overview

This repository provides a GPU-accelerated Celery task that sends prompts to a vLLM-compatible API (OpenAI-style completions endpoint) and returns responses. It supports both batch and sequential processing modes.

## Installation

### Docker

Pre-built images are available on Docker Hub:

```bash
docker pull zumoshi/vllm-celery:latest
# or a specific release tag
docker pull zumoshi/vllm-celery:<tag>
```

## Usage

Run the container with the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `RABBIT_HOST` | RabbitMQ broker hostname | Yes |
| `RABBIT_PW` | RabbitMQ broker password | Yes |
| `VLLM_MODEL` | Model used by vLLM | No (defaults to `google/gemma-3n-e4b-it`) |
| `MODE` | Processing mode: `batch` or `sequential` | No (defaults to `batch`) |

The worker connects to a vLLM server expected at `http://127.0.0.1:18000/v1`. Ensure this service is reachable within the same network context.

### Example

```bash
docker run --gpus all \
  -e RABBIT_HOST=rabbitmq.example.com \
  -e RABBIT_PW=secret \
  -e VLLM_MODEL=your-model \
  -e MODE=batch \
  --network your-network \
  zumoshi/vllm-celery:latest
```
