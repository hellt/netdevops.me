---
date: 2025-05-01
comments: true
tags:
  - orbstack
  - kubernetes
---

# Using orbstack k8s in an orbstack machine

I use [orbstack](https://orbstack.dev) on a mac to have docker/k8s and vm hypervisor functionality and I love it.

My dev setup consists of a debian VM launched by Orbstack (Linux/Arm64) where I install regular linux tools and SDKs to keep myself as distant as possible from the Darwin fuckups.

I also use k8s cluster provided by Orbstack when I play with [Nokia EDA](https://docs.eda.dev) and other k8s-native things. The little challenge that I had with Orbstack-based k8s cluster was with the way it sets the kube api server address in the generated kubeconfig.  
By default, the kubeconfig for the orbstack cluster would use `127.0.0.1:<randport>` address, which is great if you want to use this api server from the mac shell directly, but as I use a dev VM, it would not work at all. Different localhosts, right?

So after I (re)spin the orbstack cluster I run this little script in my VM's shell to copy in the kubeconfig from a mac and replace the api server with the local DNS name `k8s.orb.local`, which works great both from mac and orb VM.

```bash
cp /mnt/mac/Users/$USER/.kube/config /home/$USER/.kube/config && \
sed -i 's/127.0.0.1/k8s.orb.local/g' ~/.kube/config && \
kubectl config use-context orbstack
```

I [asked](https://discord.com/channels/1106380155536035840/1355223497215049894/1355223497215049894) Orb people to make this a default (or a configurable setting), but I don't this this setting is something that they are willing to add.
