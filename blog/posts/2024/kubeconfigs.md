---
date: 2024-06-24
comments: true
tags:
  - kubernetes
---

# Managing multiple kubeconfigs by merging them

Recently I've been deploying k8s clusters on different cloud providers, with different automation stacks and in different configurations. As a result, I ended up with a bunch of of kubeconfigs polluting my `~/.kube` directory.

As much as `kubectl` is an swiss knife for all things k8s, it still can't quite make dealing with different kubeconfigs a breeze. The annoying part is that you have to have a single kubeconfig environment with all your clusters, users, contexts listed, and this is not the case when you have multiple kubeconfigs. So, naturally one would want to merge them into a single kubeconfig.

To do that I had to write a small script that does the following high level steps:

1. Backup existing `~/.kube/config` file: you don't want to lose your existing kubeconfig because you messed up something in your script or overwrote it with a wrong kubeconfig.
2. Find paths to all kubeconfig files in a particular directory and set them as a `KUBECONFIG` environment variable.
3. merge these kubeconfigs into a single `~/.kube/config` file.

Here is the script:

```bash
cp ~/.kube/config ~/.kube/bak/config_$(date +"%Y-%m-%d_%H:%M:%S")_bak && \
KUBECONFIG=$(find ~/.kube/cluster_configs -type f | tr '\n' ':') \
kubectl config view --flatten > ~/.kube/config
```

Nothing fancy, but it does the job. Essentially the rule of thumb that I follow now is to keep all my kubeconfigs in `~/.kube/cluster_configs` directory and run this script whenever I add or delete a kubeconfig in this directory. The resulting kubeconfig will contain all the contexts from all of the files and I could do `kubectl config use-context <context>` to switch between them.
