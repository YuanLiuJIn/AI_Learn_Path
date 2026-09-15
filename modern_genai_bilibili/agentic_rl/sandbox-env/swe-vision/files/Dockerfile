FROM python:3.10-slim

# bash is required because the host starts the kernel via `bash -c ...`.
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    ipython==8.18.1 \
    ipykernel \
    jupyter_client \
    numpy \
    pillow \
    matplotlib \
    pandas \
    scipy \
    opencv-python-headless

WORKDIR /mnt/data