---
date: 2017-07-18T12:00:00Z
keywords:
- virsh
- kvm
- xargs
tags:
- virsh
- qemu/kvm/libvirt

title: Destroy and Undefine KVM VMs in a single run

---

`virsh` is a goto console utility for managing Qemu/KVM virtual machines. But when it comes to deletion of the VMs you better keep calm - there is no single command to destroy the VM, its definition XML file and disk image.

Probably not a big problem if you have a long-living VMs, but if you in a testing environment it is naturally to spawn and kill VMs quite often. Lets see how `xargs` can help us with that routine.

<!--more-->

Right now my KVM hypervisor is busy with virtualizing small Nuage VNS environment where `4010_DEMO*` VMs are virtual SDN gateways:

```
[root@srv601 ~]# virsh list
 Id    Name                           State
----------------------------------------------------
 1     1-vsc1.pod60.cats              running
 2     1-vsc2.pod60.cats              running
 3     g1pe.play.cats                 running
 4     jenkins                        running
 5     dns                            running
 6     1-es1.pod60.cats               running
 7     1-vsd1.pod60.cats              running
 8     1-util1.pod60.cats             running
 18    4010_DEMO_I2                   running
 19    4010_DEMO_I1                   running
 22    4010_DEMO2_NSGI1               running
 23    4010_DEMO2_NSGI2               running
 24    4010_DEMO_1upl_testNSGI1       running
 25    4010_DEMO_1upl_testNSGI2       running 
```

And I really need to get these last six boys gone for good. With `virsh` one need to perform the following set of commands to achieve the goal:

```bash
# removing the last VM with a virsh domain name 4010_DEMO_1upl_testNSGI2
# first destroy the domain (you even cant pass multiple names)
$ virsh destroy 4010_DEMO_1upl_testNSGI2
Domain 4010_DEMO_1upl_testNSGI2 destroyed

# now undefine the domain
$ virsh undefine 4010_DEMO_1upl_testNSGI2
Domain 4010_DEMO_1upl_testNSGI2 has been undefined

# deleting the disk images
# assuming that all the VM-related data resides in that dir
$ rm -rf /var/lib/libvirt/images/4010_DEMO_1upl_testNSGI2
```

Too much typing for a simple task... Lets see how `xargs` comes into play!

# grep and xargs!
What we need to do is to filter out the target domain names and pass these names to the `virsh destroy && virsh undefine && rm -rf` commands.

First things first, lets get the names of the domains. `grep` is the tool of choice. 

```
# grep flags:
#   -o -- return only the matched group (not the whole line with match highlighted)
#   -E -- regular expression
virsh list --all | grep -o -E "(4010_DEMO\w*)"

# OUTPUT:
4010_DEMO_I2
4010_DEMO_I1
4010_DEMO2_NSGI1
4010_DEMO2_NSGI2
4010_DEMO_1upl_testNSGI1
```

Bingo, now its [`xargs`](https://man.cx/xargs) time:

> `xargs` reads items from the standard input, delimited by blanks or newlines, and executes the command (default is /bin/echo) one or more times with any initial-arguments followed by items read from standard input. Blank lines on the standard input are ignored.

```bash
virsh list --all | grep -o -E "(4010_DEMO\w*)" | \
xargs -I % sh -c 'virsh destroy % && virsh undefine % && rm -rf /var/lib/libvirt/images/%;'
```

The `xargs` flag `-I %` here allows us to substitute each `%` sign in the command with the `xargs` input argument. This effectively destroys the virsh domain along with its definition and disk image.

> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/1).