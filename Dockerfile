# 单容器：MariaDB + Nginx + Flask(Gunicorn) + ttyd（参考 ctf-docker-template web-lnmp-php73 / web-flask-python_3.10）
FROM python:3.10-slim-bullseye

LABEL maintainer="sqli-lab" description="Hello-CTF SQLi-labs single-container"

# bullseye 默认源无 ttyd 包：从 GitHub Release 安装预编译二进制（支持 amd64 / arm64）
ARG TTYD_VERSION=1.7.7
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        default-mysql-server \
        nginx \
        default-mysql-client \
        ca-certificates \
        curl \
        procps \
    && ARCH="$(dpkg --print-architecture)" \
    && case "$ARCH" in \
         amd64) TTYD_ASSET=x86_64 ;; \
         arm64) TTYD_ASSET=aarch64 ;; \
         *) echo "unsupported arch: $ARCH" >&2; exit 1 ;; \
       esac \
    && curl -fsSL -o /usr/local/bin/ttyd \
        "https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.${TTYD_ASSET}" \
    && chmod +x /usr/local/bin/ttyd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wsgi.py .
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY service/docker-entrypoint.sh /docker-entrypoint.sh
COPY db/init /docker-init

RUN chmod +x /docker-entrypoint.sh \
    && mkdir -p /var/log/nginx /run/mysqld \
    && chown -R mysql:mysql /run/mysqld

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
