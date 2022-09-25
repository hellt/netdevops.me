---
date: 2020-05-17
comments: true
keywords:
- wireshark
- eve-ng
tags:
- wireshark
- eve-ng

---
# Using Wireshark remote capture with EVE-NG

The power of a packet capture is boundless... Sometimes its indeed a pcap that can save you nights of troubleshooting, so being able to get one quickly and easily is an ace up a neteng sleeve.  
In this post I'll show you how I use Wireshark's remote capture ability to sniff on packets running in EVE-NG without being need to install any custom plugins or packages from EVE.

<!-- more -->

EVE-NG provides some integration packs with wrappers around Wireshark's remote capture feature to make capturing a one-click task. The integration pack has all the needed software and some Duct tape to make it all work:

```
plink 0.73 (for wireshark)
all necessary wrappers
It will modify windows registry files for proper work
```

I would rather want to keep my registry untouched for a simple task like sniffing the packets from a remote location, therefore I always use Wireshark remote capture without installing any client packs from Eve. It feels more "appropriate", though I wouldn't mind to install the pack in a VM that I don't care about much.

So, you are perfectly capable of sniffing on packets running in EVE by having Wireshark alone. Thats the procedure:

1. Install wireshark
2. In the EVE lab view grep the link name of an interface you want to capture from  
    ![pic](https://gitlab.com/rdodin/pics/-/wikis/uploads/210dd1dc98ba25f1981c7e5d552afae0/image.png)  
    **2.1** right click on the device you want to capture from  
    **2.2** select "Capture" menu  
    **2.3** move mouse over the interface you want to capture from  
    **2.4** get the interface name (`vunl0_1_0` in my example)
3. Open Wireshark and choose remote capture in the list of the capture interfaces  
    ![pic2](https://gitlab.com/rdodin/pics/-/wikis/uploads/72cbfcf02025615e5edb73ee04ff5f17/image.png)
4. Enter the address of your EVE hypervisor (can use names of your systems from ssh_config)
    ![pic3](https://gitlab.com/rdodin/pics/-/wikis/uploads/1bb17b52b8660bfb70bab1e148262d85/image.png)
5. Type down the interface name you got in step 2 (the `capture filter` statement generates automatically)
    ![pic4](https://gitlab.com/rdodin/pics/-/wikis/uploads/cedfd848bac4305e946f2eccca0f2471/image.png)
6. Start capturing!

It might look like a lot of manual steps from the first sight, but it takes actually 10 seconds, since you only need to memorize the link name and type it once in the wireshark interface.
