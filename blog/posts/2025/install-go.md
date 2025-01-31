---
date: 2025-01-31
comments: true
tags:
  - go
---

# Managing multiple Go versions

When dealing with several Go projects you inevitably end up needing more than one Go version installed and selected correctly for a given project.

Somehow I always forget how I do this when I need to fix a new version for another project, so here is what I do for the future me:

1. Install the target release Go downloader. For example, for `go1.22.11`

    ```bash
    go install golang.org/dl/go1.22.11@latest
    ```

2. Now download the actual sdk

    ```bash
    go1.22.11 download
    ```

3. Now for whatever project that you want to set this version for, create the `direnv`'s `.envrc` file and set the path accordingly:

```bash
PATH=~/sdk/go1.22.11/bin:$PATH
```
