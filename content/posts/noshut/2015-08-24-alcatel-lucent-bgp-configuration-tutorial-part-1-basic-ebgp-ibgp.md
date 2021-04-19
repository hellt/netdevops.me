---
title: Nokia (Alcatel-Lucent) BGP configuration tutorial. Part 1 - basic eBGP, iBGP
date: 2015-08-24T08:51:38+00:00
author: Roman Dodin
url: /2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/
draft: false
comment_id: bgp-basic
tags:
  - Nokia
  - SROS
  - BGP
---

There is no way I would leave you without covering configuration steps for one of the most versatile, scalable and robust internet protocols also known as **BGP**. And here it is - BGP configuration guide for Nokia (Alcatel-Lucent) Service Routers.

[As with the OSPF configuration tutorial](http://netdevops.me/2015/06/alcatel-lucent-ospf-configuration-tutorial/) I will cover the configuration process for various BGP scenarios along with the verification and troubleshooting steps bundled with colorful figures, detailed code snippets and useful remarks.

BGP is so huge that I had no other option but to write about it in several parts:

  * **Part 1 - basic eBGP and iBGP configuration**
  * [Part 2 - BGP policies. Community](http://netdevops.me/2015/09/alcatel-lucent-bgp-configuration-tutorial-part-2-bgp-policies-community/)

Part 1 is dedicated to basic eBGP/iBGP configuration. We will practice with common BGP configuration procedures at first, then learn how to export routes into BGP process and prevent unnecessary route reflection by means of `split-horizon` over eBGP links.

Next we go over iBGP configuration to spread the eBGP learned routes across the Autonomous Systems. I will explain the necessity of having a full-mesh iBGP topology and the use of the `next-hop-self` command for iBGP peers.

It's a perfect time to configure some BGP, right?

<!--more-->

# Common BGP configuration steps

Despite what type of BGP (Internal or External) you are going to configure there are some basic steps we are about to discuss. Address planning, IGP configuration, router-id selection, autonomous-system number setting, peer groups and neighbor configuration - all of these task are common to each and every BGP configuration routine.

## IGP and addressing

BGP completely relies on IGP (or static routes) when resolving nexthop address received in BGP updates from its peers. This means that prior to BGP configuration you should have IGP up and running. During this session I will refer to this base topology:

![pic](http://img-fotki.yandex.ru/get/4911/21639405.11c/0_84ca0_67149947_orig.png)

A few words about the address plan and key pieces of this diagram: a BGP peering will take place between the two Autonomous Systems (hereinafter AS) 65510 and 65520.

AS 65510 utilizes `10.10.0.0/16` network for local link addresses, system interfaces of its routers and customers-assigned networks, whereas AS 65520 uses `10.20.0.0/16` for the same purposes. Address plan details could be found at the _Legend section_ of the "base topology" figure.

We will be working with the two customers networks:

  *  `R5_Customer - 10.10.55.0/24` in AS 65510
  *  `R3_Ext_Customer - 172.16.33.0/24` in AS 65520

As to Interior Gateway Protocol - I chose IS-IS, though you can choose an IGP protocol of your choice - it wont be any different. IS-IS configuration for this tutorial is super straightforward, system and network interfaces are participating in IS-IS process within the relevant ASes (except interfaces between R1-R3, R2-R4 as they are connecting different AS's and we will run BGP there). Inter-router links are all point-to-point type.

IS-IS configuration section for reference:



R1 (AS 65510):
```txt
*A:R1>config>router>isis# info
----------------------------------------------
        level-capability level-1
        area-id 10.10
        reference-bandwidth 100000000
        level 1
            wide-metrics-only
        exit
        level 2
            wide-metrics-only
        exit
        interface "system"
            no shutdown
        exit
        interface "toR2"
            interface-type point-to-point
            no shutdown
        exit
        interface "toR5"
            interface-type point-to-point
            no shutdown
        exit
        no shutdown
----------------------------------------------

## IS-IS database for 65510 consists of LSP from every router in this AS
*A:R1>config>router>isis# show router isis database

===============================================================================
Router Base ISIS Instance 0 Database
===============================================================================
LSP ID                                  Sequence  Checksum Lifetime Attributes
-------------------------------------------------------------------------------

Displaying Level 1 database
-------------------------------------------------------------------------------
R1.00-00                                0xd       0x7740   1182     L1
R2.00-00                                0xb       0x7ad1   812      L1
R5.00-00                                0xc       0x8dfd   817      L1
R6.00-00                                0xb       0xe8a5   842      L1
Level (1) LSP Count : 4

Displaying Level 2 database
-------------------------------------------------------------------------------
Level (2) LSP Count : 0
===============================================================================


## Check if we have a route to every router's system address within AS
*A:R1# show router route-table  10.10.10.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.10.1/32                                 Local   Local     02h12m52s  0
       system                                                       0
10.10.10.2/32                                 Remote  ISIS      02h12m24s  15
       10.10.99.1                                                   100
10.10.10.5/32                                 Remote  ISIS      02h12m25s  15
       10.10.99.5                                                   100
10.10.10.6/32                                 Remote  ISIS      02h12m22s  15
       10.10.99.1                                                   200
-------------------------------------------------------------------------------
No. of Routes: 4
```
R3 (AS 65520):
```txt
A:R3>config>router>isis# info
----------------------------------------------
        level-capability level-1
        area-id 20.20
        reference-bandwidth 100000000
        level 1
            wide-metrics-only
        exit
        level 2
            wide-metrics-only
        exit
        interface "system"
            no shutdown
        exit
        interface "toR4"
            interface-type point-to-point
            no shutdown
        exit
        no shutdown
----------------------------------------------

## AS 65520 consists of two routers R3 and R4, that is why we see only two LSP here
A:R3>config>router>isis# show router isis database

===============================================================================
Router Base ISIS Instance 0 Database
===============================================================================
LSP ID                                  Sequence  Checksum Lifetime Attributes
-------------------------------------------------------------------------------

Displaying Level 1 database
-------------------------------------------------------------------------------
R3.00-00                                0xc       0x8dc2   1160     L1
R4.00-00                                0xa       0xfe4e   639      L1
Level (1) LSP Count : 2

Displaying Level 2 database
-------------------------------------------------------------------------------
Level (2) LSP Count : 0
===============================================================================
```

## Configuring Router ID and Autonomous System number

Once IGP is configured its time to configure a common entity for almost every routing protocol - **Router ID**. For BGP there is more than one place to configure the Router ID. Here is the _Router ID_ selection process sorted by a priority:

  1. Router ID is configured in BGP global context with the command `configure router bgp router-id <ip-address>`
  2. Router ID is configured globally for a router with the command `configure router router-id <ip-address>`
  3. Router ID is inherited from `system` IP-address.

Important thing to remember is that if no `router-id` nor `system` interface is configured - BGP will not start. Since we have the `system` interface configured for every router we don't need to specify the `router-id` explicitly.

**AS number** can be configured either globally for a router `configure router autonomous-system <autonomous-system>` or for a specified peer group with the `local-as` command. We will stick to the first option and configure our AS numbers globally for a router:

```txt
A:R3# configure router autonomous-system 65520

*A:R3>config>router# info

#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 10.20.20.3/32
            no shutdown
        exit
        interface "toR1"
            address 10.0.99.1/31
            port 1/1/3
            no shutdown
        exit
        interface "toR4"
            address 10.20.99.0/31
            port 1/1/2
            no shutdown
        exit
        autonomous-system 65520
#--------------------------------------------------
```

# Starting eBGP

Common parameters are now configured and we can jump to eBGP peers configuration. Recall that we have two routers within AS 65510 (R1 and R2) which will have eBGP peering sessions with R3 and R3 within AS 65520 accordingly. Thus we should configure eBGP peering between the pairs R1-R3, R2-R4.

![pic](http://img-fotki.yandex.ru/get/6612/21639405.11c/0_84ca1_6e32bdad_orig.png)

Nokia BGP configuration policy **requires** you to configure **at least one peer group** to make BGP peering happen. Peer groups are logical containers for BGP peers that share common parameters. Every BGP neighbor you add should find its place in any of the BGP peer groups, in other words - **peer groups are mandatory** in SROS.

I will guide you through basic eBGP configuration between R1 and R3. R2 and R4 configuration will be just the same.

R1:
```txt
## entering BGP configuration context
*A:R1# configure router bgp

## creating group eBGP
*A:R1>config>router>bgp$ group "eBGP"

## specifying AS Number for AS we would want to peer to (which is 65520)
## for eBGP peer-as should differ from local AS
## for iBGP peer-as should match local AS Number
*A:R1>config>router>bgp>group$ peer-as 65520

## setting IP address of the remote router in AS 65520
*A:R1>config>router>bgp>group$ neighbor 10.0.99.1

## specify local-address for eBGP peer
*A:R1>config>router>bgp>group>neighbor# local-address 10.0.99.0

## Viewing resulting configuration
*A:R1>config>router>bgp>group>neighbor$ back
*A:R1>config>router>bgp>group$ back
*A:R1>config>router>bgp$ info
----------------------------------------------
            group "eBGP"
                peer-as 65520
                neighbor 10.0.99.1
                    local-address 10.0.99.0
                exit
            exit
            no shutdown
----------------------------------------------```
```

R3:
```txt
## all the comments are the same as for R1

*A:R3# configure router bgp
*A:R3>config>router>bgp$ group "eBGP"
*A:R3>config>router>bgp>group$ peer-as 65510
*A:R3>config>router>bgp>group$ neighbor 10.0.99.0
A:R3>config>router>bgp>group>neighbor$ local-address 10.0.99.1
*A:R3>config>router>bgp>group>neighbor$ back
*A:R3>config>router>bgp>group$ back
*A:R3>config>router>bgp$ info
----------------------------------------------
            group "eBGP"
                peer-as 65510
                neighbor 10.0.99.0
                    local-address 10.0.99.1
                exit
            exit
            no shutdown
----------------------------------------------
```

As simple as that, eBGP in its simplest form has been configured in 5 lines. Pay additional attention to `local-address` command. It is a common practice to specify a link IP address for an eBGP peer, otherwise SROS router will try to establish TCP session from its system IP address and will fail.

To verify the established eBGP peering use the `show router bgp summary` command (another way is to use `show router bgp neighbor <neighbor-ip-address>`)

```txt
A:R1# show router bgp summary
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
BGP Admin State         : Up          BGP Oper State              : Up
Total Peer Groups       : 1           Total Peers                 : 1
Total BGP Paths         : 7           Total Path Memory           : 1260
Total IPv4 Remote Rts   : 0           Total IPv4 Rem. Active Rts  : 0
Total McIPv4 Remote Rts : 0           Total McIPv4 Rem. Active Rts: 0
Total McIPv6 Remote Rts : 0           Total McIPv6 Rem. Active Rts: 0
Total IPv6 Remote Rts   : 0           Total IPv6 Rem. Active Rts  : 0
Total IPv4 Backup Rts   : 0           Total IPv6 Backup Rts       : 0

Total Supressed Rts     : 0           Total Hist. Rts             : 0
Total Decay Rts         : 0

Total VPN Peer Groups   : 0           Total VPN Peers             : 0
Total VPN Local Rts     : 0
Total VPN-IPv4 Rem. Rts : 0           Total VPN-IPv4 Rem. Act. Rts: 0
Total VPN-IPv6 Rem. Rts : 0           Total VPN-IPv6 Rem. Act. Rts: 0
Total VPN-IPv4 Bkup Rts : 0           Total VPN-IPv6 Bkup Rts     : 0

Total VPN Supp. Rts     : 0           Total VPN Hist. Rts         : 0
Total VPN Decay Rts     : 0

Total L2-VPN Rem. Rts   : 0           Total L2VPN Rem. Act. Rts   : 0
Total MVPN-IPv4 Rem Rts : 0           Total MVPN-IPv4 Rem Act Rts : 0
Total MDT-SAFI Rem Rts  : 0           Total MDT-SAFI Rem Act Rts  : 0
Total MSPW Rem Rts      : 0           Total MSPW Rem Act Rts      : 0
Total RouteTgt Rem Rts  : 0           Total RouteTgt Rem Act Rts  : 0
Total McVpnIPv4 Rem Rts : 0           Total McVpnIPv4 Rem Act Rts : 0
Total MVPN-IPv6 Rem Rts : 0           Total MVPN-IPv6 Rem Act Rts : 0
Total EVPN Rem Rts      : 0           Total EVPN Rem Act Rts      : 0
Total FlowIpv4 Rem Rts  : 0           Total FlowIpv4 Rem Act Rts  : 0
Total FlowIpv6 Rem Rts  : 0           Total FlowIpv6 Rem Act Rts  : 0

===============================================================================
BGP Summary
===============================================================================
Neighbor
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.0.99.1
                65520      85    0 00h41m58s 0/0/0 (IPv4)
                           85    0
-------------------------------------------------------------------------------
```

At the end of this show command you can find information about the BGP neighbors and their states. With `show router bgp summary` command issued on R1 we see `10.0.99.1` as a neighbor (which is R3's interface IP address).

If a session is established then you see the session uptime and number of routes _received/active/sent_. If the session has not been established yet an operator will see the current BGP state instead of the exchanged routes counters.

String `0/0/0 (IPv4)` is an indicator that the peering has been successfully established and R1 router received and sent exactly zero IPv4 routes. Zero counters are expected, since we just started the eBGP session but did not export any routes to it. It is very important to remember that **by default SROS does not add any non-BGP routes to the BGP process**.

# Exporting routes to BGP

No fun at all to play with zero NLRI (network layer reachability information). Lets fix this and add some routes to our eBGP process. We have a good candidate for this in our address plan - `R5_Customer - 10.10.55.0/24` network. To emulate this customer's network we must add a loopback interface to R5 and announce this network via IGP:

```txt
A:R5# configure router interface R5_Customer_loopback
*A:R5>config>router>if$ loopback
*A:R5>config>router>if$ address 10.10.55.1/24

## adding artificial R5_Customer network to IS-IS
*A:R5# configure router isis interface "R5_Customer_loopback"
```

After we created a network for our customer and announced it via IS-IS we should check if R1 could see it in its routing table:

```txt
A:R1# show router route-table 10.10.55.0/24

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.55.0/24                                 Remote  ISIS      00h00m03s  15
       10.10.99.5                                                   100
-------------------------------------------------------------------------------
No. of Routes: 1
```

Now R1 is aware of `10.10.55.0/24`, but this is not sufficient for the BGP process on R1 to advertise this prefix to R3. We should **explicitly** tell BGP process running on R1 to take `10.10.55.0/24` prefix into consideration and the way to do so is to create a **policy-statement** and **export** it to BGP.

Step-by-step plan goes like this:

  * create a _prefix-list_ to match a desired prefix
  * create a _policy-statement_ accepting prefixes from the prefix-list and delivering it to the BGP process
  * add customer's network to BGP via `export <policy_statement>` command under peer group context.

Lets implement this plan:

```txt
A:R1# configure router policy-options

## entering to policy options edit mode
A:R1>config>router>policy-options# begin

## creating prefix-list for R5_Customer network
*A:R1>config>router>policy-options# prefix-list "R5_Customer_pfx"
*A:R1>config>router>policy-options>prefix-list$ prefix 10.10.55.0/24 exact
*A:R1>config>router>policy-options>prefix-list$ back

## creating policy statement
*A:R1>config>router>policy-options# policy-statement "R5_Customer_export"
*A:R1>config>router>policy-options>policy-statement$ entry 10
*A:R1>config>router>policy-options>policy-statement>entry$ from prefix-list "R5_Customer_pfx"
*A:R1>config>router>policy-options>policy-statement>entry$ to protocol bgp
*A:R1>config>router>policy-options>policy-statement>entry$ action accept
*A:R1>config>router>policy-options>policy-statement>entry>action$ back
*A:R1>config>router>policy-options>policy-statement>entry$ back
*A:R1>config>router>policy-options>policy-statement$ back

## applying changes to policy options
*A:R1>config>router>policy-options# commit

## reviewing configuration
*A:R1>config>router>policy-options# info
----------------------------------------------
            prefix-list "R5_Customer_pfx"
                prefix 10.10.55.0/24 exact
            exit
            policy-statement "R5_Customer_export"
                entry 10
                    from
                        prefix-list "R5_Customer_pfx"
                    exit
                    to
                        protocol bgp
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------
```

After we have the policy statement configured we can reference it in the `export` command under the eBGP peer group section of R1:

```txt
*A:R1# configure router bgp
*A:R1>config>router>bgp# group "eBGP"

## hitting TAB after "export" keyword displays all available policy statements
*A:R1>config>router>bgp>group# export
<policy-name> [<policy-name>...(upto 15 max)]
 "R5_Customer_export"

*A:R1>config>router>bgp>group# export "R5_Customer_export"
```

Export command triggers R1 to send a BGP Update message with the NLRI for `R5_Customer` network to R3 (note that I made the same configuration on R2-R4 pair, so the figure below shows R2's BGP Update message as well):

![pic](http://img-fotki.yandex.ru/get/9170/21639405.11c/0_84ca2_4e1a50c8_orig.png)

Take a look at `show router bgp summary` once again on R1:

```txt
A:R1# show router bgp summary

## output omitted ##

===============================================================================
BGP Summary
===============================================================================
Neighbor
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.0.99.1
                65520     265    0 02h13m28s 1/0/1 (IPv4)
                          266    0
-------------------------------------------------------------------------------
```

Nice, we have sent and received _one_ IPv4 NLRI. It is surprising to see one prefix received considering that R3 does not have any exported networks, but we will deal with this later. Now lets check R3 to see if it has `R5_Customer` network in its routing table?

> **BGP mechanics**  
> I have to pause for a moment and share with you the BGP route processing diagram. It helps to understand what BGP databases are there on Nokia SROS and what path it takes through the BGP route machinery.
> ![pic](http://img-fotki.yandex.ru/get/4109/21639405.11c/0_84d72_94e5a74a_orig.png)
> <small>credits: Alcatel-Lucent Service Routing Architect (SRA) Self-Study guide, WILEY</small>  
> I will refer to these databases from now on as BGP RIB In, BGP Local-RIB and BGP RIB Out.


To see what routes are in **BGP RIB In** and BGP Local Routing Information Base (**BGP Local-RIB**) use the `show router bgp routes` command:

```txt
A:R3# show router bgp routes
===============================================================================
 BGP Router ID:10.20.20.3       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
u*>i  10.10.55.0/24                                      None        100
      10.0.99.0                                          None        -
      65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

Perfect, `10.10.55.0/24` network made its way into BGP Local-RIB

  * `*` flag means it passed validation checks
  * `u` tells us that this route is used and is present in the R3 routing table


```txt
A:R3# show router route-table 10.10.55.0

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.55.0/24                                 Remote  BGP       00h12m32s  170
       10.0.99.0                                                    0
-------------------------------------------------------------------------------
No. of Routes: 1
```

# Alcatel-Lucent eBGP reflecting routes issue

Now it is time to deal with that rogue route received by R1 from its neighbor R3.

```
*A:R1# show router bgp routes
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
i     10.10.55.0/24                                      None        None
      10.0.99.1                                          None        -
      65520 65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

AS 65510 local prefix `10.10.55.0/24` is in R1's own BGP Local-RIB, but why do wee see it there? Well, because R3 sent it to R1. But why the hell R3 sent back the `10.10.55.0/24` prefix to R1 given that it came from it?

Lets investigate NLRI propagation for this prefix:

  1. R1 sends BGP Update message to R3 with the `10.10.55.0/24` prefix and AS Path 65510.
  2. R3 receives this update, stores it in **BGP RIB In** database and checks if this NLRI is valid (nexthop resolvable, no AS Path loop) in order to put this prefix in R3's **BGP Local-RIB**.
  3. All the checks passed and R3 sends NLRI `10.10.55.0/24` back to R1 since **this is not prohibited** by [RFC 4271 A Border Gateway Protocol 4 (BGP-4)](https://tools.ietf.org/html/rfc4271) appending AS Path with its AS number.
  4. R1 receives this update and stores it in its **BGP RIB In** but this route will never make its way to **BGP Local-RIB** due to **AS Loop** error.

Based on the output from the `show router bgp routes` command and the fact that there is only one flag `i` associated with the  `10.10.55.0/24` prefix we can conclude that this prefix was not delivered to _Route Table Manager_ (RTM) and left alone in the BGP RIB In of R1. But why is that? If we issue super-useful command `show router bgp routes <prefix> hunt` for this prefix we could see what happened:

```txt
*A:R1# show router bgp routes 10.10.55.0/24 hunt
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.1
Path Id        : None
From           : 10.0.99.1
Res. Nexthop   : 10.0.99.1
Local Pref.    : None                   Interface Name : toR3
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : No Community Members
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.20.20.3
Fwd Class      : None                   Priority       : None
Flags          : Invalid  IGP  AS-Loop
Route Source   : External
AS-Path        : 65520 65510
Route Tag      : 0
Neighbor-AS    : 65520
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.0
Path Id        : None
To             : 10.0.99.1
Res. Nexthop   : n/a
Local Pref.    : n/a                    Interface Name : NotAvailable
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : 100
AIGP Metric    : None
Connector      : None
Community      : No Community Members
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.20.20.3
Origin         : IGP
AS-Path        : 65510
Route Tag      : 0
Neighbor-AS    : 65510
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
Routes : 2
===============================================================================
```

**RIB In Entries** section of this output and especially the lines "Flags" and "AS Path" answer the question why R1 will not pass `10.10.55.0/24` to the _BGP Local-RIB_ — there is an **AS Path Loop** for this NLRI. And this is the reason why this NLRI is in _BGP RIB In_ only.

# eBGP split-horizon

For those of you who came from Cisco or Juniper camps its quite strange to see that R3 send the same prefix back to R1. I agree, its hard to find a case when it would be desired to receive previously announced prefix over eBGP. To mitigate this round-trip exchange you can use the `split-horizon` command on R3. This split-horizon has nothing to do with standard iBGP split-horizon behavior (which is "do not advertise prefixes received from one iBGP peer to the other iBPG peers").

```txt
## check that 10.10.55.0/24 prefix is announcing back to R1
*A:R3# show router bgp routes 10.10.55.0/24 hunt
===============================================================================
 BGP Router ID:10.20.20.3       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
< output omitted >
-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.1
Path Id        : None
To             : 10.0.99.0
Res. Nexthop   : n/a
Local Pref.    : n/a                    Interface Name : NotAvailable
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : No Community Members
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.1
Origin         : IGP
AS-Path        : 65520 65510
Route Tag      : 0
Neighbor-AS    : 65520
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
Routes : 2
===============================================================================


## issue split-horizon command to disable this useless behavior
A:R3# configure router bgp group "eBGP"
A:R3>config>router>bgp>group# split-horizon 


## there is now no routes in RIB Out Entries section
*A:R3# show router bgp routes 10.10.55.0/24 hunt
===============================================================================
 BGP Router ID:10.20.20.3       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.0
Path Id        : None
From           : 10.0.99.0
Res. Nexthop   : 10.0.99.0

<output omitted>

-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Routes : 1
===============================================================================



## and R1 now has no routes in its RIB In and Local-RIB databases.
A:R1# show router bgp routes
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
No Matching Entries Found
===============================================================================
```

# eBGP resulting configuration

Check the resulting eBGP config that you would have on your routers at this moment:

R1:
```txt
A:R1>config>router>bgp# info
----------------------------------------------
            group "eBGP"
                export "R5_Customer_export"
                peer-as 65520
                split-horizon
                neighbor 10.0.99.1
                exit
            exit
            no shutdown
----------------------------------------------

A:R1>config>router>policy-options# info
----------------------------------------------
            prefix-list "R5_Customer_pfx"
                prefix 10.10.55.0/24 exact
            exit
            policy-statement "R5_Customer_export"
                entry 10
                    from
                        prefix-list "R5_Customer_pfx"
                    exit
                    to
                        protocol bgp
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------

A:R1# show router bgp neighbor 10.0.99.1 advertised-routes
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
i     10.10.55.0/24                                      n/a         100
      10.0.99.0                                          None        -
      65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================


A:R1# show router bgp neighbor 10.0.99.1 received-routes
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
No Matching Entries Found
===============================================================================
```
R2:
```txt
A:R2>config>router>bgp# info
----------------------------------------------
            group "eBGP"
                export "R5_Customer_export"
                peer-as 65520
                split-horizon
                neighbor 10.0.99.3
                exit
            exit
            no shutdown
----------------------------------------------

A:R2>config>router>policy-options# info
----------------------------------------------
            prefix-list "R5_Customer_pfx"
                prefix 10.10.55.0/24 exact
            exit
            policy-statement "R5_Customer_export"
                entry 10
                    from
                        prefix-list "R5_Customer_pfx"
                    exit
                    to
                        protocol bgp
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------



A:R2# show router bgp neighbor 10.0.99.3 advertised-routes
===============================================================================
 BGP Router ID:10.10.10.2       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
i     10.10.55.0/24                                      n/a         200
      10.0.99.2                                          None        -
      65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================



A:R2# show router bgp neighbor 10.0.99.3 received-routes
===============================================================================
 BGP Router ID:10.10.10.2       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
No Matching Entries Found
===============================================================================
```
R3:
```txt
A:R3>config>router>bgp# info
----------------------------------------------
            group "eBGP"
                peer-as 65510
                split-horizon
                neighbor 10.0.99.0
                exit
            exit
            no shutdown
----------------------------------------------




A:R3# show router bgp neighbor 10.0.99.0 advertised-routes
===============================================================================
 BGP Router ID:10.20.20.3       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
No Matching Entries Found
===============================================================================



A:R3# show router bgp neighbor 10.0.99.0 received-routes
===============================================================================
 BGP Router ID:10.20.20.3       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
u*>i  10.10.55.0/24                                      n/a         100
      10.0.99.0                                          None        -
      65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```
R4:
```txt
A:R4>config>router>bgp# info
----------------------------------------------
            group "eBGP"
                peer-as 65510
                split-horizon
                neighbor 10.0.99.2
                exit
            exit
            no shutdown
----------------------------------------------



A:R4# show router bgp neighbor 10.0.99.2 advertised-routes
===============================================================================
 BGP Router ID:10.20.20.4       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
No Matching Entries Found
===============================================================================




A:R4# show router bgp neighbor 10.0.99.2 received-routes
===============================================================================
 BGP Router ID:10.20.20.4       AS:65520       Local AS:65520
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
u*>i  10.10.55.0/24                                      n/a         200
      10.0.99.2                                          None        -
      65510
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

# iBGP configuration

iBGP sessions are established inside BGP Autonomous System and are used to distribute BGP routes between the routers there. In our case we have two Autonomous Systems, so we will configure full mesh of iBGP sessions within AS 65510 and AS 66520:

![pic](http://img-fotki.yandex.ru/get/6527/21639405.11c/0_84ca3_3adf0431_orig.png)

The reason we need to provide a full-mesh of iBGP sessions is dictated by the [iBGP split-horizon rule](https://supportforums.cisco.com/discussion/11487611/why-we-need-bgp-split-horizon-rule). Starting with AS 65510, configure _iBGP_ peer group for every router inside this AS and specify the other routers `system` IP addresses as a neighbor. For iBGP it is quite common to use `system` or loopback IP address (in contrast with link addresses used in eBGP) as a neighbor address because this enables IGP path redundancy.

Configuration sequence is straightforward:

  1. create "iBGP" peer group
  2. set local AS Number as a `peer-as` inside the iBGP peer group
  3. specify the neighbors using their `system` interface addresses

```txt
## repeat configuration steps on all routers in AS 65510 and AS 65520
*A:R1# configure router bgp group "iBGP"
*A:R1>config>router>bgp>group# info
----------------------------------------------
                ## iBGP peers share the same AS Number in peer-as command 
                peer-as 65510
                neighbor 10.10.10.2
                exit
                neighbor 10.10.10.5
                exit
                neighbor 10.10.10.6
                exit
----------------------------------------------
```

Note, that you do not need to specify the local-address statement (though it is not prohibited) since SROS router will initiate TCP socket opening from its system IP address by default.

To verify that iBGP sessions have been successfully established you can use good-old `show router bgp summary` or fancy `show router bgp group <group name>` commands:

```txt
A:R1# show router bgp group "iBGP"

===============================================================================
BGP Group : iBGP
===============================================================================
-------------------------------------------------------------------------------
Group            : iBGP
-------------------------------------------------------------------------------
Description      : (Not Specified)
Group Type       : No Type              State            : Up
Peer AS          : 65510                Local AS         : 65510
Local Address    : n/a                  Loop Detect      : Ignore
Import Policy    : None Specified / Inherited
Export Policy    : None Specified / Inherited
Hold Time        : 90                   Keep Alive       : 30
Min Hold Time    : 0
Cluster Id       : None                 Client Reflect   : Enabled
NLRI             : Unicast              Preference       : 170
TTL Security     : Disabled             Min TTL Value    : n/a
Graceful Restart : Disabled             Stale Routes Time: n/a
Restart Time     : n/a
Auth key chain   : n/a
Bfd Enabled      : Disabled             Disable Cap Nego : Disabled
Creation Origin  : manual
Flowspec Validate: Disabled             Default Route Tgt: Disabled
Aigp Metric      : Disabled
Split Horizon    : Disabled
Damp Peer Oscill*: Disabled
GR Notification  : Disabled             Fault Tolerance  : Disabled
Next-Hop Unchang*: None

List of Peers
- 10.10.10.2 :
- 10.10.10.5 :
- 10.10.10.6 :

Total Peers      : 3                    Established      : 3
-------------------------------------------------------------------------------
Peer Groups : 1
===============================================================================
```

Ok, now we got iBGP full-mesh configured for both ASes but to start playing with iBGP let me introduce you to another customer network - `R3_Ext_Customer - 172.16.33.0/24`. This customer network resides beside R3 and you should add it to the BGP with the same policies/export routine as we did before for `R5_Customer`.

```txt
## 1. create interface to emulate R3_Ext_Customer network
*A:R3# configure router interface R3_Ext_Customer
*A:R3>config>router>if$ address 172.16.33.1/24
*A:R3>config>router>if$ loopback

## 2. configure policy statement to export specific prefix to bgp
*A:R3>config>router>policy-options# info
----------------------------------------------
            prefix-list "R3_Ext_Customer"
                prefix 172.16.33.0/24 exact
            exit
            policy-statement "export_R3_Ext_Customer"
                entry 10
                    from
                        prefix-list "R3_Ext_Customer"
                    exit
                    to
                        protocol bgp
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------

## 3. export
*A:R3# configure router bgp group "eBGP" export "export_R3_Ext_Customer"
```

What happens next? Correct, `R3_Ext_Customer` NLRI goes from R3 to R1 via eBGP. R1 checks if this NLRI is valid by checking the AS Path for looping and the next-hop for reachability.

Since the default behavior of the eBGP is to set its **egress** interface's IP address as a next-hop, we see that R1 receives BGP routes with `10.0.99.1` address as the next-hop:

```txt
A:R1# show router bgp neighbor 10.0.99.1 received-routes
===============================================================================
 BGP Router ID:10.10.10.1       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
u*>i  172.16.33.0/24                                     n/a         None
      10.0.99.1                                          None        -
      65520
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

This next-hop is reachable to R1 since it has `toR3` interface in this network. So R1 has every right to pass NLRI `10.0.99.1` to the _BGP Local-RIB_ and then to the Routing Table Manager (RTM then installs this route to R1's routing table).

And now iBGP on R1 comes into play by advertising NLRI `10.0.99.1` to its iBGP peers. This is the default BGP's behavior to advertise valid BGP routes came from eBGP peer to all iBGP peers, and the most important part of this eBGP->iBGP redistribution is that the **next-hop** once set by eBGP peer (R3 in our case) **goes unchanged** in iBGP updates:

![pic](http://img-fotki.yandex.ru/get/36/21639405.11c/0_84ca4_7c4fdef1_orig.png)

Take a look at R5's BGP routes:

```txt
A:R5# show router bgp routes
===============================================================================
 BGP Router ID:10.10.10.5       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
i     172.16.33.0/24                                     100         None
      10.0.99.1                                          None        -
      65520
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

R5 received `R3_Ext_Customer 172.16.33.0/24` NLRI but it cant use it (`u` flag is absent). Invoke `hunt` command to see whats wrong:

```txt
A:R5# show router bgp routes 172.16.33.0/24 hunt
===============================================================================
 BGP Router ID:10.10.10.5       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
Network        : 172.16.33.0/24
Nexthop        : 10.0.99.1
Path Id        : None
From           : 10.10.10.1
Res. Nexthop   : Unresolved
Local Pref.    : 100                    Interface Name : NotAvailable
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : No Community Members
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.1
Fwd Class      : None                   Priority       : None
Flags          : Invalid  IGP  Nexthop-Unresolved
Route Source   : Internal
AS-Path        : 65520
Route Tag      : 0
Neighbor-AS    : 65520
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

Aha, R5 cant validate received NLRI since its next-hop is unresolvable to R5. Recall the R1 did not change next-hop information it received from R3, so R5 received the same IP address `10.0.99.1` as a next-hop and R5 has no route towards it. That is the reason that R5's routing table has no network `10.0.99.1`:

```txt
A:R5# show router route-table 176.16.33.0/24

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
No. of Routes: 0
```

There are two approaches to fix this:

  1. use `next-hop-self` command on R1
  2. adding eBGP interfaces to IGP process (as passive interface) making them known to every router participating in the IGP domain. Or implementing static or default routes in AS 65510 to reach R3's interface network

We will stick to the first option.

## iBGP next-hop-self

The `next-hop-self` command forces iBGP speaker, who received an eBGP update message to substitute next-hop information with its `system` IP address.

```txt
A:R1# configure router bgp group "iBGP"
A:R1>config>router>bgp>group# next-hop-self
```

Get back to R5 and check whats changed:

```txt
A:R5# show router bgp routes
===============================================================================
 BGP Router ID:10.10.10.5       AS:65510       Local AS:65510
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Flag  Network                                            LocalPref   MED
      Nexthop (Router)                                   Path-Id     Label
      As-Path
-------------------------------------------------------------------------------
u*>i  172.16.33.0/24                                     100         None
      10.10.10.1                                         None        -
      65520
-------------------------------------------------------------------------------
Routes : 1
===============================================================================
```

Now it is a totally different story! R5 successfully validates the received NLRI and can use it thanks to resolvable next-hop which is R1's system IP address `10.10.10.1`.

The next step is to pass this route to the RTM which is responsible for routing-table provisioning. If we take a look at R5 routing table for the recently received `172.16.33.0/24` prefix we will see that next-hop isn't `10.10.10.1`:

```txt
A:R5# show router route-table 172.16.33.0/24

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
172.16.33.0/24                                Remote  BGP       00h41m45s  170
       10.10.99.4                                                   0
-------------------------------------------------------------------------------
No. of Routes: 1
```

The reason behind this discrepancy is that the routing table should have connected networks as a next-hop and since `10.10.10.1` is far from being connected to R5 it performs an operation called **recursive lookup**. R5 takes next-hop value received from the iBGP update `10.10.10.1` and performs the route-table lookup:

```txt
A:R5# show router route-table 10.10.10.1

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.10.1/32                                 Remote  ISIS      00h44m28s  15
       10.10.99.4                                                   100
-------------------------------------------------------------------------------
No. of Routes: 1
```

R5 knows how to reach `10.10.10.1` by means of IS-IS protocol and the next-hop for this prefix is indeed `10.10.99.4` which is a connected network:

```txt
A:R5# show router route-table 10.10.99.4

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.10.99.4/31                                 Local   Local     00h44m45s  0
       toR1                                                         0
-------------------------------------------------------------------------------
No. of Routes: 1
```

That is why we see a different next-hop in the routing and BGP Local-RIB tables.

# Wrapping up

To this moment we have done a good job - we have configured the peering between two autonomous systems AS 65510 and AS 65520 and successfully exchanged the prefixes. Now, a client residing in the _R3\_Ext\_Customer_ network can reach hosts from the _R5\_Customer_ network:

```txt
## we have to specify a source address for ping to success,
## since by default ALU routers perform ping from their system interface
## and AS 65510 know nothing about system addresses of foreign AS.
A:R3# ping 10.10.55.1 source 172.16.33.1 
PING 10.10.55.1 56 data bytes
64 bytes from 10.10.55.1: icmp_seq=1 ttl=63 time=9.38ms.
64 bytes from 10.10.55.1: icmp_seq=2 ttl=63 time=3.58ms.
64 bytes from 10.10.55.1: icmp_seq=3 ttl=63 time=3.13ms.
64 bytes from 10.10.55.1: icmp_seq=4 ttl=63 time=28.7ms.
64 bytes from 10.10.55.1: icmp_seq=5 ttl=63 time=103ms.

---- 10.10.55.1 PING Statistics ----
5 packets transmitted, 5 packets received, 0.00% packet loss
```

This was accomplished by mutual exchange of the corresponding routes both via eBGP and iBGP protocols.

If some of you want to get the full picture - see this configuration snapshot captured on every router of this topology:

R1:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "system"
            address 10.10.10.1/32
            no shutdown
        exit
        interface "toR2"
            address 10.10.99.0/31
            port 1/1/1
            no shutdown
        exit
        interface "toR3"
            address 10.0.99.0/31
            port 1/1/3
            no shutdown
        exit
        interface "toR5"
            address 10.10.99.4/31
            port 1/1/4
            no shutdown
        exit                          
        autonomous-system 65510
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 10.10
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only     
            exit
            interface "system"
                no shutdown
            exit
            interface "toR2"
                interface-type point-to-point
                no shutdown
            exit
            interface "toR5"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service
        customer 1 create
            description "Default customer"
        exit                          
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            prefix-list "R5_Customer_pfx"
                prefix 10.10.55.0/24 exact
            exit
            policy-statement "R5_Customer_export"
                entry 10
                    from
                        prefix-list "R5_Customer_pfx"
                    exit
                    to
                        protocol bgp
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
            group "eBGP"
                export "R5_Customer_export" 
                peer-as 65520         
                split-horizon
                neighbor 10.0.99.1
                    local-address 10.0.99.0
                exit
            exit
            group "iBGP"
                next-hop-self
                peer-as 65510
                neighbor 10.10.10.2
                exit
                neighbor 10.10.10.5
                exit
                neighbor 10.10.10.6
                exit
            exit
            no shutdown
        exit
    exit


exit all
```
R2:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "system"
            address 10.10.10.2/32
            no shutdown
        exit
        interface "toR1"
            address 10.10.99.1/31
            port 1/1/1
            no shutdown
        exit
        interface "toR4"
            address 10.0.99.2/31
            port 1/1/3
            no shutdown
        exit
        interface "toR6"
            address 10.10.99.2/31     
            port 1/1/4
            no shutdown
        exit
        autonomous-system 65510
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 10.10
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only
            exit                      
            interface "system"
                no shutdown
            exit
            interface "toR1"
                interface-type point-to-point
                no shutdown
            exit
            interface "toR6"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service                           
        customer 1 create
            description "Default customer"
        exit
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            prefix-list "R5_Customer_pfx"
                prefix 10.10.55.0/24 exact
            exit
            policy-statement "R5_Customer_export"
                entry 10
                    from
                        prefix-list "R5_Customer_pfx"
                    exit
                    to
                        protocol bgp
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
            group "eBGP"
                export "R5_Customer_export" 
                peer-as 65520
                split-horizon
                neighbor 10.0.99.3
                    local-address 10.0.99.2
                exit
            exit
            group "iBGP"
                peer-as 65510
                neighbor 10.10.10.1
                exit
                neighbor 10.10.10.5
                exit
                neighbor 10.10.10.6
                exit
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "System Time NTP Configuration"
#--------------------------------------------------
    system
        time
            ntp
            exit
        exit
    exit

exit all
```
R3:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "R3_Ext_Customer"
            address 172.16.33.1/24
            loopback
            no shutdown
        exit
        interface "system"
            address 10.20.20.3/32
            no shutdown
        exit
        interface "toR1"
            address 10.0.99.1/31
            port 1/1/3
            no shutdown
        exit
        interface "toR4"              
            address 10.20.99.0/31
            port 1/1/2
            no shutdown
        exit
        autonomous-system 65520
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 20.20
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only     
            exit
            interface "system"
                no shutdown
            exit
            interface "toR4"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service
        customer 1 create
            description "Default customer"
        exit
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            prefix-list "R3_Ext_Customer"
                prefix 172.16.33.0/24 exact
            exit
            policy-statement "export_R3_Ext_Customer"
                entry 10              
                    from
                        prefix-list "R3_Ext_Customer"
                    exit
                    to
                        protocol bgp
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
            group "eBGP"
                export "export_R3_Ext_Customer" 
                peer-as 65510
                split-horizon
                neighbor 10.0.99.0
                    local-address 10.0.99.1
                exit
            exit                      
            group "iBGP"
                next-hop-self
                peer-as 65520
                neighbor 10.20.20.4
                exit
            exit
            no shutdown
        exit
    exit


exit all
```
R4:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "system"
            address 10.20.20.4/32
            no shutdown
        exit
        interface "toR2"
            address 10.0.99.3/31
            port 1/1/3
            no shutdown
        exit
        interface "toR3"
            address 10.20.99.1/31
            port 1/1/2
            no shutdown
        exit
        autonomous-system 65520
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf                          
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 20.20
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only
            exit
            interface "system"
                no shutdown
            exit
            interface "toR3"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown               
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service
        customer 1 create
            description "Default customer"
        exit
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"             
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "BGP Configuration"
#--------------------------------------------------
        bgp
            group "eBGP"
                peer-as 65510
                split-horizon
                neighbor 10.0.99.2
                    local-address 10.0.99.3
                exit
            exit
            group "iBGP"
                next-hop-self
                peer-as 65520
                neighbor 10.20.20.3
                exit
            exit
            no shutdown
        exit
    exit                              


exit all
```
R5:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "R5_Customer_loopback"
            address 10.10.55.1/24
            loopback
            no shutdown
        exit
        interface "system"
            address 10.10.10.5/32
            no shutdown
        exit
        interface "toR1"
            address 10.10.99.5/31
            port 1/1/4
            no shutdown
        exit
        interface "toR6"
            address 10.10.99.6/31
            port 1/1/1
            no shutdown
        exit                          
        autonomous-system 65510
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 10.10
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only
            exit
            interface "system"
                no shutdown
            exit                      
            interface "R5_Customer_loopback"
                passive
                no shutdown
            exit
            interface "toR1"
                interface-type point-to-point
                no shutdown
            exit
            interface "toR6"
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service
        customer 1 create
            description "Default customer"
        exit                          
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "BGP Configuration"
#--------------------------------------------------
        bgp
            group "iBGP"
                peer-as 65510         
                neighbor 10.10.10.1
                exit
                neighbor 10.10.10.2
                exit
                neighbor 10.10.10.6
                exit
            exit
            no shutdown
        exit
    exit


exit all
```
R6:
```txt
#--------------------------------------------------
echo "Router (Network Side) Configuration"
#--------------------------------------------------
    router 
        interface "system"
            address 10.10.10.6/32
            no shutdown
        exit
        interface "toR2"
            address 10.10.99.3/31
            port 1/1/4
            no shutdown
        exit
        interface "toR5"
            address 10.10.99.7/31
            port 1/1/1
            no shutdown
        exit
        autonomous-system 65510
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf                          
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            level-capability level-1
            area-id 10.10
            reference-bandwidth 100000000
            level 1
                wide-metrics-only
            exit
            level 2
                wide-metrics-only
            exit
            interface "system"
                no shutdown
            exit
            interface "toR2"
                interface-type point-to-point
                no shutdown
            exit
            interface "toR5"          
                interface-type point-to-point
                no shutdown
            exit
            no shutdown
        exit
    exit

#--------------------------------------------------
echo "Service Configuration"
#--------------------------------------------------
    service
        customer 1 create
            description "Default customer"
        exit
    exit
#--------------------------------------------------
echo "Router (Service Side) Configuration"
#--------------------------------------------------
    router 
#--------------------------------------------------
echo "OSPFv2 Configuration"
#--------------------------------------------------
        ospf                          
            no shutdown
        exit
#--------------------------------------------------
echo "ISIS Configuration"
#--------------------------------------------------
        isis
            no shutdown
        exit
#--------------------------------------------------
echo "BGP Configuration"
#--------------------------------------------------
        bgp
            group "iBGP"
                peer-as 65510
                neighbor 10.10.10.1
                exit
                neighbor 10.10.10.2
                exit
                neighbor 10.10.10.5
                exit
            exit
            no shutdown
        exit                          
    exit


exit all
```

And for those of you who's motto is _"pcap or it didnt happen"_ I share the wireshark dumps for these links:

  * [R1 - R3](https://drive.google.com/file/d/0BwGlWrU8lplrMkhiZUwxeVIyQmM/view?usp=sharing) (eBGP operation)
  * [R2 - R4](https://drive.google.com/file/d/0BwGlWrU8lplrOTFZcnBZZkxPSkk/view?usp=sharing) (eBGP operation)
  * [R1 - R5](https://drive.google.com/file/d/0BwGlWrU8lplrSE4xU2JQYi1hdVU/view?usp=sharing) (iBGP operation)

