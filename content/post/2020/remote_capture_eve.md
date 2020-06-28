---
date: 2020-05-17T06:00:00Z
comment_id: remote_capture_eveng
keywords:
- wireshark
- eve-ng
tags:
- wireshark
- eve-ng

title: Using Wireshark remote capture with EVE-NG
---
The power of a packet capture is boundless... Sometimes its indeed a pcap that can save you nights of troubleshooting, so being able to get one quickly and easily is an ace up a neteng sleeve.  
In this post I'll show you how I use Wireshark's remote capture ability to sniff on packets running in EVE-NG without being need to install any custom plugins or packages from EVE.
<!--more-->

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

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>