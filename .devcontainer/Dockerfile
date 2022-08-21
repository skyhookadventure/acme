FROM tensorflow/tensorflow:latest-gpu-jupyter

# Install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
    build-essential \
    curl \
    ffmpeg \
    git \
    libgl1-mesa-glx \
    libosmesa6 \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python-opengl \
    rsync \
    unzip \
    wget \
    xvfb

# Install pip (we need the latest version not the standard Ubuntu version, to
# support modern wheels)
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py

# Set python aliases
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install python dev dependencies
RUN pip install \
    jedi \
    jupyterlab \
    pytest \
    pylance \
    toml \
    yapf
