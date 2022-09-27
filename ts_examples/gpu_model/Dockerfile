ARG BASE_IMAGE=nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu18.04

FROM ${BASE_IMAGE} AS compile-image
ARG BASE_IMAGE=nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu18.04
ENV PYTHONUNBUFFERED TRUE


ARG PYTHON_CMD=python3.8
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
    ${PYTHON_CMD} \
    ${PYTHON_CMD}-dev \
    ${PYTHON_CMD}-distutils \
    ${PYTHON_CMD}-venv \
    && ldconfig \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/* ~/*

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && ${PYTHON_CMD} get-pip.py \
    && rm get-pip.py
RUN update-alternatives --install /usr/bin/python python /usr/bin/${PYTHON_CMD} 1 \ 
    && update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3.8 1
RUN ${PYTHON_CMD} -m venv /home/venv
ENV PATH="/home/venv/bin:$PATH"
RUN python -m pip install -U pip setuptools

# needed by torchserve's metric??
RUN python -m pip install --no-cache-dir nvgpu

# Install pytorch related
# 1. torchserve==0.6.0 needs torch>=1.9.0
RUN export USE_CUDA=1
ARG CU_VER="cu113"
ARG TORCH_VER="1.11.0"
ARG TORCH_VISION_VER="0.12.0"
ARG TORCH_AUDIO_VER="0.11.0"
ARG TORCH_TEXT_VER="0.12.0"
RUN python -m pip install --no-cache-dir \
    torch==$TORCH_VER+$CU_VER \
    torchvision==$TORCH_VISION_VER+$CU_VER \
    torchaudio==$TORCH_AUDIO_VER \
    torchtext==$TORCH_TEXT_VER \
    --extra-index-url https://download.pytorch.org/whl/cu113
RUN python -m pip install --no-cache-dir captum torchserve torch-model-archiver

# install custom python packages
COPY ./requirements.txt /tmp/ts_env/requirements.txt
RUN python -m pip install -r /tmp/ts_env/requirements.txt

# Final image for production
FROM ${BASE_IMAGE} AS runtime-image
ENV PYTHONUNBUFFERED TRUE

ARG PYTHON_CMD=python3.8
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
    ${PYTHON_CMD} \
    ${PYTHON_CMD}-dev \
    ${PYTHON_CMD}-distutils \
    ${PYTHON_CMD}-venv \
    && ldconfig \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/* ~/*

RUN useradd -m model-server \
    && mkdir -p /home/model-server/tmp

COPY --chown=model-server --from=compile-image /home/venv /home/venv

ENV PATH="/home/venv/bin:$PATH"

# copy docker entrypoint
COPY ./ts_assets/dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh \
    && chown -R model-server /home/model-server
RUN mkdir /home/model-server/model-store && chown -R model-server /home/model-server/model-store

# # copy model file & assets
# COPY ./ts_assets/ts_log_config.xml /home/model-server/ts_log_config.xml
# COPY ./ts_assets/config.properties /home/model-server/config.properties
# COPY ./ts_assets/gpu_model.mar /home/model-server/model-store

EXPOSE 8080 8081 8082 7070 7071

USER model-server
WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]