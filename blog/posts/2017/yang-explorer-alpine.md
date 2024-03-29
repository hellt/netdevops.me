---
date: 2017-08-10
comments: true
keywords:
- Docker
- Yang Explorer
- Alpine
tags:
- yang
- docker
- yang explorer
- alpine linux

---

# Yang Explorer in a docker container based on Alpine

I wrote about the Yang Explorer in a docker quite some time ago, Yang Explorer was v0.6 at that time. Back then the motivation to create a docker image was pretty simple -- installation was a pain in **v0.6**, it is still a pain, but the official version bumped to **0.8(beta)**.

So I decided to re-build [an image](https://hub.docker.com/r/hellt/yangexplorer-docker/), now using Alpine Linux as a base image to reduce the size.

<!-- more -->

Just take a look how noob-ish I was to publish a `Dockerfile` like this:

```Dockerfile
FROM ubuntu:14.04
MAINTAINER Roman Dodin <dodin.roman@gmail.com>
RUN DEBIAN_FRONTEND=noninteractive apt-get update; apt-get install -y python2.7 python-pip python-virtualenv git graphviz libxml2-dev libxslt1-dev python-dev zlib1g-dev
RUN DEBIAN_FRONTEND=noninteractive git clone https://github.com/CiscoDevNet/yang-explorer.git
WORKDIR /yang-explorer
RUN bash setup.sh -y
RUN sed -i -e 's/HOST=\x27localhost\x27/HOST=$HOSTNAME/g' start.sh
CMD ["bash", "start.sh"]
```

Several unnecessary layers, using Ubuntu as a base -- these are the Docker-novice errors.

Few things changed in the [Yang Explorer](https://github.com/CiscoDevNet/yang-explorer) regarding the setup process, now you do not need to install explicitly all the dependencies, they will be installed using the packaged `requirements.txt` file, so our Dockerfile could be as short as this:

```Dockerfile
FROM alpine

LABEL maintainer="dodin.roman@gmail.com, netdevops.me"

RUN apk add --no-cache bash git python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    git clone https://github.com/CiscoDevNet/yang-explorer.git

WORKDIR /yang-explorer

RUN apk add --no-cache gcc py-crypto python-dev libffi-dev musl-dev openssl-dev libxml2-dev libxslt-dev && \
    bash setup.sh -y && \
    sed -i -e 's/HOST=\x27localhost\x27/HOST=$HOSTNAME/g' start.sh && \
    apk del musl-dev gcc

CMD ["bash", "start.sh"]
```

In the first `RUN` we write a layer with the tools that are needed to clone the official repo and in the second `RUN` we install build dependencies, go through setup process and uninstall unnecessary build dependencies to reduce the size.

> Compressed image size is **358Mb**. Uncompressed size is 1.9Gb

![Layers disposition](https://lh3.googleusercontent.com/pIf91DS4P8xb3FFuqVxWIjH3VLS3xS6DXp3UXAK3uJCveF9olt-ICnRj6peqqDnIY2k_WH5JEcl6Zc4LdoA476baHWDAywZ2NiSMG8WfQDd1leycyhdqA38s2hjyeN16bX9VGuXfdlc=w676-h397-no)

## Usage

To use this image:

1. Start the container

    ```shell
    docker run -p 8088:8088 -d hellt/yangexplorer-docker
    ```

2. Navigate your flash-capable browser to `http://<ip_of_your_docker_host>:8088`

## Differences with Robert Csapo image

Main differences are in the size:

- Compressed = 358Mb vs 588Mb
- Uncompressed = 1.9Gb vs 2.51Gb

## Links

- [My image on Docker Hub](https://hub.docker.com/r/hellt/yangexplorer-docker/)
- [Robert' image on Docker hub](https://hub.docker.com/r/robertcsapo/yang-explorer/)
- [Official Yang Explorer repo](https://github.com/CiscoDevNet/yang-explorer)
