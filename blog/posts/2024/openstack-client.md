---
date: 2024-01-11
comments: true
tags:
  - openstack
  - docker
---

# OpenStack Client Container Image

I like the portability, managability and package manager agnostic nature of container images. Especially for the tools I use couple of times a month. And even more so for Python tools that don't have native wheels for all their dependencies. Like OpenStack Client.

So I built a small [multi-stage Dockerfile](https://github.com/hellt/dockerfiles/blob/main/openstack-client/openstack-client.dockerfile) to build a container image with OpenStack Client and all its dependencies. It's based on the official Python image and has a slim footprint:

```Dockerfile
--8<-- "https://raw.githubusercontent.com/hellt/dockerfiles/main/openstack-client/openstack-client.dockerfile"
```

You can pull the image from [ghcr](https://github.com/hellt/dockerfiles/pkgs/container/openstack-client):

```
docker pull ghcr.io/hellt/openstack-client:6.4.0
```

To use this image you first need to source the env vars from your openrc file:

```
source myopenrc.sh
```

Then I prefer to install the alias `openstack` to my shell so that it feels like I have the client installed locally:

```bash
alias openstack="docker run --rm -it \
    -e OS_AUTH_URL=${OS_AUTH_URL} -e OS_PROJECT_ID=${OS_PROJECT_ID} \
    -e OS_USER_DOMAIN_NAME=${OS_USER_DOMAIN_NAME} \
    -e OS_PROJECT_NAME=${OS_PROJECT_NAME} \
    -e OS_USERNAME=${OS_USERNAME} -e OS_PASSWORD=${OS_PASSWORD} \
    ghcr.io/hellt/openstack-client:6.4.0 openstack $@"
```

Then you can use the client as usual:

```
❯ openstack server list
+-----------------------------+----------------+--------+-----------------------------+------------------------------+---------------------+
| ID                          | Name           | Status | Networks                    | Image                        | Flavor              |
+-----------------------------+----------------+--------+-----------------------------+------------------------------+---------------------+
| 0fa75185-0f76-482f-8cc3-    | k8s-w3-411e6d7 | ACTIVE | k8s-net-304e6df=10.10.0.11  | nesc-baseimages-             | ea.008-0024         |
| 38e4d60212c8                |                |        |                             | debian-11-latest             |                     |
-- snip --
```
