---
date: 2024-02-05
comments: true
tags:
  - bash
---

# Formatting bash

Whenever I need to format `bash` scripts I use the mvdan's shfmt - <https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd> as a docker container:

```bash
sudo docker run --rm -u "$(id -u):$(id -g)" -v $(pwd):/mnt -w /mnt mvdan/shfmt:v3 -w utils/if-wait.sh
```
