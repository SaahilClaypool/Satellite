FROM ubuntu:latest
WORKDIR "/app"
EXPOSE 80
EXPOSE 8443


RUN echo "install" && apt update && \
    DEBIAN_FRONTEND="noninteractive" apt install -y \
    build-essential \
    cmake \
    autoconf \
    curl \
    git \
    libtool \
    libssl-dev \
    pkg-config

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir ./bin
ENV PATH="/app/bin:${PATH}"

COPY install_quiche.sh .
RUN bash install_quiche.sh

COPY install_curl.sh .
RUN bash install_curl.sh

RUN echo "install" && apt update && \
    DEBIAN_FRONTEND="noninteractive" apt install -y \
    libpcre3 libpcre3-dev zlib1g zlib1g-dev

COPY install_nginx.sh .
RUN bash install_nginx.sh

# seems like it needs to be re-installed after nginx install
RUN bash install_quiche.sh


COPY nginx.conf .
RUN echo "\n\n\n\n\n\n\n\n" | openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
RUN mkdir nginx-1.16.1/logs


EXPOSE 443
RUN mkdir /data && echo "test file" > /data/test

CMD nginx -c `pwd`/nginx.conf -g "daemon off;"
# # Network Tools Install

# RUN echo "install" && apt update && \
#     DEBIAN_FRONTEND="noninteractive" apt install -y \
#     tcpdump