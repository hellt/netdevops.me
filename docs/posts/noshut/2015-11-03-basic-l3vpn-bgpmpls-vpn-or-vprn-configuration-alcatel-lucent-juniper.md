---
title: Basic L3VPN (BGP/MPLS VPN or VPRN) configuration on Nokia (Alcatel-Lucent) SROS & Juniper MX
date: 2015-11-03
author: Roman Dodin
url: /2015/11/basic-l3vpn-bgpmpls-vpn-or-vprn-configuration-alcatel-lucent-juniper/
comment_id: l3vpn-tutor
keys:
  - Nokia
  - Juniper
  - L3VPN
  - VPRN
  - BGP
tags:
  - Nokia
  - Juniper
  - L3VPN
  - VPRN
  - BGP
---

The topic of this post is **Layer 3 VPN** (L3VPN or VPRN as we call it in SROS) configuration, and I decided to kill two birds with one stone by inviting Juniper vMX to our cozy SROS environment.

The BGP/MPLS VPN ([RFC 4364](https://tools.ietf.org/html/rfc4364)) configuration will undergo the following milestones:

- PE-PE relationship configuration with VPN IPv4 address family introduction
- PE-CE routing configuration with both BGP and OSPF as routing protocols
- Export policy configuration for advertising VPN routes on PE routers
- AS override configuration
- and many more

We'll wrap it up with the Control Plane/Data Plane evaluation diagrams which help a lot with understanding the whole BGP VPN mechanics. Take your seats, and buckle up!
<!--more-->

The topology I use throughout this tutorial consists of two customers (namely Alcatel and Juniper) which have two remote sites and want to get connectivity between them by means of an L3VPN service:

[![pic](http://img-fotki.yandex.ru/get/6605/21639405.11c/0_86301_84e43902_orig.png)](http://img-fotki.yandex.ru/get/6605/21639405.11c/0_86301_84e43902_orig.png)

![pic](http://img-fotki.yandex.ru/get/9356/21639405.11c/0_86302_9307f47e_orig.png)

We start off with ISIS (any IGP would suffice) running smoothly in our provider core so every router can reach every other's loopback address. Another prerequisite is to have an _MPLS enabled_ core, since L3VPN uses MPLS encapsulation for dataplane communication. I configured RSVP-TE tunnels between PE routers for this tutorial in the way that PE1_ALU can resolve PE2_JUN (and vice versa) loopback address via RSVP-TE tunnel.

Lets have a look at the relevant configuration blocks on the three routers PE1_ALU, P1_ALU and PE2_JUN

PE1_ALU:

```txt
A:PE1_ALU>config>router# info 
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 10.10.10.1/32
            no shutdown
        exit
        interface "toP1"
            address 10.99.99.0/31
            port 1/1/2
            no shutdown
        exit
        autonomous-system 100
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 49.10
            traffic-engineering
            reference-bandwidth 100000000
            level 1                   
                wide-metrics-only
            exit
            interface "system"
                no shutdown
            exit
            interface "toP1"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
#--------------------------------------------------
echo "MPLS Configuration"
#--------------------------------------------------
        mpls
            interface "system"
                no shutdown
            exit
            interface "toP1"
                no shutdown
            exit
        exit
#--------------------------------------------------
echo "RSVP Configuration"
#--------------------------------------------------
        rsvp
            interface "system"
                no shutdown
            exit
            interface "toP1"
                no shutdown
            exit
            no shutdown
        exit
#--------------------------------------------------
echo "MPLS LSP Configuration"
#--------------------------------------------------
        mpls
            path "loose"
                no shutdown
            exit
            lsp "toPE2"
                to 10.10.10.3
                cspf
                primary "loose"
                exit
                no shutdown
            exit
            no shutdown
        exit

## Verification commands
A:PE1_ALU# show router route-table 10.10.10.3

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.10.3/32                                 Remote  ISIS      01d00h57m  15
       10.99.99.1                                                   200
-------------------------------------------------------------------------------


A:PE1_ALU# show router tunnel-table 10.10.10.3

===============================================================================
Tunnel Table (Router: Base)
===============================================================================
Destination           Owner Encap TunnelId  Pref     Nexthop        Metric
-------------------------------------------------------------------------------
10.10.10.3/32         rsvp  MPLS  1         7        10.99.99.1     200
-------------------------------------------------------------------------------
```

P1_ALU:

```txt
A:P1_ALU>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 10.10.10.2/32
            no shutdown
        exit
        interface "toPE1"
            address 10.99.99.1/31
            port 1/1/1
            no shutdown
        exit
        interface "toPE2"
            address 10.99.99.2/31
            port 1/1/2
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 49.10
            traffic-engineering
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            interface "system"
                no shutdown
            exit
            interface "toPE1"
                interface-type point-to-point
                no shutdown
            exit
            interface "toPE2"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
#--------------------------------------------------
echo "MPLS Configuration"
#--------------------------------------------------
        mpls
            interface "system"
                no shutdown
            exit
            interface "toPE1"
                no shutdown
            exit
            interface "toPE2"
                no shutdown
            exit
        exit
#--------------------------------------------------
echo "RSVP Configuration"
#--------------------------------------------------
        rsvp
            interface "system"
                no shutdown
            exit
            interface "toPE1"
                no shutdown
            exit
            interface "toPE2"
                no shutdown
            exit
            no shutdown
        exit
#--------------------------------------------------
echo "MPLS LSP Configuration"
#--------------------------------------------------
        mpls
            no shutdown
        exit
----------------------------------------------
```

PE2_JUN:

```txt
root@PE2_JUN# show 
## Last changed: 2015-10-20 17:08:01 UTC
version 14.1R1.10;
<... omitted >
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 10.99.99.3/31;
            }
            family iso;
            family mpls;
        }
    }
    lo0 {
        unit 0 {
            family inet {
                address 10.10.10.3/32;
            }
            family iso {
                address 49.1001.0010.0100.0300;
            }
            family mpls;
        }
    }
}
routing-options {
    autonomous-system 100;
}
protocols {
    rsvp {
        interface ge-0/0/0.0;
    }
    mpls {
        label-switched-path toPE1 {
            to 10.10.10.1;
        }
        interface ge-0/0/0.0;
    }
    isis {
        reference-bandwidth 100g;
        level 1 wide-metrics-only;
        level 2 wide-metrics-only;
        interface ge-0/0/0.0 {
            point-to-point;
            level 2 disable;
        }
        interface lo0.0;
    }
}

## Verification commands
root@PE2_JUN# run show route 10.10.10.1

inet.0: 6 destinations, 6 routes (6 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

10.10.10.1/32      *[IS-IS/15] 1d 00:10:30, metric 200
                    > to 10.99.99.2 via ge-0/0/0.0

inet.3: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

10.10.10.1/32      *[RSVP/7/1] 11:22:07, metric 200
                    > to 10.99.99.2 via ge-0/0/0.0, label-switched-path toPE1
```

## BGP L3VPN terminology

Before we dive deep into the BGP L3VPN configuration it is necessary to refresh on some basic theory. To get a deeper and broader knowledge on the following topic please consider Juniper's _JUNOS MPLS and VPNs student guide_ and [_Alcatel-Lucent's Service Routing Architect guide_](https://www.amazon.com/Alcatel-Lucent-Service-Routing-Architect-Self-Study/dp/111887515X).

### VRFs

In order to maintain different customer's routes independently PE routers use separate logical routing tables called **Virtual Routing and Forwarding (VRF)**.
{{< admonition type=info title="RFC 4364. VRFs: Multiple Forwarding Tables in PEs" open=false >}}
Each PE router maintains a number of separate forwarding tables. One of the forwarding tables is the "default forwarding table". The others are "VPN Routing and Forwarding tables", or "VRFs".

3.1. VRFs and Attachment Circuits<br /> Every PE/CE attachment circuit is associated, by configuration, with one or more VRFs. An attachment circuit that is associated with a VRF is known as a "VRF attachment circuit".

In the simplest case and most typical case, a PE/CE attachment circuit is associated with exactly one VRF. When an IP packet is received over a particular attachment circuit, its destination IP address is looked up in the associated VRF. The result of that lookup determines how to route the packet.
{{< /admonition >}}

Provider Edge routers must have a VRF configured for each connected site. VRFs are totally separated in routers control plane by default, so we can depict VRFs as the routers on their own caged in a single hardware unit:

![pic](http://img-fotki.yandex.ru/get/5212/21639405.11c/0_86305_d80b5336_orig.png)

VRFs also remain local to the corresponding hosting PE routers and their number representation or names are never propagated to the other PEs. In our example we have four VRFs in total, two VRFs (VRF Alcatel and VRF Juniper) per PE.

### Route Distinguisher

Since one router can have many routing instances (VRFs) inside, it is necessary to help a router to distinct between the different routes in the different VRFs. It is highly likely that customers connected to a single PE will have overlapping IP addresses and this will potentially lead to troubles as the router won't know which customer a route belongs to.

I emulated this situation to help you better understand the problem; see, Juniper's loopback address for the emulated customers CE1/CE2 overlaps with Alcatel's customer loopback addresses. How will a PE router PE1_ALU distinct between these routes?

![pic](http://img-fotki.yandex.ru/get/16132/21639405.11c/0_86306_45532d6b_orig.png)

[Route Distinguisher](https://tools.ietf.org/html/rfc4364#section-4.2) (RD) comes to the rescue.

> **RFC 4364. Route Distinguisher definition**  
> An RD is simply a number, and it does not contain any inherent information; it does not identify the origin of the route or the set of VPNs to which the route is to be distributed. The purpose of the RD is solely to allow one to create distinct routes to a common IPv4 address prefix.

![pic](http://img-fotki.yandex.ru/get/15489/21639405.11c/0_86307_f6b5a984_orig.png)

RD can be written in several forms, but it is handy to use the IP address in the _Administrator_ subfield and VPN number in the _Assigned number_ subfield:

```txt
A:PE1_ALU>config>service>vprn# route-distinguisher
  - no route-distinguisher
  - route-distinguisher <rd>

 <rd>                 : <ip-addr:comm-val>|<2byte-asnumber:ext-comm-val>|
                        <4byte-asnumber:comm-val>
                        ip-addr        - a.b.c.d
                        comm-val       - [0..65535]
                        2byte-asnumber - [1..65535]
                        ext-comm-val   - [0..4294967295]
                        4byte-asnumber - [1..4294967295]

### EXAMPLE ##
A:PE1_ALU>config>service>vprn# route-distinguisher 10.10.10.1:20
```

### VPN-IPv4 routes

A combination of a Route Distinguisher and an IPv4 route effectively produces what is called the [VPN-IPv4 route](https://tools.ietf.org/html/rfc4364#section-4.1). VPN-IPv4 routes are **12 byte** length (8b RD + 4b IPv4) addresses exchanged by MP-BGP speakers. PE routers compose VPN-IPv4 addresses and allocate MPLS labels for the routes before sending them to the MP-BGP neighbors. Consider the picture above to get a visual representation of an VPN-IPv4 route.

### Route Targets

So Route Distinguishers make every VPN-IPv4 route unique in a providers core, but we still need a mechanism to tell what VRF a single VPN-IPv4 route belongs to? We need a way to extend the VPN-IPv4 route with the information about which routing instance this route should be put into.

[BGP community](https://netdevops.me/2015/09/alcatel-lucent-bgp-configuration-tutorial-part-2-bgp-policies-community/) is a good way to solve this problem. For L3VPNs a specific [extended community](https://tools.ietf.org/html/rfc4360) was defined in [RFC 4364 Section 4.3.1](https://tools.ietf.org/html/rfc4364#section-4.3.1) called **Route Target**.

{{< admonition type=info title="RFC 4364. Route Target definition" open=false >}}
Every VRF is associated with one or more Route Target (RT) attributes. When a VPN-IPv4 route is created (from an IPv4 route that the PE has learned from a CE) by a PE router, it is associated with one or more Route Target attributes. These are carried in BGP as attributes of the route.

Any route associated with Route Target T must be distributed to every PE router that has a VRF associated with Route Target T. When such route is received by a PE router, it is eligible to be installed in those of the PE's VRFs that are associated with Route Target T. (Whether it actually gets installed depends upon the outcome of the BGP decision process, and upon the outcome of the decision process of the IGP (i.e., the intra-domain routing protocol) running on the PE/CE interface.)

A Route Target attribute can be thought of as identifying a set of sites. (Though it would be more precise to think of it as identifying a set of VRFs.) Associating a particular Route Target attribute with a route allows that route to be placed in the VRFs that are used for routing traffic that is received from the corresponding sites.

There is a set of Route Targets that a PE router attaches to a route received from site S; these may be called the "Export Targets". And there is a set of Route Targets that a PE router uses to determine whether a route received from another PE router could be placed in the VRF associated with site S; these may be called the "Import Targets". The two sets are distinct, and need not be the same. Note that a particular VPN-IPv4 route is only eligible for installation in a particular VRF if there is some Route Target that is both one of the route's Route Targets and one of the VRF's Import Targets.
{{< /admonition >}}

Usually the RTs are represented as `<AS Number of a client network>:<VRF ID>`:

```txt
*A:PE1_ALU>config>service>vprn$ vrf-target
  - vrf-target {<ext-community>|export <ext-community>|import <ext-community>}
  - no vrf-target

 <ext-community>      : target:{<ip-addr:comm-val>|
                        <2byte-asnumber:ext-comm-val>|
                        <4byte-asnumber:comm-val>}
                        ip-addr        - a.b.c.d
                        comm-val       - [0..65535]
                        2byte-asnumber - [0..65535]
                        ext-comm-val   - [0..4294967295]
                        4byte-asnumber - [0..4294967295]

### EXAMPLE ##
*A:PE1_ALU>config>service>vprn$ vrf-target target:200:20
```

## PE<->PE MP-BGP configuration

First thing to accomplish in the L3VPN configuration is the BGP peering inside the provider's core network. We have two Provider Edge routers (PE) and one core provider (P) router in our simple network. Our business goal is to provide the L3VPN service to our beloved JUN and ALU customers. To do so, we need to configure BGP peering between all the PE routers involved in the L3VPN service setup, these two routers are PE1_ALU and PE2_JUN.

The BGP configuration part for PE1_ALU and PE2_JUN routers follows a simple iBGP configuration routine (check [BGP configuration tutorial](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/) to grab the basics), the only part which is different is a need of a [new BGP address family](https://tools.ietf.org/html/rfc4364#section-4.1). We need to enable this address family to deal with the VPN routes, which are different from the IPv4 routes.

In Juniper this family is called `inet-vpn`, in SROS it is `vpn-ipv4`, but nonetheless it is just an address family which enables communication of VPN routes between the peers. We will see later how this family differs from a classic IPv4, but for now just look at the BGP configuration part for both PE routers:

PE1_ALU:

```txt
*A:PE1_ALU>config>router>bgp# info 
----------------------------------------------
            group "iBGP"
                family ipv4 vpn-ipv4
                peer-as 100
                local-address 10.10.10.1
                neighbor 10.10.10.3
                exit
            exit
            no shutdown
----------------------------------------------
```

PE2_JUN:

```
bgp {
        group iBGP {
            local-address 10.10.10.3;
            family inet {               
                unicast;
            }
            family inet-vpn {
                unicast;
            }
            peer-as 100;
            neighbor 10.10.10.1;
        }
    }
```

![pic](http://img-fotki.yandex.ru/get/3013/21639405.11c/0_86303_bcf9be09_orig.png)

As you see, the only part which is related to L3VPN is this new VPN address family.

Support for the additional address families transforms a classical BGP to a fancy Multi-Protocol BGP ([RFC 4760](https://tools.ietf.org/html/rfc4760)). Lets see how this family is communicated in the BGP messages:

[![pic](http://img-fotki.yandex.ru/get/3913/21639405.11c/0_86304_6385a76b_orig.png)](http://img-fotki.yandex.ru/get/3913/21639405.11c/0_86304_6385a76b_orig.png)

Both routers announces the capability to exchange **VPN Unicast IPv4** routes in the `BGP OPEN` messages. If a BGP peer sees this capability in an incoming OPEN message, it assumes that the neighbor speaks VPN IPv4 routes.

## Configuring VRFs on PE1_ALU (SROS)

So far we have configured PE-PE relationship which is a foundation for a working L3VPN service. Our next step is a VRF configuration which can be seen as a customers facing dedicated routers inside a singel PE router hardware unit. We will start with PE1_ALU and configure VRFs 20 and 30.

### 1. Ports configuration

At first we should ensure that customer facing ports operate in `access` mode.

```txt
### customer router `CE1_ALU` connects to a PE via port 1/1/1
*A:PE1_ALU# configure port 1/1/1 shutdown
*A:PE1_ALU# configure port 1/1/1 ethernet mode access
*A:PE1_ALU# configure port 1/1/1 no shutdown

### customer router `CE1_JUN` connects to a PE via port 1/1/3
*A:PE1_ALU# configure port 1/1/3 shutdown
*A:PE1_ALU# configure port 1/1/3 ethernet mode access
*A:PE1_ALU# configure port 1/1/3 no shutdown```
```

### 2. Customers creation

SROS uses the concept of the `customers` which is similar to the tenants in a virtualization world. I will create two new customers (`Customer 1` is a default one) to map them to the customers we have in our network:

```txt
*A:PE1_ALU>config>service# info
----------------------------------------------
        customer 1 create
            description "Default customer"
        exit
        customer 20 create
            description "Juniper"
        exit
        customer 30 create
            description "Alcatel"
        exit
----------------------------------------------
```

### 3. VRF configuration

After that I create a VPRN service (which is a fancy SROS name for a L3VPN) for each customer:

```txt
### create vprn service
*A:PE1_ALU# configure service vprn 20 customer 20 create

### give it a name
*A:PE1_ALU>config>service>vprn$ description "Juniper Site A"

### create route-distinguisher for VRF 20
*A:PE1_ALU>config>service>vprn$ route-distinguisher 10.10.10.1:20

### set route target for this VRF
### here I configure the use of a single target 
### for both import and export operations following this form <AS_Num>:<Service_Num>
*A:PE1_ALU>config>service>vprn$ vrf-target target:200:20

### Create an interface in this VRF
*A:PE1_ALU>config>service>vprn$ interface toCE1 create
*A:PE1_ALU>config>service>vprn>if$ address 10.20.99.0/31

### map a port to this interface. SAP here goes for "Service Access Point"
*A:PE1_ALU>config>service>vprn>if$ sap 1/1/3 create
*A:PE1_ALU>config>service>vprn>if>sap$ back
*A:PE1_ALU>config>service>vprn>if$ back

### tell a router to resolve Next-Hop address in this VRF with MPLS tunnels
*A:PE1_ALU>config>service>vprn$ auto-bind mpls

### enable VPRN service
*A:PE1_ALU>config>service>vprn$ no shutdown
```

VRF 30 configuration repeats the same steps:

```txt
A:PE1_ALU>config>service# info 
----------------------------------------------
        vprn 30 customer 30 create
            route-distinguisher 10.10.10.1:30
            auto-bind mpls
            vrf-target target:300:30
            interface "toCE1" create
                address 10.30.99.0/31
                sap 1/1/1 create
                exit
            exit
            no shutdown
        exit
----------------------------------------------
```

### Configuring PE -> CE routing protocols

Ok, our VRFs 20 and 30 are configured on PE1_ALU router and we have customers interfaces attached. What we need to do next is to configure a routing protocol which will propagate customers routes to the PE router. On PE1_ALU router we will use BGP as a routing protocol towards the CE routers, consequently CE routers will use BGP as well. Lets configure BGP instances for VRFs 20 and 30:

BGP configuration for VRF 20:

```txt
/configure service vprn 20 customer 20
### specify AS number for BGP speaker in VRF 20
            autonomous-system 100

### configure BGP peer and use "as-override" technique
            bgp
                group "toCE"
                    as-override
                    peer-as 200
                    local-address 10.20.99.0
                    split-horizon
                    neighbor 10.20.99.1
                    exit
                exit
                no shutdown
            exit
            no shutdown
----------------------------------------------
```

#### AS override

The `as-override` command under the BGP section is used to resolve the issue with AS-PATH loop prevention mechanism.  
When a BGP UPDATE message goes from CE1_JUN over eBGP to PE1_ALU it has AS-PATH value of `200`. Then this UPDATE message traverses Service Provider's network and as it goes over eBGP session to CE2_JUN its AS-PATH value becomes `"100 200"`. But CE2_JUN is a part of AS `200` itself, so it will silently discard a route update with AS-PATH value containing its AS number (AS PATH loop prevention mechanism makes it so).

`as-override` command placed under the BGP context of the receiving VRF on a PE router replaces the customers AS number with Service Providers own AS number, so AS-PATH string of `"100 200"` will become `"100 100"` and will be accepted by the CE router residing in AS 200 since no loop will be detected.

#### Export policies

Note, that it is **mandatory** to create an export policy on SROS PE routes for incoming BGP-VPN routes to leave the VRF over the PE -> CE routing protocol to the CE router:

```txt
*A:PE1_ALU# configure router policy-options 
*A:PE1_ALU>config>router>policy-options# begin 
*A:PE1_ALU>config>router>policy-options# policy-statement "MP-BGP_to_CE"
*A:PE1_ALU>config>router>policy-options>policy-statement>entry$ from protocol bgp-vpn 
*A:PE1_ALU>config>router>policy-options>policy-statement>entry$ action accept 
*A:PE1_ALU>config>router>policy-options>policy-statement>entry>action$ back 
*A:PE1_ALU>config>router>policy-options>policy-statement>entry$ back 
*A:PE1_ALU>config>router>policy-options>policy-statement$ back 
*A:PE1_ALU>config>router>policy-options# commit 
*A:PE1_ALU>config>router>policy-options# info 
----------------------------------------------
            policy-statement "MP-BGP_to_CE"
                entry 10
                    from
                        protocol bgp-vpn
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------
```

Now add this policy under the BGP context of the VRF:

```
*A:PE1_ALU# configure service vprn 20 bgp group "toCE" export "MP-BGP_to_CE"
```

Super, now repeat the steps for `VRF 30`. The complete service configuration part on PE1_ALU should look as follows:

```txt
A:PE1_ALU>config>service# info
----------------------------------------------
        customer 1 create
            description "Default customer"
        exit
        customer 20 create
            description "Juniper"
        exit
        customer 30 create
            description "Alcatel"
        exit
        vprn 20 customer 20 create
            description "Juniper Site A"
            autonomous-system 100
            route-distinguisher 10.10.10.1:20
            auto-bind mpls
            vrf-target target:200:20
            interface "toCE1" create
                address 10.20.99.0/31
                sap 1/1/3 create
                exit
            exit
            bgp
                group "toCE"
                    as-override
                    export "MP-BGP_to_CE"
                    peer-as 200
                    local-address 10.20.99.0
                    split-horizon
                    neighbor 10.20.99.1
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
        vprn 30 customer 30 create
            description "Alcatel Site A"
            autonomous-system 100
            route-distinguisher 10.10.10.1:30
            auto-bind mpls
            vrf-target target:300:30
            interface "toCE1" create
                address 10.30.99.0/31
                sap 1/1/1 create
                exit
            exit
            bgp
                group "toCE"
                    as-override
                    export "MP-BGP_to_CE"
                    peer-as 300
                    local-address 10.30.99.0
                    split-horizon
                    neighbor 10.30.99.1
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
----------------------------------------------
```

## Configuring VRFs on PE2_JUN (Juniper)

Juniper JUNOS does not use concept of network/access ports, thats why you deal with CE-facing interfaces just like you do with the normal ones:

```
set interfaces ge-0/0/1 unit 0 family inet address 10.20.99.2/31
set interfaces ge-0/0/2 unit 0 family inet address 10.30.99.2/31
```

Now the VRF part; VRF is called a routing-instance in JUNOS.

```txt
[edit routing-instances]
root@PE2_JUN# show | display set 
### create a routing instance and set its type to VRF
### in JUNOS its possible to set VRF name like 
### set routing-instance "Juniper_Site_B" but we will use numerical id for consistency
set routing-instances 20 instance-type vrf

### give VRF a description
set routing-instances 20 description "Juniper Site B"

### provision interface to CE router, RT and RD
set routing-instances 20 interface ge-0/0/1.0
set routing-instances 20 route-distinguisher 10.10.10.3:20
set routing-instances 20 vrf-target target:200:20

### and for VRF 30
set routing-instances 30 description "Alcatel Site B"
set routing-instances 30 instance-type vrf
set routing-instances 30 interface ge-0/0/2.0
set routing-instances 30 route-distinguisher 10.10.10.3:30
set routing-instances 30 vrf-target target:300:30
```

VRF configuration on Juniper looks almost identical to Nokia. The major difference here is that you don't have to tell JUNOS to resolve VRF's next-hop address via MPLS tunnel. And you don't have to configure an export policy in case you are using eBGP as a PE-CE protocol. Juniper defaults to that behavior.

### PE -> CE configuration on Juniper

Note, that with Juniper we omit the explicit AS number configuration under the BGP configuration. In that case the globally configured AS number will be used.

Configuration portion for VRF 20 will look as follows:

```
root@PE2_JUN# show | display set 
<... omitted ...>
set routing-instances 20 protocols bgp group toCE local-address 10.20.99.2
set routing-instances 20 protocols bgp group toCE peer-as 200
set routing-instances 20 protocols bgp group toCE as-override
set routing-instances 20 protocols bgp group toCE neighbor 10.20.99.3
```

So far we've played with BGP as a PE-CE routing protocol, but frankly speaking OSPF is not a stranger for this task as well. Lets see how to configure the OSPF adjacency between the Juniper PE and a CE2_ALU router.

A key piece in this configuration block is the export policy which lets vpn-ipv4 routes imported into VRF 30 to be exported to CE2_ALU over OSPF.

Configure an export policy first:

```txt
[edit]
root@PE2_JUN# show
<... omitted ...>
policy-options {
    policy-statement MP-BGP_to_CE_via_OSPF {
        term export {
            from protocol bgp;
            then accept;
        }
    }
}
```

Then configure PE-CE OSPF protocol with the export policy applied:

```txt
### optionally set router-id for OSPF process to use
routing-options {
    router-id 100.100.100.100;
}
protocols {
    ospf {
        export MP-BGP_to_CE_via_OSPF;
        ## configure OSPF area and interfaces
        area 0.0.0.0 {
            interface ge-0/0/2.0 {
                interface-type p2p;
            }
        }
    }
}

### DISPLAY SET
set routing-instances 30 routing-options router-id 100.100.100.100
set routing-instances 30 protocols ospf export MP-BGP_to_CE_via_OSPF
set routing-instances 30 protocols ospf area 0.0.0.0 interface ge-0/0/2.0 interface-type p2p```
```

Complete VRF configuration for PE2_JUN goes like this:

```txt
[edit routing-instances]
root@PE2_JUN# show
20 {
    description "Juniper Site B";
    instance-type vrf;
    interface ge-0/0/1.0;
    route-distinguisher 10.10.10.3:20;
    vrf-target target:200:20;
    protocols {
        bgp {
            group toCE {
                local-address 10.20.99.2;
                peer-as 200;
                as-override;
                neighbor 10.20.99.3;
            }
        }
    }
}
30 {
    description "Alcatel Site B";
    instance-type vrf;
    interface ge-0/0/2.0;
    route-distinguisher 10.10.10.3:30;
    vrf-target target:300:30;
    routing-options {
        router-id 100.100.100.100;
    }
    protocols {
        ospf {
            export MP-BGP_to_CE_via_OSPF;
            area 0.0.0.0 {
                interface ge-0/0/2.0 {
                    interface-type p2p;
                }
            }
        }
    }
}
```

## CE -> PE routing protocol configuration

Now it is time to connect our customers to the service provider's network via VRFs created earlier and finally add some VPN routes. CE routers completely unaware of a complex L3VPN configuration on the PE routers, what they need to do is just setup a routing protocol over which customers routes could be delivered to (and received from) the Service Provider.

Starting with Juniper CE1_JUN and CE2_JUN that run eBGP with PE routers:

CE1_JUN:

```txt
root@CE1_JUN# show 
### Last changed: 2015-10-28 17:40:05 UTC
version 14.1R1.10;
<... omitted ...>

### 1. configure PE-facing interface
interfaces {
    ge-0/0/0 {
        mac 50:01:00:06:00:02;
        unit 0 {                        
            family inet {
                address 10.20.99.1/31;
            }
        }
    }
### 2. dont forget about loopback, this address will be exported to remote site
    lo0 {
        unit 0 {
            family inet {
                address 1.1.1.1/32;
            }
        }
    }
}

### 3. AS number is a mandatory for eBGP session to run
routing-options {
    autonomous-system 200;
}

### 4. and a simple eBGP configuration
protocols {
    bgp {
        group toPE {
            local-address 10.20.99.1;
            
            ## 5. we need to export loopback address to eBGP
            export export_loopback;
            peer-as 100;
            neighbor 10.20.99.0;        
        }
    }
}

### 6. policy to export loopback address
policy-options {
    prefix-list loopback {
        1.1.1.1/32;
    }
    policy-statement export_loopback {
        term Loopback {
            from {
                prefix-list loopback;
            }
            then accept;
        }
    }
}
```

CE2_JUN:

```txt
root@CE2_JUN# show 
### Last changed: 2015-10-28 16:50:23 UTC
version 14.1R1.10;

### 1. configure PE-facing interface
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {               
                address 10.20.99.3/31;
            }
        }
    }
### 2. dont forget about loopback, this address will be exported to remote site
    lo0 {
        unit 0 {
            family inet {
                address 2.2.2.2/32;
            }
        }
    }
}

### 3. AS number is a mandatory for eBGP session to run
routing-options {
    autonomous-system 200;
}

### 4. and a simple eBGP configuration
protocols {
    bgp {
        group toPE {
            local-address 10.20.99.3;
            family inet {
                unicast;
            }
            
            ## 5. we need to export loopback address to eBGP
            export export_loopback;     
            peer-as 100;
            neighbor 10.20.99.2;
        }
    }
}

### 6. policy to export loopback address
policy-options {
    prefix-list loopback {
        2.2.2.2/32;
    }
    policy-statement export_loopback {
        term Loopback {
            from {
                prefix-list loopback;
            }
            then accept;
        }
    }
}
```

Now its Nokia time. Pay attention to the CE2_ALU router, since we are using OSPF on CE2-PE2 link configuration it is a little bit different from other CE's configs.

CE1_ALU:

```txt
A:CE1_ALU>config>router# info
----------------------------------------------

### 1. Interfaces and AS Num config

#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 1.1.1.1/32
            no shutdown
        exit
        interface "toPE"
            address 10.30.99.1/31
            port 1/1/1
            no shutdown
        exit
        autonomous-system 300

### 2. Policy for exporting loopback address
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
#--------------------------------------------------
echo "BGP Configuration"
#--------------------------------------------------
        bgp
            group "toPE"
                export "export_loopback" ## tell CE to export its system address to eBGP peer
                peer-as 100
                local-address 10.30.99.1
                split-horizon
                neighbor 10.30.99.0
                exit
            exit
            no shutdown
        exit
----------------------------------------------
```

CE2_ALU:

```txt
A:CE2_ALU>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 2.2.2.2/32
            no shutdown
        exit
        interface "toPE"
            address 10.30.99.3/31
            port 1/1/1
            no shutdown
        exit
        autonomous-system 300

### we running OSPF as PE-CE protocol
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            area 0.0.0.0
                interface "system"
                    no shutdown
                exit
                interface "toPE"
                    interface-type point-to-point
                    no shutdown
                exit
            exit
            no shutdown
        exit
----------------------------------------------
```

## Control plane walkthrough

We are done with the configuration, all in all it was not a complex task, what is more important is to understand what's going on with control and data planes. I believe you will like this step-by-step walkthrough via every node in the network.

I will start with dissection of a control plane operation from the point where MP-BGP session between PE routers has been already established and we are enabling VRFs on customers routers. Refer to this overview chart and see how an information about CE1_JUN's loopback interface propagates through the entire network to CE2_JUN counterpart:

> All the pictures are clickable, to see the full sized pics choose "open an image in a separate tab" option in your browser.

[![l3_vpn_control_plane](http://img-fotki.yandex.ru/get/31082/21639405.11c/0_86308_2af39052_orig.png)](http://img-fotki.yandex.ru/get/31082/21639405.11c/0_86308_2af39052_orig.png)

### Step 1

CE1_JUN router has an export policy `export_loopback` configured which is used by BGP to construct the BGP UPDATE message with `lo0` prefix as an NLRI.

### Step 2

CE1_JUN sends a regular BGP UPDATE message to its eBGP peer PE1_ALU.

[![l3vpn_control_plane](http://img-fotki.yandex.ru/get/17849/21639405.11c/0_86309_b4edb4e4_orig.png)](http://img-fotki.yandex.ru/get/17849/21639405.11c/0_86309_b4edb4e4_orig.png)

### Step 3

PE1_ALU router receives this update via its interface `toCE1` configured in `vprn 20` context. PE1_ALU populates its VRF 20 with a route to `1.1.1.1/32` via `10.20.99.1`.

### Step 4

PE1_ALU router has an established MP-iBGP session with PE2_JUN so it takes a BGP route from VRF 20 and automatically sends an MP-BGP UPDATE message to its peer. Note, that ALU routers will send MP-BGP update automatically only for the connected to VRF routes and the routes received via BGP. If we had OSPF between CE1 and PE1, we would need to configure an export policy to propagate this update over MP-BGP session.

Since PE1_ALU router wants to send an update for a _route in the VRF_ it should construct an MP-BGP Update message which has a specific Path attribute - **MP_REACH_NLRI** - to communicate this routing information. And PE1_ALU will transform the `1.1.1.1/32` IPv4 prefix to an VPN-IPv4 one.

[![l3vpn_control_plane](http://img-fotki.yandex.ru/get/6403/21639405.11c/0_8630a_dddcc68e_orig.png)](http://img-fotki.yandex.ru/get/6403/21639405.11c/0_8630a_dddcc68e_orig.png)

Take a closer look at this BGP message. See how PE1_ALU router added some valuable additional information to correctly pass CE1_ALU's loopback address via MP-BGP. First of all examine how NLRI has been transformed in MP-BGP: it now has a Route Distinguisher which we configured for VRF 20 earlier, it has the IPv4 prefix itself and it has the MPLS label `131068`.

PE1_ALU router allocated a VPN label which it associated with the VRF 20. This label tells PE1_ALU router that if it ever receives a data packet with this label it should associate the data encapsulated within it with VRF 20! This way ingress PE routers tell others PEs what label should be used as a VPN label for the routes residing in a particular VRF.

There are two methods of allocating the VPN labels (they are also called Service labels):

  1. **per VRF**: all routes originated from a single VRF will have the same VPN label. SROS routers default to this.
  2. **per VRF per next-hop**: If a VRF has >1 CE interfaces, PE router will allocate different labels for different CE interfaces inside one VRF. **Juniper** routers default to this.

If we zoom over the Extended Community attribute of the BGP UPDATE message, we can spot the Route Target `200:20` value there.

Important things happened to the Next-Hop, not only it looks now like a VPN-IPv4 route with a Route Distinguisher value of `0:0` and without MPLS label, but Next-Hop IPv4 address has been changed to PE1_ALU's system (loopback) interface `10.10.10.1`. This is how PE1 router tells PE2 that it can reach VRF 20 routes via PE1.

In the end of the day, PE1_ALU's update reaches PE2_JUN since it has the IP destination address of 10.10.10.3.

Notice, that BGP updates traverse Service Provider's network in a form of the simple IP packets, MPLS is out of the picture at this moment. Service Provider's core router - P1_ALU - simply routes IP packets and has no take in BGP at all.

### Step 5

PE2_JUN receives the BGP UPDATE with VPN-IPv4 route. Once this route passes validation checks (Nexhop resolvable, no AS Path loop) PE2 submits this route to a specific table named `bgp.l3vpn.0`. This table stores all BGP VPN routes, refer to this figure to examine some of its content:

[![l3vpn_control_plane](http://img-fotki.yandex.ru/get/4121/21639405.11c/0_8630b_e7511a43_orig.png)](http://img-fotki.yandex.ru/get/4121/21639405.11c/0_8630b_e7511a43_orig.png)

PE2 extracts the routing information from this update an based on the Route Target value installs the IPv4 route `1.1.1.1/32` into the VRF 20 table - `20.inet.0`. PE2 resolves the next-hop address of the fellow PE1_ALU (10.10.10.1) via MPLS Label Switched Path (LSP) and stores this information in the `20.inet.0` table:

```
20.inet.0: 5 destinations, 5 routes (5 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

1.1.1.1/32         *[BGP/170] 2d 08:38:15, localpref 100, from 10.10.10.1
                      AS path: 200 I, validation-state: unverified
                    > to 10.99.99.2 via ge-0/0/0.0, label-switched-path toPE1
```

Remember that it is mandatory to have an active LSP to the remote PE, since we have to have an MPLS transport to the remote end to carry the data packets.

### Step 6

Since we installed the route for the `1.1.1.1/32` IPv4 prefix into VRF 20 and we have an active eBGP peer in VRF 20, we should send an update for this IPv4 prefix to the CE2_JUN router to let the CE2 site to be aware of the remote prefix. This update goes as an ordinary eBGP update.

### Step 7

CE2_JUN receives the BGP UPDATE and installs a route into the only table it has for IPv4 routes - `inet.0`.

This completes Control Plane operation regarding the prefix `1.1.1.1/32`, same process goes for the other loopbacks and connected to VRFs link addresses for both Alcatel and Juniper customers.

## Data plane walkthrough

To complete this post we should examine the data plane operations. We will see how data packets destined to `1.1.1.1` propagate through the network using the labels allocated during the control plane operations.

![l3vpn_dataplane](http://img-fotki.yandex.ru/get/3708/21639405.11c/0_8630c_5f8e9edd_orig.png)

### Step 1

CE2_JUN wants to send a data packet to CE1_JUN via L3VPN service provided by our network. CE2 has an active route in its route table `inet.0` that says that it can reach `1.1.1.1/32` via `10.20.99.2` address via the `ge-0/0/0` interface. CE2 has a MAC address for `10.20.99.2` so it constructs the whole frame and puts it on the wire.

[![l3vpn_dataplane](http://img-fotki.yandex.ru/get/6416/21639405.11c/0_8630d_cdb63a28_orig.png)](http://img-fotki.yandex.ru/get/6416/21639405.11c/0_8630d_cdb63a28_orig.png)

### Step 2

PE2_JUN receives the Ethernet frame on its interface `ge-0/0/1` which belongs to VRF 20, that is how PE2 decides to associate this packet with VRF 20. PE2 consults with the VRF 20 routing table and sees that it has to use the LSP `toPE1` to send the incoming data packet further.  
Then PE2 gets MPLS label which it received earlier from its RSVP neighbor P1_ALU during the LSP signalization process.

[![l3vpn_dataplane](http://img-fotki.yandex.ru/get/4519/21639405.11c/0_8630e_5890a719_orig.png)](http://img-fotki.yandex.ru/get/4519/21639405.11c/0_8630e_5890a719_orig.png)

But this was just a transport MPLS label, it helps PE2_JUN to reach PE1_ALU, but PE2 needs one label more - the VPN Label - to tell PE1_ALU to which VRF this data belongs. This label was signalled earlier (see Control Plane operation section) via MP-BGP.

Now PE2 has everything it needs:

  1. MPLS VPN label to encapsulate the data packets from its VRF 20 destined to the VRF 20 on PE1_ALU
  2. Transport MPLS Label to get to PE1_ALU via MPLS core

and thus it constructs a packet with two labels stacked and fires it off.

### Step 3

P1_ALU is totally unaware of the whole services and customers mess, it just switches MPLS packets by replacing the incoming transport label with the outgoing one.

### Step 4

PE1_ALU receives an MPLS packet from P1_ALU. It pops out the transport label (_fig. 4.1_) and examines the enclosed MPLS label. This label value `131068` was signalled by PE1_ALU via MP-BGP during the Control Plane operation. So PE1 knows that it has to pop this label and associate the enclosed packet with the VPRN 20 (VRF 20) (_fig. 4.2_)

[![l3vpn_dataplane](http://img-fotki.yandex.ru/get/5907/21639405.11c/0_8630f_a746c430_orig.png)](http://img-fotki.yandex.ru/get/5907/21639405.11c/0_8630f_a746c430_orig.png)

VRF's 20 routing table says that packets destined to `1.1.1.1` should be forwarded to `10.20.99.3` address (_fig. 4.3_), which is a connected network leading to CE1_JUN (_fig. 4.4_). PE1_ALU constructs the packet and moves it via Ethernet out of the 1/1/2 port (_fig. 4.5_).

### Step 5

CE2_JUN receives an ordinary IP packet with a destination address matching its interface. It decapsulates ICMP echo request and sends back the echo reply.

This concludes the control and data plane operations walk through. If you followed along the explanations and practiced the configuration steps, you should be in a good shape to implement the basic L3VPN services and also should have a pretty solid understanding of the service establishment mechanics.
