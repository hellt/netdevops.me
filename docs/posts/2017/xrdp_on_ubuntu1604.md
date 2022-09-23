---
date: 2017-08-25
comment_id: xrdp-ubuntu
keywords:
- xrdp
- ubuntu
tags:
- xrdp
- ubuntu

title: Installing xrdp 0.9.1 on Ubuntu 16.04 Xenial

---

[xrdp](http://www.xrdp.org/) is defacto the default RDP server for Linux systems sharing with VNC the _remote access solution_ olympus. I personally found it more resource friendly and feature rich compared to VNC solutions I tried.

The only problem I found with `xrdp` is that current Ubuntu LTS release Xenial 16.04 has a way outdated 0.6.1-2 version of xrdp in the packages repo. This version has no shared clipboard support, which makes remote support/remote access a tedious task. 

xrdp currently [in its 0.9.3 version](https://github.com/neutrinolabs/xrdp/releases) and it would be really nice to have a more recent package, rather than installing it from sources, like [many](http://c-nergy.be/blog/?p=8969) [solutions](https://ethernetworkingnotes.blogspot.ru/2017/01/install-latest-xrdp-release-on-ubuntu.html) [propose](https://www.google.ru/search?q=xrdp+0.9+ubuntu+16.04&newwindow=1&ei=GLufWbfIKYf4wAKK85mICA&start=0&sa=N&biw=1920&bih=935).

Well, no need to compile `xrdp` from sources (unless you want to), because you can leverage [a ppa from hermlnx](https://launchpad.net/~hermlnx/+archive/ubuntu/xrdp) that has `xrdp 0.9.1-7` already built for **amd64** and **i386** systems

```bash
# all you need is
sudo add-apt-repository ppa:hermlnx/xrdp
sudo apt-get update
sudo apt-get install xrdp
```

You can also try a `deb` package of `xrdp 0.9.2` -- https://github.com/suminona/xrdp-ru-audio

