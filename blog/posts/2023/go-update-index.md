---
date: 2023-02-15
comments: true
tags:
  - go
---

# Refreshing Go package index for your package

It is quite frustrating to wait for pkg.go.dev to refresh your index, and I always forget how give it a [slight push](https://go.dev/doc/modules/publishing):

```bash
GOPROXY=proxy.golang.org go list -m example.com/mymodule@v0.1.0
```

The new version won't appear immediately, but at least it seems it will be quicker to show up.
