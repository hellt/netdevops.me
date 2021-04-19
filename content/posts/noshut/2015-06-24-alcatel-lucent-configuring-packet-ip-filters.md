---
title: Nokia (Alcatel-Lucent). Configuring Packet (IP) Filters
date: 2015-06-24T16:59:56+00:00
author: Roman Dodin
url: /2015/06/alcatel-lucent-configuring-packet-ip-filters/
draft: false
comment_id: ip-filter
tags:
  - SROS
  - Nokia
  - IP Filter
---
Packet filters (or in Cisco terminology Access Control Lists, aka ACL) are one of the most used tools in a network engineer's tool set. Blocking telnet/ssh access, restricting specific traffic flows, implementing policy-based routing or NATing - all of these tasks use IP filter's capabilities.

In this example I'll show you how to configure a basic SSH-blocking IP filter on a Nokia (Alcatel-Lucent) SROS running `TiMOS-B-12.0.R8`.
<!--more-->

According to the topology provided we will block SSH access to R1's system IP. This particular task could be done in various ways, but we will configure IP filter on R2 (applied to R2's interface `to_R4` in the incoming direction).

![pic](http://img-fotki.yandex.ru/get/15504/21639405.11b/0_83cc9_15a855d7_orig.png)

And the rule we will configure on R2 will be as follows:

  * If R2 receives a packet with a TCP destination port == 22 on interface `to_R4` it must drop it.

Lets begin with testing ssh access before any configuration is done:

```txt
A:R4# ssh 1.1.1.1
The authenticity of host '1.1.1.1 (1.1.1.1)' can't be established.
RSA key fingerprint is 9c:97:50:00:b0:f7:45:6f:9e:14:9a:06:11:ba:c6:e8.
Are you sure you want to continue connecting (yes/no)? yes

TiMOS-B-12.0.R8 both/i386 ALCATEL SR 7750 Copyright (c) 2000-2015 Alcatel-Lucent.
All rights reserved. All use subject to applicable license agreements.
Built on Fri Jan 9 09:55:30 PST 2015 by builder in /rel12.0/b1/R8/panos/main

admin@1.1.1.1's password:

A:R1# logout
Connection to 1.1.1.1 closed.
```

Working, as expected, good. Now lets block SSH access via IP filter configuration on R2:

```txt
## Creating ip-filter 
*A:R2# configure filter ip-filter 100 create

## Adding description (optional)
*A:R2>config>filter>ip-filter$ description "block ssh to 1.1.1.1/32"

## Adding name to a filter (optional)
*A:R2>config>filter>ip-filter$ filter-name "block_ssh_to_R1"

## Creating filter entry 
*A:R2>config>filter>ip-filter$ entry 10 create

## Specifying match statement for TCP packets, since SSH uses TCP
*A:R2>config>filter>ip-filter>entry$ match protocol "tcp"

## In match context specifying the SSH port number 
*A:R2>config>filter>ip-filter>entry>match$ dst-port eq 22

## optionally adding another match rule - Destination IP for R1
*A:R2>config>filter>ip-filter>entry>match$ dst-ip 1.1.1.1/32

## Leaving "match" context and adding DROP action to this filter's entry
*A:R2>config>filter>ip-filter>entry>match$ back
*A:R2>config>filter>ip-filter>entry$ action drop

## Moving one step back to filter's context and adding default action FORWARD, since implicitly it is DROP.
*A:R2>config>filter>ip-filter>entry$ back
*A:R2>config>filter>ip-filter$ default-action forward

## Lets see the whole filter config at once
*A:R2# configure filter ip-filter 100
*A:R2>config>filter>ip-filter# info
----------------------------------------------
            filter-name "block_ssh_to_R1"
            default-action forward
            description "block ssh to 1.1.1.1/32"
            entry 10 create
                match protocol tcp
                    dst-ip 1.1.1.1/32
                    dst-port eq 22
                exit
                action drop
            exit
----------------------------------------------
```

We created a simple IP filter, but it was not applied to any interface. Lets do this:

```txt
*A:R2# configure router interface "toR4"
*A:R2>config>router>if# ingress filter ip
ip 
 "block_ssh_to_R1"   100 ## you can refer to ip filter by its name or id

*A:R2>config>router>if# ingress filter ip "block_ssh_to_R1"

## make sure that ip filter applied correctly
*A:R2>config>router>if# info
----------------------------------------------
            address 10.2.4.2/24
            port 1/1/3
            ingress
                filter ip 100
            exit
            no shutdown
----------------------------------------------
```

![pic](http://img-fotki.yandex.ru/get/6314/21639405.11c/0_83cca_4dab30b3_orig.png)

Done, the filter has been applied to the appropriate interface and now should be running properly. Lets verify it by making SSH login attempt once again:

```txt
A:R4# ssh 1.1.1.1
Connect to address 1.1.1.1 failed  ## Our filter is working as expected
```

You use `show filter`  command to see the details of the newly created filter along with a number of packets matched by this filter:

```txt
*A:R2# show filter ip 100

===============================================================================
IP Filter
===============================================================================
Filter Id    : 100                              Applied        : Yes
Scope        : Template                         Def. Action    : Forward
Radius Ins Pt: n/a
CrCtl. Ins Pt: n/a
RadSh. Ins Pt: n/a
Entries      : 1
Description  : block ssh to 1.1.1.1/32
-------------------------------------------------------------------------------
Filter Match Criteria : IP
-------------------------------------------------------------------------------
Entry        : 10
Description  : (Not Specified)
Log Id       : n/a
Src. IP      : 0.0.0.0/0
Src. Port    : n/a
Dest. IP     : 1.1.1.1/32
Dest. Port   : eq 22
Protocol     : 6                                Dscp           : Undefined
ICMP Type    : Undefined                        ICMP Code      : Undefined
Fragment     : Off                              Src Route Opt  : Off
Sampling     : Off                              Int. Sampling  : On
IP-Option    : 0/0                              Multiple Option: Off
TCP-syn      : Off                              TCP-ack        : Off
Option-pres  : Off
Match action : Drop
Ing. Matches : 2 pkts (156 bytes)     ## See matched SSH packets
Egr. Matches : 0 pkts

===============================================================================
```

# Match-list and Port list

In the example above we used one ip address and one port to create our filter, but what if we need to match on the whole range of IP addresses and ports? You need to use match-list and port-list in this case:

```txt
*A:R1>config>filter# info
----------------------------------------------
        match-list
            ip-prefix-list "3_routes" create
                prefix 10.10.10.10/32
                prefix 20.20.20.20/32
                prefix 30.30.30.30/32
            exit
            port-list "allowed_ports" create
                port 22
                port 80
            exit
        exit
        ip-filter 10 create
            default-action forward
            entry 10 create
                match protocol tcp
                    dst-port port-list "allowed_ports"
                    src-ip ip-prefix-list "3_routes"
                exit
                action drop
            exit
        exit
----------------------------------------------
```

And that's all for this quick IP filter tutorial.

