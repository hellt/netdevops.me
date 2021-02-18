---
date: 2021-02-18T06:00:00Z
comment_id: uksm
keywords:
  - uksm
  - ubuntu
tags:
  - uksm
  - ubuntu

title: How to patch Ubuntu 20.04 Focal Fossa with UKSM?
---
<!--more-->

Running multiple VMs out of the same disk image is something we, network engineers, do quite often. A virtualized network usually consists of a few identical virtualized network elements that we interconnected with links making a topology.

![topo](https://img-fotki.yandex.ru/get/6605/21639405.11c/0_86301_84e43902_orig.png)

In the example above we have 7 virtualized routers in total, although we used only two VM images to create this topology (virtualized Nokia router and it's Juniper vMX counterpart). Each of this VMs require some memory to run, for the simplicity, lets say each VM requires 5GB of RAM.

So roughly, the above topology will claim 30-35GB of RAM in order to operate. Enriching the topology by adding more VMs of the same type will continue to push for more memory, thus running big topologies often becomes an exercise of hunting for RAM.

Luckily, there are technologies like Kernel Same Merging (KSM) and it's enhanced version Ultra-KSM (UKSM) that are able to lift the memory requirement for use cases like above. In a nutshell, they allow to merge mem pages of the same content, effectively reusing the same memory pages between virtual machines.

> from [UKSM usenix paper](https://www.usenix.org/system/files/conference/fast18/fast18-xia.pdf)  
> Memory deduplication can reduce memory footprint by eliminating redundant pages. This is particularly true when similar OSes/applications/data are used across different VMs.
> Essentially, memory deduplication detects those redundant pages, and merges them by enabling transparent page sharing.

Although UKSM is not a silver bullet for every application and use case, it tends to be a very good fit for hypervisors used to run virtualized networking topologies. For that reason the EVE-NG network emulation platform embeds UKSM in their product.

So I decided to bring UKSM to my Ubuntu 20.04 VM that I use to launch virtualized routers and containers to witness the benefits/issues of having it.

![uksm](https://gitlab.com/rdodin/pics/-/wikis/uploads/5ac1a3e597d26fbf94d18e7d898e6a7c/image.png)

The results look promising. Running 6 VMs with a system memory footprint of one is a solid memory optimization, especially considering that performance penalty is something we can bare in a lab where we mostly play with control plane features.

[![uksm-compare](https://gitlab.com/rdodin/pics/-/wikis/uploads/55317652924b2ad3d083cf6719b5cd1e/image.png)](https://gitlab.com/rdodin/pics/-/wikis/uploads/55317652924b2ad3d083cf6719b5cd1e/image.png)

Now if you want to bring UKSM to your hypervisor you will need to jump through some hoops, as UKSM is a kernel feature that is not available as a module. This means that you need to build a kernel with UKSM enabled, and that might be a barrier too high for some of you. It was for me, until I spent a night trying multiple things until it worked, so let me share with you the process and the outcomes so that you can rip the benefits without having all the trouble of trial-and-error routine.

#### 0 TL;DR
* Download UKSM patches
* Download kernel source
* Apply UKSM patch
* Build kernel
* Install kernel

## 1 Get UKSM patches
As mentioned above, UKSM is a kernel feature and the way it is distributed nowadays is via `patch` files that are available in [this Github repo](https://github.com/dolohow/uksm). So our first step is cloning this repo to get the patches for recent (4.x and 5.x) kernels. Easy start.

## 2 Get the kernel source code
As the UKSM patches need to be applied to a kernel source code, we need to get one. Here things can get a tad complicated.

There are many different kernels out there:
* vanilla Linux kernels blessed by Linux himself
* distribution kernels (Debian, Ubuntu, Fedora, etc)
* third party kernels with the best hacks

The UKSM patches were created against the vanilla Linux kernel, but my Ubuntu VM runs a kernel that was produced by Ubuntu team.

```bash
# on Ubuntu 20.04
uname -a
Linux kernel-build 5.4.0-48-generic #52-Ubuntu SMP Thu Sep 10 10:58:49 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```
Vanilla linux kernel uses X.Y.Z versioning. If anything is appended after X.Y.Z (like `-48-generic`) in my case, it indicates that the kernel comes from a distributor (Ubuntu in my case).

> Things that didn't work:  
> 1 At first I tried to download the original Linux kernel, but the build process failed without giving me a good explanation.  
> 2 Download latest 5.4 kernel from Ubuntu - UKSM patch didn't apply, as the code has changed apparently

After multiple rinse-repeat iterations I found out that I can take the Ubuntu kernel `5.4.0-48.52` as UKSM patch applies to it no problem and the build succeeds.

How did I get one? Oh, that is also something worth documenting, as the path to knowing it is paved with broken links and articles dated early 2000s. First, go [here](https://git.launchpad.net/~ubuntu-kernel/ubuntu/+source/linux/+git/focal/refs/) and check what tags/branches are available for Focal release of Ubuntu. Once the tag/branch name is found, pull this one only, to save on data transfer:

```bash
# fetch single branch/tag only
git clone --depth 1 --single-branch --branch Ubuntu-5.4.0-48.52 https://git.launchpad.net/\~ubuntu-kernel/ubuntu/+source/linux/+git/focal
```

Fast forward 180MB of kernel source code and you have it in `focal` directory. Next is patching.

## 3 Patch the source
To embed the UKSM code into the kernel code we need to use the [patch](https://en.wikipedia.org/wiki/Patch_(Unix)) utility.

In the UKSM repo we cloned in step 1 we have patch files per kernel MAJOR.MINOR version. As we downloaded the Ubuntu kernel 5.4.0-something, let's try and apply the patch from `uksm-5.4.patch` patch file.

```bash
# assuming we cloned UKSM repo in ~
cd focal
patch -p1 < ~/uksm/v5.x/uksm-5.4.patch
```

> **patch command must not return any failures. If it does, do not proceed!** 

This is the most important step, the patch must apply cleanly, meaning that if you see any `FAILURE` strings in its output (or `echo $?` doesn't return `0`) it means the patch is not compatible with the kernel.

The tricky part was to find the `Ubuntu kernel+patch file` combination that didn't result in an error. For me the merry pair was `Ubuntu-5.4.0-48.52 + uksm-5.4.patch`.

## 4 Build the patched kernel
Once the patch is cleanly applied we build the kernel.

> Here I feel obliged to say that it was my first kernel build, so the explanations are surely not technically correct, but it works, so why not sharing my view on it.

To build the kernel we fist need to create the build configuration file. As we use the kernel that we actually run (5.4.0-48) we can reuse the existing kernel configuration:

```bash
# being in focal directory
make oldconfig
```

This command will run the config generation script and it prompted me that there is a UKSM config option added (as a result of a UKSM patch) and if I want to use it instead of the default KSM option. I typed `1` in the prompt confirming that I need UKSM to be an acting KSM feature. That is the only input that was needed.

After the config is made, start the build process:

```bash
# j8 is the number of cores I had on my machine
make -j8 deb-pkg LOCALVERSION=-uksm
```

40 minutes later I had four debian packages created:

```bash
~/focal #Ubuntu-5.4.0-48.52 !15 ?16                                                              root@devbox-u20 08:36:17
❯ ls -la ../*deb
-rw-r--r-- 1 root root  11441428 Feb 17 20:50 ../linux-headers-5.4.60-uksm_5.4.60-uksm-1_amd64.deb
-rw-r--r-- 1 root root 910558572 Feb 17 20:58 ../linux-image-5.4.60-uksm-dbg_5.4.60-uksm-1_amd64.deb
-rw-r--r-- 1 root root  61261664 Feb 17 20:50 ../linux-image-5.4.60-uksm_5.4.60-uksm-1_amd64.deb
-rw-r--r-- 1 root root   1071476 Feb 17 20:50 ../linux-libc-dev_5.4.60-uksm-1_amd64.deb
```

## 5 Install the kernel
Out of these four files I needed to install all but `*dbg*` files:

```bash
sudo dpkg -i ../linux-headers-5.4.60-uksm_5.4.60-uksm-1_amd64.deb
sudo dpkg -i ../linux-image-5.4.60-uksm_5.4.60-uksm-1_amd64.deb
sudo dpkg -i ../linux-libc-dev_5.4.60-uksm-1_amd64.deb
```

Once this is done, update your grub config to have the new kernel load by default:

```bash
sudo update-grub
```

And `reboot`. Done!

## 6 Verify UKSM is working
After the reboot, ensure that your new kernel is running by examining `uname -r` output. It should match the new version.

Launch some VMs, and check the memory consumption as well as the number of sharing pages with `cat /sys/kernel/mm/uksm/pages_sharing`.

## 7 Get the built kernel
If you don't want to build a kernel yourself (and one night lost I can see why), I packaged the deb files into a bare container which you can pull and copy the files from to install the kernel on your Ubuntu machine:

```bash
# pull the container and copy the deb files out of it
docker pull ghcr.io/hellt/ubuntu-5.4.60-uksm:0.1
id=$(docker create ghcr.io/hellt/ubuntu-5.4.60-uksm:0.1 foo)
docker cp $id:/uksm-kernel .
```

All you need to do is to start with step 5 and you should be all good. Thanks for tuning in!

## PS. KSM vs UKSM
There is a KSM kernel feature that allows you to achieve some memory sharing via a similar mechanisms. It can be that KSM will deliver a similar performance on your setup, and being included in your kernel by default it might be worth checking out.

The following resources will help you start with KSM:

* https://gist.github.com/mapuo/17e3b253222172c1659782eb14150c3a
* https://www.linux-kvm.org/page/KSM#Enabling_KSM
* https://openterprise.it/2019/03/enable-ksm-kernel-same-page-merging-on-fedora/
* https://rotelok.com/enable-ksm-centos7-debian/
* https://www.kernel.org/doc/Documentation/vm/ksm.txt

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>