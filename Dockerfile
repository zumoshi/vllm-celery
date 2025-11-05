FROM vastai/vllm:v0.11.0-cuda-12.9-pytorch-2.8.0-py312

RUN bash -c ". /venv/main/bin/activate && pip install 'celery[zstd]'"

RUN mkdir /root/gpu
COPY ./gpu/tasks.py /root/gpu/

# Add Celery wrapper script
RUN cat > /opt/supervisor-scripts/celery-wrapper.sh <<EOF
#!/bin/bash
set -e

. /venv/main/bin/activate

VLLM_URL="http://127.0.0.1:18000/health"
MAX_RETRIES=90
SLEEP_INTERVAL=3

echo "Waiting for vllm service to be ready..."
cd /root/

for i in $(seq 1 $MAX_RETRIES); do
    if curl -fs $VLLM_URL >/dev/null 2>&1; then
        echo "vllm is ready. Starting Celery..."
        exec celery -A gpu.tasks worker --loglevel=info --queues=gpu
    fi
    echo "vllm not ready, retrying in $SLEEP_INTERVAL seconds... ($i/$MAX_RETRIES)"
    sleep $SLEEP_INTERVAL
done

echo "vllm did not become ready in time, exiting."
exit 1
EOF

RUN cat > /etc/supervisor/conf.d/celery.conf <<EOF
[program:celery]
environment=PROC_NAME="%(program_name)s"
command=/opt/supervisor-scripts/celery-wrapper.sh
autostart=true
autorestart=unexpected
exitcodes=0
startsecs=0
stopasgroup=true
killasgroup=true
stopsignal=TERM
stopwaitsecs=10
stdout_logfile=/dev/stdout
redirect_stderr=true
stdout_events_enabled=true
stdout_logfile_maxbytes=0
stdout_logfile_backups=0
EOF


