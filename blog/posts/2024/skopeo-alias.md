---
date: 2024-03-08
comments: true
tags:
  - skopeo
---

# Using skopeo container image

By now you know I hate to "install" things on the systems I work on, and that is because I have too many machines I carry work on. Hence, I prefer to containerize all the things and use handy aliases.

Here is one for skopeo to copy images between registries:

```bash
alias skopeo='sudo docker run --rm \
-v ~/.config/gcloud:/root/.config/gcloud:ro \
-v ~/.docker/config.json:/tmp/auth.json:ro \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /usr/bin/docker-credential-gcr:/usr/bin/docker-credential-gcr \
quay.io/skopeo/stable:v1.14'
```

```bash
$ skopeo --version
skopeo version 1.14.2
```

Note this quirky `docker-credential-gcr` binary mount, this is an authentication helper for skopeo to authenticate with GCP.
Other clouds might require other helpers or file mounts.