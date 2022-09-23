---
date: 2017-10-26
comments: true
keywords:
- virsh
tags:
- virsh

title: Changing Libvirt bridge attachment in a running domain aka on-the-fly

---

At work I always prefer KVM hosts for reasons such as _flexible, free and GUI-less_. Yet I never bothered to go deeper into the networking features of Libvirt, so I only connect VMs to the host networks via Linux Bridges or OvS. Far far away from fancy virtual libvirt networks.

Even with this simple networking approach I recently faced a tedious task of reconnecting VMs to different bridges _on-the-fly_.  
My use case came from a need to connect a single traffic generator VM to the different access ports of virtual CPEs. Essentially this meant that I need to reconnect my traffic generator interfaces to different bridges back and forth:

<p align=center>
<img src=https://gitlab.com/rdodin/netdevops.me/uploads/2e1c09af2d208dc2dde78dcb6372059d/image.png/>
</p>

Apparently there is no such `virsh` command that will allow you to change bridge attachments for networking devices, so a bit of bash-ing came just handy.

<!--more-->

You know network interface device definition grepped from Libvirt XML format holds bridge association:

```xml
<!-- OMITTED -->
  <devices>
<!-- OMITTED -->
    <interface type='bridge'>
      <mac address='52:54:00:cd:75:4f'/>
      <source bridge='br12'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </interface>
<!-- OMITTED -->
```

The brute force approach would be to change the bridge identified in the domain definition, restart the domain and be with it. **Not sporty at all!**

Instead I decided that it would be good to have a script that for starters will take `domain_name`, `interface_name` and `new_bridge_id` and do the rest. So [`vifmove.sh`](https://gist.github.com/hellt/3626a753a74e3e5a950c71e6b294543f) (virsh interface move) was born.

This is a tiny bash script which does the job for me just fine:

<p align=center>
<img src="https://gitlab.com/rdodin/netdevops.me/uploads/f49318a2c6e475f3aacdb15abbd79d83/image.png"/>
</p>

Underneath its all simple, I leveraged `virsh update-device` command and just templated the interface definition XML file:

{{< gist hellt 3626a753a74e3e5a950c71e6b294543f >}}

If you find this one useful, feel free to add your ideas in the [gist](https://gist.github.com/hellt/3626a753a74e3e5a950c71e6b294543f) comments.
