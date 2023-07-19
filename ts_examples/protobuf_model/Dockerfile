FROM python:3.9.16
ENV PYTHONUNBUFFERED TRUE

RUN APT_INSTALL="apt-get install -y --no-install-recommends" \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
    openjdk-11-jre-headless \
    build-essential \
    cmake \
    apt-utils \
    ca-certificates \
    pkg-config \
    g++ \
    git \
    curl \
    yasm \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    && ldconfig \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/* ~/*

RUN python -m venv /home/venv
ENV PATH="/home/venv/bin:$PATH"
RUN python -m pip install -U pip setuptools

# needed by torchserve's metric??
RUN python -m pip install --no-cache-dir nvgpu pyyaml

# pytorch
RUN python -m pip install --no-cache-dir \
    torch==1.13.1 \
    torchvision==0.14.1 \
    torchaudio==0.13.1
# torchserve
RUN python -m pip install --no-cache-dir captum torchserve torch-model-archiver
# protobuf
RUN python -m pip install --no-cache-dir protobuf

# add model-server user
RUN useradd -m model-server && mkdir -p /home/model-server/tmp

# setup torchserve
COPY ./dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh && chown -R model-server /home/model-server
RUN mkdir /home/model-server/model-store && chown -R model-server /home/model-server/model-store
COPY ./config.properties /home/model-server/config.properties

EXPOSE 8080 8081 8082 7070 7071

USER model-server
WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve", "protobuf_model", "protobuf_model.mar"]