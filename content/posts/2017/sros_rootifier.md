---
date: 2017-11-22
comment_id: sros-root
keywords:
- SROS
- Nokia
- 7750SR
tags:
- SROS
- Nokia

title: SROS Rootifier or how to flatten 7750 SR config

---

Back in the days when I mostly did routing stuff I spent the whole day configuring SROS devices via SSH. And once in a while I saw that SSH session or its server part (or even underlying connection) glitched, resulting in a corrupted lines feeded to the device.

What was also quite common is to make a mistake (i.e. syntax one) in a single line and watch like the rest of config got applied to the wrong context.

These sad facts pushed me to create a **rootifier** CLI script, that was converting tree-like SROS config into flattented (aka rooted) fashion.

![rootifier](https://gitlab.com/rdodin/netdevops.me/uploads/29184e488b07d8b5efb77d367a9e41ce/image.png)

Now I decided to make a web service of that script, that is publicly available at http://rootifier.netdevops.me/

<!--more-->

## SROS config structure
As you well aware, SROS config is of indent-based tree-like structure:
```bash
configure
--------------------------------------------------
echo "System Configuration"
--------------------------------------------------
    system
        name "ntdvps"
        location "netdevops.me"
        chassis-mode d
```
It is readable for a human, but it is much safer to apply batch config using the flattened structure, where each command is given in a full context fashion. Passed through a rootifier our example will transform as displayed:
```
/configure system name "ntdvps"
/configure system location "netdevops.me"
/configure system chassis-mode d
```
Now each command has a full path applied and even making an error in a single command will not affect the rest of them, making **configuration safer**.

Yeah, probably applying rootifier to a short config snippets make a little sense, but pushing a solid 300+ lines config to a fresh box would definitely benefit from rootifying.

Take a look [at this diff](https://www.diffchecker.com/dHwUDWUw) made for a real-life config of SROS box before and after rootifying. Not only **it downsized from 1600 lines to 600**, it also **became safer** to push via console/SSH connection.

## Usage scenarios and limitations
As I explain in the _Usage and Limitations_ section rootifier accepts

* either the whole config file content
* or any part of it, that starts under `configure` section

For instance, valid config portions are:

**1. Full config**

As you see it via `admin display-config` or in the config file you can copy it it as a whole, or from the beginning to the desired portion
```
# TiMOS-B-14.0.R4 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2016 Nokia.
# All rights reserved. All use subject to applicable license agreements.
# Built on Thu Jul 28 17:26:11 PDT 2016 by builder in /rel14.0/b1/R4/panos/main

# Generated WED NOV 22 12:22:35 2017 UTC

exit all
configure
#--------------------------------------------------
echo "System Configuration"
#--------------------------------------------------
    system
        name "pe.pod62.cats"
        chassis-mode d
        dns
        exit
        snmp
        exit
        time
            ntp
                server 10.167.55.2
                no shutdown
            exit
            sntp
                shutdown
            exit
            dst-zone CEST
                start last sunday march 02:00
                end last sunday october 03:00
            exit
            zone UTC
        exit
```

**2. Portion of the config that starts with 4 spaces exactly**
```
    system
        name "pe.pod62.cats"
        chassis-mode d
        dns
        exit
        snmp
        exit
        time
            ntp
                server 10.167.55.2
                no shutdown
            exit
```

**3. Any part of the config with specified context**

Since rootifier does not know the config structure and makes decision only by indentations in the passed config, it can not say what context was this snippet from:
```
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            prefix-list "loopback"
                prefix 1.1.1.1/32 exact
            exit
            policy-statement "export_loopback"
                entry 10
                    from
                        prefix-list "loopback"
                    exit
                    action accept
                    exit
                exit
            exit
            commit
        exit
```
Thus, rootifier will not render the rooted version of this snippet correctly.

Now we, of course, know that policies are configured under the `/configure router` context, so we can help rootifier by setting the context:
```
    # put a missing context before your snippet
    router
        policy-options
            begin
            prefix-list "loopback"
                prefix 1.1.1.1/32 exact
            exit
            policy-statement "export_loopback"
                entry 10
                    from
                        prefix-list "loopback"
                    exit
                    action accept
                    exit
                exit
            exit
            commit
        exit
```

You can even extract deeply nested config portions and rootify them, just specify the missing context:
```
    # missing context
    router policy-options
            # original snippet
            prefix-list "Customer_1"
                prefix 10.10.55.0/24 exact
                prefix 10.10.66.0/24 exact
            exit
            prefix-list "Customer_2"
                prefix 172.10.55.0/24 exact
                prefix 172.10.66.0/24 exact
            exit
            community "East" members "65510:200"
            community "West" members "65510:100"
            community "Customer_2" members "65510:2"
```

## PS
Rootifier web service is a [Flask application deployed in a container](https://netdevops.me/2017/flask-application-in-a-production-ready-container/) in ElasticBeanstalk on AWS. Probably I will write about this way of deploying the code in a later post.

Rootifier [source code](https://github.com/hellt/Rootifier) is hosted on Github.

A similar work (CLI version) was done by honorable **David Roy** - [transcode-sros](https://github.com/door7302/transcode-sros).

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>