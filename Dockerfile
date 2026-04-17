# Usa Ubuntu 24.04 (LTS), ufficialmente supportato da Playwright
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    wget bc \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev libopenjp2-7-dev \
    libdbus-1-3 libatk1.0-0t64 libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libxkbcommon0 libasound2t64 \
    libatk-bridge2.0-0 libnss3 libnspr4 libcups2 libdrm2 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_23.x | bash -
RUN apt-get install -y --no-install-recommends nodejs

ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
ENV COMPOSER_ALLOW_SUPERUSER=1

RUN curl https://pyenv.run | bash
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /root/.bashrc && \
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /root/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc

ARG PYTHON_VERSION=3.13.2
ARG VENV_NAME=venv

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv virtualenv ${PYTHON_VERSION} ${VENV_NAME} && \
    pyenv global ${VENV_NAME}

COPY ./requirements.txt ./

RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

RUN mkdir -p ./DSS && mkdir -p ./PPP
COPY ./PolicyGapper ./PolicyGapper
RUN chmod +x ./PolicyGapper/run.sh
COPY ./PolicyGapper/google-play-scraper ./PolicyGapper/google-play-scraper
WORKDIR /app/PolicyGapper/google-play-scraper
RUN npm install

WORKDIR /app/PolicyGapper

CMD ["/bin/bash"]
