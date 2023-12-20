FROM python:3.11.7
ENV PYTHONUNBUFFERED TRUE

RUN APT_INSTALL="apt-get install -y --no-install-recommends" \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
    openjdk-17-jdk \
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

# pytorch
RUN python -m pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
    torch==2.0.1 \
    torchvision==0.15.2 

# torchserve
RUN python -m pip install --no-cache-dir nvgpu==0.10.0 pynvml==11.4.1 pyyaml==6.0.1
RUN python -m pip install --no-cache-dir torchserve==0.8.2 torch-model-archiver==0.8.2
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
CMD ["serve", "grpc_model", "grpc_model.mar"]