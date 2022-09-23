---
title: Nokia (Alcatel-Lucent) SROS OSPF configuration tutorial
date: 2015-06-22
author: Roman Dodin
url: /2015/06/alcatel-lucent-ospf-configuration-tutorial/
# toc: true
draft: false
comments: true
tags:
  - SROS
  - Nokia
  - OSPF
---


The purpose of this post is to cover basic [OSPFv2](https://datatracker.ietf.org/doc/html/rfc2328) configuration steps and commands for Nokia SROS routers. Intended readers are engineers with basic OSPF knowledge who want to know how to configure OSPF on Alcatel-Lucent Service Routers (7750-SR, 7705-SR, 7210-SR).

All examples are valid for `TiMOS-B-12.0.R8` software.
<!--more-->

# Single-area OSPF

Basic OSPF protocol configuration in a single area consists of the following steps:

  1. Enable OSPF globally
  2. Configure router with OSPF _Router ID_
  3. Configure backbone OSPF _Area 0_
  4. Include interfaces in _Area 0_

The following network topology will be used throughout this tutorial:

<img class="aligncenter" src="http://img-fotki.yandex.ru/get/9739/21639405.11b/0_83cb2_d11bc8dc_XL.png" alt="" width="530" height="705" />

## Enabling OSPF

To enable OSPF on a router simply issue `configure router ospf` command. This will start OSPF process #0 on a router. If you would like to run another separate OSPF process on the same router, use  `configure router ospf <N>`, where _N_ is a decimal number of the desired OSPF process.

## Router ID

Each router running OSPF should have an unique 32-bit identifier, namely **Router ID**. This identifier will be equal to the first configured value in the following prioritized:

  1. `router-id` value configured globally for a router
  2. `system` interface IPv4 address value
  3. the last 32 bits of the chassis MAC address

Configuring router-id explicitly:

```
*A:R1# configure router router-id
  - no router-id
  - router-id  <ip-address>

  <ip-address>         : a.b.c.d

*A:R1# configure router router-id 2.2.2.2
```

Use `show router ospf status` command to check Router ID current value and OSPF status:

```
*A:R1# show router ospf status

===============================================================================
OSPFv2 (0) Status
===============================================================================
OSPF Cfg Router Id           : 0.0.0.0
OSPF Oper Router Id          : 1.1.1.1    # Router ID inherited from System IPv4 address
OSPF Version                 : 2
OSPF Admin Status            : Enabled    # OSPF administratively enabled
OSPF Oper Status             : Enabled    # OSPF is operating

<output omitted>
```

## Configuring Backbone Area

Are configuration is done in the OSPF configuration context with `area` command:

```
A:R1>config>router>ospf# area
  - area  <area-id>
  - no area  <area-id>

  <area-id>            :  <ip-address> |  [0..4294967295]
```

Area ID can be set either as decimal (`area 0`) or in dotted-decimal format (`area 0.0.0.0`).

It is easier to enable OSPF and set the Area ID in a single sweep:

```
# This command will enable OSPF process (it is disabled by default) and configure Area 0 on this router.

A:R1# configure router ospf area 0
```

To check all the configured areas on a router use `show router ospf area` command:

```
A:R1# show router ospf area

==================================================================
OSPFv2 (0) all areas
==================================================================
Area Id         Type        SPF Runs    LSA Count   LSA Cksum Sum
------------------------------------------------------------------
0.0.0.0         Standard    2           1           0xcaf7
------------------------------------------------------------------
No. of OSPF Areas: 1
==================================================================
```

## Configuring OSPF interfaces

Once the _backbone area_ is configured its time to add some interfaces to it with `interface <interface_name>` command.

```dockerfile
# Entering to OSPF Area 0 configuration context
*A:R1# configure router ospf area 0

# Adding system interface to OSPF process
*A:R1>config>router>ospf>area# interface "system"
*A:R1>config>router>ospf>area>if$ back

# Adding interface toR2 and configuring it with point-to-point type
# By default, ethernet interfaces use Broadcast interface type 
*A:R1>config>router>ospf>area# interface "toR2"
*A:R1>config>router>ospf>area>if$ interface-type point-to-point
*A:R1>config>router>ospf>area>if$ back
*A:R1>config>router>ospf>area# back

# This configuration steps effectively lead us to this OSPF configuration for router R1
*A:R1>config>router>ospf# info
----------------------------------------------
            area 0.0.0.0
                interface "system"
                    no shutdown
                exit
                interface "toR2"
                    interface-type point-to-point
                    no shutdown
                exit
            exit
            no shutdown
----------------------------------------------
```

To check that OSPF interfaces were configured properly by evaluating their status use:

```
*A:R1# show router ospf interface

===============================================================================
OSPFv2 (0) all interfaces
===============================================================================
If Name               Area Id         Designated Rtr  Bkup Desig Rtr  Adm  Oper
-------------------------------------------------------------------------------
system                0.0.0.0         1.1.1.1         0.0.0.0         Up   DR
toR2                  0.0.0.0         0.0.0.0         0.0.0.0         Up   PToP
-------------------------------------------------------------------------------
No. of OSPF Interfaces: 2
===============================================================================
```

Repeat the same configuration steps to include all interfaces to _OSPF Area 0_ for the other backbone routers R2, R3, R4 and you will end up with a fully configured _OSPF Backbone Area_.

## Verification

Finally its time to check that our routers have established the neighboring relationships:

```
A:R1# show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR2                             2.2.2.2         Full       1    0       33
   0.0.0.0
toR3                             3.3.3.3         Full       1    0       39
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 2
===============================================================================
```

One of the most useful OSPF verification commands is `show router ospf database`. This command shows all the _Links State Advertisements_ (LSA) and helps the engineer to troubleshoot OSPF-related issues.

```
A:R1# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.0         1.1.1.1         1.1.1.1         873  0x8000000b 0x4dd5
Router  0.0.0.0         2.2.2.2         2.2.2.2         561  0x80000006 0x1c2b
Router  0.0.0.0         3.3.3.3         3.3.3.3         879  0x80000008 0x6d94
Router  0.0.0.0         4.4.4.4         4.4.4.4         1588 0x80000005 0x94ec
-------------------------------------------------------------------------------
No. of LSAs: 4
===============================================================================
```

You can query OSPF database for a specific LSAs by augmenting the above mentioned command:

```
A:R1# show router ospf database
  - database [type {router|network|summary|asbr-summary|external|nssa|all}]
    [area  <area-id>] [adv-router  <router-id>] [ <link-state-id>] [detail]

  <router|network|su*> : keywords - specify database type
  <area-id>            : ip-address - a.b.c.d
                        area - [0..4294967295]
  <router-id>          : a.b.c.d
  <link-state-id>      : a.b.c.d
  <detail>             : keyword - displays detailed information
```

# Multi-area OSPF

Basic Multi-area OSPF configuration is straightforward as well. I added two more routers to the topology and introduced two areas: Area 1 and Area 2.

![pic](http://img-fotki.yandex.ru/get/6828/21639405.11b/0_83cb9_73aa3ab3_orig.png)

<small>I mistyped the port numbers for R5-R1 and R6-R2 pairs, it should be 1/1/4. Though this wont affect the course of this tutorial in anyway.</small>

We will start by configuring `Area 1` on routers R5 and R1 using the same commands we used for single-area OSPF configuration.

R5 configuration:

```dockerfile
# Creating Area 1 on R5 and adding "system" and "toR1" interfaces
A:R5# configure router ospf area 1
*A:R5>config>router>ospf>area$ interface "toR1" interface-type point-to-point
*A:R5>config>router>ospf>area$ interface "system"


# Verifying created Area 1 and its interfaces
*A:R5# show router ospf interface

===============================================================================
OSPFv2 (0) all interfaces
===============================================================================
If Name               Area Id         Designated Rtr  Bkup Desig Rtr  Adm  Oper
-------------------------------------------------------------------------------
system                0.0.0.1         5.5.5.5         0.0.0.0         Up   DR
toR1                  0.0.0.1         0.0.0.0         0.0.0.0         Up   PToP
-------------------------------------------------------------------------------
No. of OSPF Interfaces: 2
===============================================================================
```

R1 configuration

```dockerfile
# Creating Area 1 on R1 (ABR) and adding "toR5" interface to it.

*A:R1# configure router ospf area 1
*A:R1>config>router>ospf>area$ interface "toR5" interface-type point-to-point


# Verifying created Area 1 and its interfaces
*A:R1# show router ospf interface

===============================================================================
OSPFv2 (0) all interfaces
===============================================================================
If Name               Area Id         Designated Rtr  Bkup Desig Rtr  Adm  Oper
-------------------------------------------------------------------------------
system                0.0.0.0         1.1.1.1         0.0.0.0         Up   DR
toR2                  0.0.0.0         0.0.0.0         0.0.0.0         Up   PToP
toR3                  0.0.0.0         0.0.0.0         0.0.0.0         Up   PToP
toR5                  0.0.0.1         0.0.0.0         0.0.0.0         Up   PToP
-------------------------------------------------------------------------------
No. of OSPF Interfaces: 4
===============================================================================
```

Adding one more _Area_ (besides backbone Area 0) on R1 makes it _Area Border Router._ So R1 will form and maintain another neighbor relationships with R5 in Area 1. We will check if its true:

R5 verification:

```
*A:R5# show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR1                             1.1.1.1         Full       1    0       33
   0.0.0.1
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================
```

R1 verification:

```
*A:R1# show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR2                             2.2.2.2         Full       1    0       32
   0.0.0.0
toR3                             3.3.3.3         Full       1    0       36
   0.0.0.0
toR5                             5.5.5.5         Full       1    0       31
   0.0.0.1
-------------------------------------------------------------------------------
No. of Neighbors: 3
===============================================================================
```

I repeated same configuration steps on R6: added it to Area 2 and neighbored with R2.

## Examining Multi-area LSDB

Since we configured multi-area OSPF we should expect to see some new LSA in our Link State Database:

On R1:

```
A:R1# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.0         1.1.1.1         1.1.1.1         550  0x80000007 0x58cd
Router  0.0.0.0         2.2.2.2         2.2.2.2         668  0x80000006 0xaf65
Router  0.0.0.0         3.3.3.3         3.3.3.3         193  0x80000006 0x7192
Router  0.0.0.0         4.4.4.4         4.4.4.4         732  0x80000007 0xa34d
Summary 0.0.0.0         5.5.5.5         1.1.1.1         773  0x80000002 0x508f
Summary 0.0.0.0         10.1.5.0        1.1.1.1         1091 0x80000002 0x7172
Summary 0.0.0.0         6.6.6.6         2.2.2.2         519  0x80000002 0x4d3
Summary 0.0.0.0         10.2.6.0        2.2.2.2         724  0x80000002 0x3ca1
Router  0.0.0.1         1.1.1.1         1.1.1.1         830  0x80000004 0x50ea
Router  0.0.0.1         5.5.5.5         5.5.5.5         171  0x80000005 0x47bb
Summary 0.0.0.1         1.1.1.1         1.1.1.1         660  0x80000002 0x1d37
Summary 0.0.0.1         2.2.2.2         1.1.1.1         183  0x80000002 0xda11
Summary 0.0.0.1         3.3.3.3         1.1.1.1         122  0x80000002 0xac3b
Summary 0.0.0.1         4.4.4.4         1.1.1.1         318  0x80000002 0x6a15
Summary 0.0.0.1         6.6.6.6         1.1.1.1         207  0x80000002 0xe69
Summary 0.0.0.1         10.1.2.0        1.1.1.1         377  0x80000003 0x9055
Summary 0.0.0.1         10.1.3.0        1.1.1.1         262  0x80000003 0x855f
Summary 0.0.0.1         10.2.4.0        1.1.1.1         1039 0x80000003 0x5a24
Summary 0.0.0.1         10.2.6.0        1.1.1.1         864  0x80000002 0x4637
Summary 0.0.0.1         10.3.4.0        1.1.1.1         1056 0x80000003 0x4e2f
-------------------------------------------------------------------------------
No. of LSAs: 20
===============================================================================
```

On R5:

```
A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         900  0x80000004 0x50ea
Router  0.0.0.1         5.5.5.5         5.5.5.5         238  0x80000005 0x47bb
Summary 0.0.0.1         1.1.1.1         1.1.1.1         728  0x80000002 0x1d37
Summary 0.0.0.1         2.2.2.2         1.1.1.1         252  0x80000002 0xda11
Summary 0.0.0.1         3.3.3.3         1.1.1.1         190  0x80000002 0xac3b
Summary 0.0.0.1         4.4.4.4         1.1.1.1         387  0x80000002 0x6a15
Summary 0.0.0.1         6.6.6.6         1.1.1.1         276  0x80000002 0xe69
Summary 0.0.0.1         10.1.2.0        1.1.1.1         446  0x80000003 0x9055
Summary 0.0.0.1         10.1.3.0        1.1.1.1         329  0x80000003 0x855f
Summary 0.0.0.1         10.2.4.0        1.1.1.1         1106 0x80000003 0x5a24
Summary 0.0.0.1         10.2.6.0        1.1.1.1         932  0x80000002 0x4637
Summary 0.0.0.1         10.3.4.0        1.1.1.1         1124 0x80000003 0x4e2f
-------------------------------------------------------------------------------
No. of LSAs: 12
===============================================================================
```

Aha, R1 being an ABR lists all LSA's for both Area 0 and Area 1. Moreover, R1 lists _Type 3 Summary LSA from Area 0 to Area 1_ and vice versa, _from Area 1 to Area 0_.

R5 has only Area 1 LSAs, since R5 "lives" exactly in a single area - Area 1.

# OSPF routes propagation

To ensure that OSPF routers exchanged OSPF routes lets check R5 and R1 routing tables:

On R1 (ABR):

```dockerfile
# Checking routes that have been received via OSPF

*A:R1# show router route-table protocol ospf

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
2.2.2.2/32                                    Remote  OSPF      03h01m17s  10
       10.1.2.2                                                     100
3.3.3.3/32                                    Remote  OSPF      03h01m13s  10
       10.1.3.3                                                     100
4.4.4.4/32                                    Remote  OSPF      03h01m10s  10
       10.1.2.2                                                     200
5.5.5.5/32                                    Remote  OSPF      00h39m07s  10
       10.1.5.5                                                     100
6.6.6.6/32                                    Remote  OSPF      00h19m38s  10
       10.1.2.2                                                     200
10.2.4.0/24                                   Remote  OSPF      04h15m26s  10
       10.1.2.2                                                     200
10.2.6.0/24                                   Remote  OSPF      00h19m48s  10
       10.1.2.2                                                     200
10.3.4.0/24                                   Remote  OSPF      04h15m26s  10
       10.1.3.3                                                     200
-------------------------------------------------------------------------------
No. of Routes: 8
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================


# Checking R1's route table

A:R1# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
1.1.1.1/32                                    Local   Local     00h20m56s  0
       system                                                       0
2.2.2.2/32                                    Remote  OSPF      00h15m29s  10
       10.1.2.2                                                     100
3.3.3.3/32                                    Remote  OSPF      00h15m11s  10
       10.1.3.3                                                     100
4.4.4.4/32                                    Remote  OSPF      00h14m40s  10
       10.1.2.2                                                     200
5.5.5.5/32                                    Remote  OSPF      00h18m59s  10
       10.1.5.5                                                     100
6.6.6.6/32                                    Remote  OSPF      00h16m28s  10
       10.1.2.2                                                     200
10.1.2.0/24                                   Local   Local     00h20m36s  0
       toR2                                                         0
10.1.3.0/24                                   Local   Local     00h20m36s  0
       toR3                                                         0
10.1.5.0/24                                   Local   Local     00h20m36s  0
       toR5                                                         0
10.2.4.0/24                                   Remote  OSPF      00h20m31s  10
       10.1.2.2                                                     200
10.2.6.0/24                                   Remote  OSPF      00h16m38s  10
       10.1.2.2                                                     200
10.3.4.0/24                                   Remote  OSPF      00h20m30s  10
       10.1.3.3                                                     200
-------------------------------------------------------------------------------
No. of Routes: 12
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================
```

On R5:

```dockerfile
*A:R5# show router route-table protocol ospf

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
1.1.1.1/32                                    Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     100
2.2.2.2/32                                    Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     200
3.3.3.3/32                                    Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     200
4.4.4.4/32                                    Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     300
6.6.6.6/32                                    Remote  OSPF      00h20m14s  10
       10.1.5.1                                                     300
10.1.2.0/24                                   Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     200
10.1.3.0/24                                   Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     200
10.2.4.0/24                                   Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     300
10.2.6.0/24                                   Remote  OSPF      00h20m25s  10
       10.1.5.1                                                     300
10.3.4.0/24                                   Remote  OSPF      02h57m09s  10
       10.1.5.1                                                     300
-------------------------------------------------------------------------------
No. of Routes: 10
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================


# Checking R5's route table

A:R5# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
1.1.1.1/32                                    Remote  OSPF      00h20m13s  10
       10.1.5.1                                                     100
2.2.2.2/32                                    Remote  OSPF      00h19m27s  10
       10.1.5.1                                                     200
3.3.3.3/32                                    Remote  OSPF      00h19m09s  10
       10.1.5.1                                                     200
4.4.4.4/32                                    Remote  OSPF      00h18m37s  10
       10.1.5.1                                                     300
5.5.5.5/32                                    Local   Local     00h24m57s  0
       system                                                       0
6.6.6.6/32                                    Remote  OSPF      00h20m25s  10
       10.1.5.1                                                     300
10.1.2.0/24                                   Remote  OSPF      00h23m46s  10
       10.1.5.1                                                     200
10.1.3.0/24                                   Remote  OSPF      00h23m46s  10
       10.1.5.1                                                     200
10.1.5.0/24                                   Local   Local     00h24m37s  0
       toR1                                                         0
10.2.4.0/24                                   Remote  OSPF      00h23m47s  10
       10.1.5.1                                                     300
10.2.6.0/24                                   Remote  OSPF      00h20m36s  10
       10.1.5.1                                                     300
10.3.4.0/24                                   Remote  OSPF      00h23m47s  10
       10.1.5.1                                                     300
-------------------------------------------------------------------------------
No. of Routes: 12
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================
```

Since we configured all the routers in our topology and verified that the routes have been propagated properly we can try to run `ping` between R6 and R5 system interfaces:

```
A:R6# ping 5.5.5.5
PING 5.5.5.5 56 data bytes
64 bytes from 5.5.5.5: icmp_seq=1 ttl=62 time=11.7ms.
```

# OSPF Route Summarization

So far we have configured multi-area OSPF topology with three Areas. One of the multi-area OSPF benefits is to perform _manual route summarization_. In this section we will configure OSPF route summarization between Area 0 and Area 1.

The idea is depicted below where we will have a single Summary LSA (Type 3) in the Area 1 instead of three different LSAs.

![pic](http://img-fotki.yandex.ru/get/16191/21639405.11b/0_83cbc_fd84eebd_orig.png)

To get a range of IP addresses which we will summarize later we will add 3 loopback interfaces to R3 router and include them in OSPF Area 0:

```
A:R3# show router interface

===============================================================================
Interface Table (Router: Base)
===============================================================================
Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId
   IP-Address                                                    PfxState
-------------------------------------------------------------------------------
lo1                              Up          Up/--       Network loopback
   192.168.3.1/32                                                n/a
lo2                              Up          Up/--       Network loopback
   192.168.3.2/32                                                n/a
lo3                              Up          Up/--       Network loopback
   192.168.3.3/32                                                n/a
 <output omitted>


*A:R3# show router ospf interface

===============================================================================
OSPFv2 (0) all interfaces
===============================================================================
If Name               Area Id         Designated Rtr  Bkup Desig Rtr  Adm  Oper
-------------------------------------------------------------------------------
system                0.0.0.0         3.3.3.3         0.0.0.0         Up   DR
toR1                  0.0.0.0         0.0.0.0         0.0.0.0         Up   PToP
toR4                  0.0.0.0         0.0.0.0         0.0.0.0         Up   PToP
lo1                   0.0.0.0         3.3.3.3         0.0.0.0         Up   DR
lo2                   0.0.0.0         3.3.3.3         0.0.0.0         Up   DR
lo3                   0.0.0.0         3.3.3.3         0.0.0.0         Up   DR
-------------------------------------------------------------------------------
No. of OSPF Interfaces: 6
===============================================================================
```

Since we added these interfaces to OSPF Area 0 we see them coming to R5 router as _Type 3 Network Summary LSA_. And these routes make their way to the routing table of R5.

```
A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         531  0x80000005 0x4eeb
Router  0.0.0.1         5.5.5.5         5.5.5.5         43   0x80000006 0x45bc
Summary 0.0.0.1         1.1.1.1         1.1.1.1         496  0x80000003 0x1b38
Summary 0.0.0.1         2.2.2.2         1.1.1.1         1898 0x80000002 0xda11
Summary 0.0.0.1         3.3.3.3         1.1.1.1         225  0x80000003 0xaa3c
Summary 0.0.0.1         4.4.4.4         1.1.1.1         463  0x80000003 0x6816
Summary 0.0.0.1         6.6.6.6         1.1.1.1         373  0x80000003 0xc6a
Summary 0.0.0.1         10.1.2.0        1.1.1.1         323  0x80000004 0x8e56
Summary 0.0.0.1         10.1.3.0        1.1.1.1         32   0x80000004 0x8360
Summary 0.0.0.1         10.2.4.0        1.1.1.1         513  0x80000004 0x5825
Summary 0.0.0.1         10.2.6.0        1.1.1.1         1089 0x80000003 0x4438
Summary 0.0.0.1         10.3.4.0        1.1.1.1         1188 0x80000004 0x4c30
Summary 0.0.0.1         192.168.3.1     1.1.1.1         566  0x80000001 0x5c2b
Summary 0.0.0.1         192.168.3.2     1.1.1.1         560  0x80000001 0x5234
Summary 0.0.0.1         192.168.3.3     1.1.1.1         554  0x80000001 0x483d
-------------------------------------------------------------------------------
No. of LSAs: 15
===============================================================================


A:R5# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
 < <ouput omitted>>

192.168.3.1/32                                Remote  OSPF      00h10m07s  10
       10.1.5.1                                                     200
192.168.3.2/32                                Remote  OSPF      00h10m02s  10
       10.1.5.1                                                     200
192.168.3.3/32                                Remote  OSPF      00h09m56s  10
       10.1.5.1                                                     200
-------------------------------------------------------------------------------
No. of Routes: 15
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================
```

We will configure route summarization on Area Border Router (R1), so it will advertise **only one** summary route `192.168.3.0/30` instead of three specific routes.

Configuration steps:

```
A:R1# configure router ospf area 0
A:R1>config>router>ospf>area# area-range 192.168.3.0/30
```

Pay attention, that summarization command `area-range` must be applied in the context of the area being summarized. Since we are summarizing routes **from Area 0** to Area 1 we use this command in the **Area 0** configuration context.

By default, the command `area-range <prefix>/<length>` will actually be expanded to `area-range <prefix>/<length> advertise`, meaning that ABR will advertise this prefix. Counterpart statement `not-advertise` can be supplied to enable route suppression and will be discussed in a detail in next section.

**Pay attention:** route summarization procedure automatically adds a _black-hole_ route in R1's route table:

```
*A:R1# show router route-table 192.168.3.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.3.0/30                                Blackh* OSPF      00h32m52s  255
       Black Hole                                                   100
192.168.3.1/32                                Remote  OSPF      00h53m58s  10
       10.1.3.3                                                     100
192.168.3.2/32                                Remote  OSPF      00h53m52s  10
       10.1.3.3                                                     100
192.168.3.3/32                                Remote  OSPF      00h53m47s  10
       10.1.3.3                                                     100
-------------------------------------------------------------------------------
No. of Routes: 4
```

Lets see what has changed at R5. R5's LSDB now has just **one** _Type 3 Summary LSA_ for the aggregated `192.168.3.0/30` network and has no LSA's for the specific prefixes:

```
A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         1234 0x80000005 0x4eeb
Router  0.0.0.1         5.5.5.5         5.5.5.5         746  0x80000006 0x45bc
Summary 0.0.0.1         1.1.1.1         1.1.1.1         1199 0x80000003 0x1b38
Summary 0.0.0.1         2.2.2.2         1.1.1.1         658  0x80000003 0xd812
Summary 0.0.0.1         3.3.3.3         1.1.1.1         928  0x80000003 0xaa3c
Summary 0.0.0.1         4.4.4.4         1.1.1.1         1166 0x80000003 0x6816
Summary 0.0.0.1         6.6.6.6         1.1.1.1         1076 0x80000003 0xc6a
Summary 0.0.0.1         10.1.2.0        1.1.1.1         1026 0x80000004 0x8e56
Summary 0.0.0.1         10.1.3.0        1.1.1.1         735  0x80000004 0x8360
Summary 0.0.0.1         10.2.4.0        1.1.1.1         1216 0x80000004 0x5825
Summary 0.0.0.1         10.2.6.0        1.1.1.1         420  0x80000004 0x4239
Summary 0.0.0.1         10.3.4.0        1.1.1.1         340  0x80000005 0x4a31
Summary 0.0.0.1         192.168.3.0     1.1.1.1         4    0x80000001 0x5437
-------------------------------------------------------------------------------
No. of LSAs: 13
===============================================================================



A:R5# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
 <ouptut omitted>    

192.168.3.0/30                                Remote  OSPF      00h30m58s  10
       10.1.5.1                                                     200
-------------------------------------------------------------------------------
No. of Routes: 13
===============================================================================
```

Verifying that IP connectivity works for summarized route:

```
A:R5# ping 192.168.3.3
PING 192.168.3.3 56 data bytes
64 bytes from 192.168.3.3: icmp_seq=1 ttl=63 time=10.2ms.
```

# OSPF Route filtering on ABR

You can filter unwanted routes on the ABR with the `area-range` command adding the key `not-advertise`.

![pic](http://img-fotki.yandex.ru/get/6422/21639405.11b/0_83cba_d148eb08_orig.png)

For example lets take a look at R6's route table which contains specific routes to R3's loopback addresses. These addresses is advertising by R2 since it is acting as ABR and advertises all the routes it has in its routing table.

```
A:R6# show router route-table 192.168.3.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.3.1/32                                Remote  OSPF      01h21m48s  10
       10.2.6.2                                                     300
192.168.3.2/32                                Remote  OSPF      01h21m43s  10
       10.2.6.2                                                     300
192.168.3.3/32                                Remote  OSPF      01h21m37s  10
       10.2.6.2                                                     300
-------------------------------------------------------------------------------
No. of Routes: 3
```

If we want to prevent R2 from advertising some routes to its neighbor in _Area 1_ then we have to add configuration commands in Area 0's context of R2:

```
A:R2# configure router ospf area 0
A:R2>config>router>ospf>area# area-range 192.168.3.1/32 not-advertise
```

By doing this, we tell R2 to stop advertising _Type 3 Summary LSA_ for prefix 192.168.3.1/32. And R6's route table immediately reflects this change by not having this specific route in its route table:

```
A:R6# show router route-table 192.168.3.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.3.2/32                                Remote  OSPF      01h28m38s  10
       10.2.6.2                                                     300
192.168.3.3/32                                Remote  OSPF      01h28m32s  10
       10.2.6.2                                                     300
-------------------------------------------------------------------------------
No. of Routes: 2
```

You can also use "summary" prefix to filter a range of routes:

```dockerfile
# filter all prefixes that falls under 192.168.3.0/30 aggregate
A:R2>config>router>ospf>area# area-range 192.168.3.0/30 not-advertise

# All loopback routes are filtered by R2
A:R6# show router route-table 192.168.3.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
No. of Routes: 0
```

**Note:** Route filtering does not install any _black-hole_ routes.

# ASBR and OSPF Route Redistribution

Routes between different routing domains can me mutually exchanged. External routers can be exported into OSPF and vice versa. The process of routes exchange is often called **route redistribution**.

![pic](http://img-fotki.yandex.ru/get/6833/21639405.11b/0_83cbe_34bbedc2_orig.png)

In this section we will redistribute the routes that are in R5's route table but are not advertised yet into OSPF process. These routes are created by means of additional loopback interfaces that are not included into OSPF process.

```dockerfile
*A:R5# show router route-table 192.168.5.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.5.1/32                                Local   Local     00h00m14s  0
       lo1                                                          0
192.168.5.2/32                                Local   Local     00h00m09s  0
       lo2                                                          0
192.168.5.3/32                                Local   Local     00h00m05s  0
       lo3                                                          0
-------------------------------------------------------------------------------
No. of Routes: 3


# ensure that loopbacks are not OSPF-enabled interfaces
*A:R5# show router ospf interface

===============================================================================
OSPFv2 (0) all interfaces
===============================================================================
If Name               Area Id         Designated Rtr  Bkup Desig Rtr  Adm  Oper
-------------------------------------------------------------------------------
system                0.0.0.1         5.5.5.5         0.0.0.0         Up   DR
toR1                  0.0.0.1         0.0.0.0         0.0.0.0         Up   PToP
-------------------------------------------------------------------------------
No. of OSPF Interfaces: 2
===============================================================================


# and R1 has no routes towards these prefixes, since they are only local to R5
A:R1# show router route-table 192.168.5.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
No. of Routes: 0
```

To redistribute these local routes into OSPF process a **policy** should be configured. Lets give our policy a `EXPORT Local Loopbacks` name:

```dockerfile
*A:R5# configure router policy-options


*A:R5>config>router>policy-options# begin

# create prefix list to match desired routes
*A:R5>config>router>policy-options# prefix-list "Loopbacks_to_export"
*A:R5>config>router>policy-options>prefix-list$ prefix 192.168.5.0/24 longer
*A:R5>config>router>policy-options>prefix-list$ back

# create policy statement to export routes
*A:R5>config>router>policy-options# policy-statement "EXPORT Local Loopbacks"
*A:R5>config>router>policy-options>policy-statement$ entry 10
# refer to the prefix list created earlier
*A:R5>config>router>policy-options>policy-statement>entry$ from prefix-list "Loopbacks_to_export"
# narrow the scope of this policy "to protocol ospf" only
*A:R5>config>router>policy-options>policy-statement>entry$ to protocol ospf

# set accept action (default action is deny all)
*A:R5>config>router>policy-options>policy-statement>entry# action accept
*A:R5>config>router>policy-options>policy-statement>entry>action# back
*A:R5>config>router>policy-options>policy-statement>entry$ back
*A:R5>config>router>policy-options>policy-statement$ back

# commit changes
*A:R5>config>router>policy-options# commit


# verify the created policy
*A:R5>config>router>policy-options# info
----------------------------------------------
            prefix-list "Loopbacks_to_export"
                prefix 192.168.5.0/24 longer
            exit
            policy-statement "EXPORT Local Loopbacks"
                entry 10
                    from
                        prefix-list "Loopbacks_to_export"
                    exit
                    to
                        protocol ospf
                    exit
                    action accept
                    exit
                exit
            exit
----------------------------------------------
```

The next step is to configure R5 router as an **ASBR** and to apply the created policy to OSPF process:

```dockerfile
# "asbr" keyword makes a router an ASBR
*A:R5# configure router ospf
*A:R5>config>router>ospf# asbr
# apply the export policy
*A:R5>config>router>ospf# export "EXPORT Local Loopbacks"
```

## Verifying redistributed routes propagation

Now, our R5 router is now configured as an ASBR and the local routes should get exported into OSPF process. These changes allow other routers in OSPF domain to receive these routes by means of _Type 4 ASBR Summary LSA_ and _Type 5 AS External LSA_:

R5:

```
*A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         1033 0x80000004 0x50ea
Router  0.0.0.1         5.5.5.5         5.5.5.5         1072 0x80000006 0x4bb4
Summary 0.0.0.1         1.1.1.1         1.1.1.1         706  0x80000004 0x1939
Summary 0.0.0.1         2.2.2.2         1.1.1.1         2226 0x80000002 0xda11
Summary 0.0.0.1         3.3.3.3         1.1.1.1         107  0x80000003 0xaa3c
Summary 0.0.0.1         4.4.4.4         1.1.1.1         929  0x80000003 0x6816
Summary 0.0.0.1         6.6.6.6         1.1.1.1         1879 0x80000002 0xe69
Summary 0.0.0.1         10.1.2.0        1.1.1.1         366  0x80000003 0x9055
Summary 0.0.0.1         10.1.3.0        1.1.1.1         472  0x80000003 0x855f
Summary 0.0.0.1         10.2.4.0        1.1.1.1         737  0x80000003 0x5a24
Summary 0.0.0.1         10.2.6.0        1.1.1.1         939  0x80000003 0x4438
Summary 0.0.0.1         10.3.4.0        1.1.1.1         442  0x80000003 0x4e2f
Summary 0.0.0.1         192.168.3.0     1.1.1.1         355  0x80000003 0x5039
AS Ext  n/a             192.168.5.1     5.5.5.5         506  0x80000001 0x63ea
AS Ext  n/a             192.168.5.2     5.5.5.5         506  0x80000001 0x59f3
AS Ext  n/a             192.168.5.3     5.5.5.5         506  0x80000001 0x4ffc
-------------------------------------------------------------------------------
No. of LSAs: 16
===============================================================================
```

R1:

```
A:R1# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.0         1.1.1.1         1.1.1.1         655  0x80000006 0x5acc
Router  0.0.0.0         2.2.2.2         2.2.2.2         988  0x80000006 0xaf65
Router  0.0.0.0         3.3.3.3         3.3.3.3         1122 0x80000009 0x1a6b
Router  0.0.0.0         4.4.4.4         4.4.4.4         1133 0x80000006 0xa54c
Summary 0.0.0.0         5.5.5.5         1.1.1.1         562  0x80000003 0x4e90
Summary 0.0.0.0         10.1.5.0        1.1.1.1         472  0x80000003 0x6f73
Summary 0.0.0.0         6.6.6.6         2.2.2.2         189  0x80000003 0x2d4
Summary 0.0.0.0         10.2.6.0        2.2.2.2         166  0x80000003 0x3aa2
AS Summ 0.0.0.0         5.5.5.5         1.1.1.1         1407 0x80000001 0x449b
Router  0.0.0.1         1.1.1.1         1.1.1.1         1368 0x80000004 0x50ea
Router  0.0.0.1         5.5.5.5         5.5.5.5         1409 0x80000006 0x4bb4
Summary 0.0.0.1         1.1.1.1         1.1.1.1         1042 0x80000004 0x1939
Summary 0.0.0.1         2.2.2.2         1.1.1.1         321  0x80000003 0xd812
Summary 0.0.0.1         3.3.3.3         1.1.1.1         443  0x80000003 0xaa3c
Summary 0.0.0.1         4.4.4.4         1.1.1.1         1265 0x80000003 0x6816
Summary 0.0.0.1         6.6.6.6         1.1.1.1         266  0x80000003 0xc6a
Summary 0.0.0.1         10.1.2.0        1.1.1.1         703  0x80000003 0x9055
Summary 0.0.0.1         10.1.3.0        1.1.1.1         809  0x80000003 0x855f
Summary 0.0.0.1         10.2.4.0        1.1.1.1         1074 0x80000003 0x5a24
Summary 0.0.0.1         10.2.6.0        1.1.1.1         1275 0x80000003 0x4438
Summary 0.0.0.1         10.3.4.0        1.1.1.1         779  0x80000003 0x4e2f
Summary 0.0.0.1         192.168.3.0     1.1.1.1         691  0x80000003 0x5039
AS Ext  n/a             192.168.5.1     5.5.5.5         843  0x80000001 0x63ea
AS Ext  n/a             192.168.5.2     5.5.5.5         843  0x80000001 0x59f3
AS Ext  n/a             192.168.5.3     5.5.5.5         843  0x80000001 0x4ffc
-------------------------------------------------------------------------------
No. of LSAs: 25
===============================================================================
```

R3:

```
A:R3# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.0         1.1.1.1         1.1.1.1         683  0x80000006 0x5acc
Router  0.0.0.0         2.2.2.2         2.2.2.2         1016 0x80000006 0xaf65
Router  0.0.0.0         3.3.3.3         3.3.3.3         1148 0x80000009 0x1a6b
Router  0.0.0.0         4.4.4.4         4.4.4.4         1159 0x80000006 0xa54c
Summary 0.0.0.0         5.5.5.5         1.1.1.1         591  0x80000003 0x4e90
Summary 0.0.0.0         10.1.5.0        1.1.1.1         499  0x80000003 0x6f73
Summary 0.0.0.0         6.6.6.6         2.2.2.2         217  0x80000003 0x2d4
Summary 0.0.0.0         10.2.6.0        2.2.2.2         193  0x80000003 0x3aa2
AS Summ 0.0.0.0         5.5.5.5         1.1.1.1         1434 0x80000001 0x449b
AS Ext  n/a             192.168.5.1     5.5.5.5         870  0x80000001 0x63ea
AS Ext  n/a             192.168.5.2     5.5.5.5         870  0x80000001 0x59f3
AS Ext  n/a             192.168.5.3     5.5.5.5         870  0x80000001 0x4ffc
-------------------------------------------------------------------------------
No. of LSAs: 12
===============================================================================
```

R6:

```
A:R6# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.2         2.2.2.2         2.2.2.2         432  0x80000004 0x76b3
Router  0.0.0.2         6.6.6.6         6.6.6.6         1309 0x80000006 0xf9f2
Summary 0.0.0.2         1.1.1.1         2.2.2.2         535  0x80000003 0xe802
Summary 0.0.0.2         2.2.2.2         2.2.2.2         1098 0x80000004 0xcc7d
Summary 0.0.0.2         3.3.3.3         2.2.2.2         524  0x80000003 0x7806
Summary 0.0.0.2         4.4.4.4         2.2.2.2         1427 0x80000003 0x5e80
Summary 0.0.0.2         5.5.5.5         2.2.2.2         471  0x80000003 0x1c5a
Summary 0.0.0.2         10.1.2.0        2.2.2.2         661  0x80000003 0x726f
Summary 0.0.0.2         10.1.3.0        2.2.2.2         85   0x80000003 0x5329
Summary 0.0.0.2         10.1.5.0        2.2.2.2         200  0x80000003 0x3d3d
Summary 0.0.0.2         10.2.4.0        2.2.2.2         58   0x80000003 0x508e
Summary 0.0.0.2         10.3.4.0        2.2.2.2         549  0x80000003 0x3049
AS Summ 0.0.0.2         5.5.5.5         2.2.2.2         1460 0x80000001 0x1265
AS Ext  n/a             192.168.5.1     5.5.5.5         899  0x80000001 0x63ea
AS Ext  n/a             192.168.5.2     5.5.5.5         899  0x80000001 0x59f3
AS Ext  n/a             192.168.5.3     5.5.5.5         899  0x80000001 0x4ffc
-------------------------------------------------------------------------------
No. of LSAs: 16
===============================================================================


A:R6# show router route-table 192.168.5.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.5.1/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
192.168.5.2/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
192.168.5.3/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
-------------------------------------------------------------------------------
No. of Routes: 3
```

# OSPF Stub Area

OSPF Stub Areas help to optimize LSDB and routing tables of the routers. We will configure **Area 2** as a stub area and this will tell ABR (R2) to not distribute any _External_ routes and send a default route into Area 2 instead. To configure Area 2 as stub you need to configure **all OSPF routers inside this area**:

![pic](http://img-fotki.yandex.ru/get/6504/21639405.11b/0_83cbb_ffa2879e_orig.png)

```dockerfile
# on R2 (ABR)
A:R2# configure router ospf
A:R2>config>router>ospf# area 2 stub


# on R6 (Area 2 router)
A:R6# configure router ospf area 2 stub
```

The following "before/after" comparison shows that **after** configuring Area 2's routers as _stub_, R6 router no longer receives _ASBR Summary LSA_ and _AS External LSA_ nor it has routes 192.168.5.1-3/32. Instead it has a new _Summary LSA_ from the ABR with the _Link State ID_ 0.0.0.0 which means **default route**.

R6 before stub area configuration:

```
A:R6# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.2         2.2.2.2         2.2.2.2         432  0x80000004 0x76b3
Router  0.0.0.2         6.6.6.6         6.6.6.6         1309 0x80000006 0xf9f2
Summary 0.0.0.2         1.1.1.1         2.2.2.2         535  0x80000003 0xe802
Summary 0.0.0.2         2.2.2.2         2.2.2.2         1098 0x80000004 0xcc7d
Summary 0.0.0.2         3.3.3.3         2.2.2.2         524  0x80000003 0x7806
Summary 0.0.0.2         4.4.4.4         2.2.2.2         1427 0x80000003 0x5e80
Summary 0.0.0.2         5.5.5.5         2.2.2.2         471  0x80000003 0x1c5a
Summary 0.0.0.2         10.1.2.0        2.2.2.2         661  0x80000003 0x726f
Summary 0.0.0.2         10.1.3.0        2.2.2.2         85   0x80000003 0x5329
Summary 0.0.0.2         10.1.5.0        2.2.2.2         200  0x80000003 0x3d3d
Summary 0.0.0.2         10.2.4.0        2.2.2.2         58   0x80000003 0x508e
Summary 0.0.0.2         10.3.4.0        2.2.2.2         549  0x80000003 0x3049
AS Summ 0.0.0.2         5.5.5.5         2.2.2.2         1460 0x80000001 0x1265
AS Ext  n/a             192.168.5.1     5.5.5.5         899  0x80000001 0x63ea
AS Ext  n/a             192.168.5.2     5.5.5.5         899  0x80000001 0x59f3
AS Ext  n/a             192.168.5.3     5.5.5.5         899  0x80000001 0x4ffc
-------------------------------------------------------------------------------
No. of LSAs: 16
===============================================================================



A:R6# show router route-table 192.168.5.0/24 longer

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
192.168.5.1/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
192.168.5.2/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
192.168.5.3/32                                Remote  OSPF      00h28m27s  150
       10.2.6.2                                                     1
-------------------------------------------------------------------------------
No. of Routes: 3
```

R6 after stub area configuration:

```
*A:R6# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.2         2.2.2.2         2.2.2.2         199  0x80000002 0xecdf
Router  0.0.0.2         6.6.6.6         6.6.6.6         0    0x80000002 0x20d2
Summary 0.0.0.2         0.0.0.0         2.2.2.2         5    0x80000004 0x5102
Summary 0.0.0.2         1.1.1.1         2.2.2.2         199  0x80000002 0x9e4
Summary 0.0.0.2         2.2.2.2         2.2.2.2         199  0x80000002 0xee5f
Summary 0.0.0.2         3.3.3.3         2.2.2.2         199  0x80000002 0x98e8
Summary 0.0.0.2         4.4.4.4         2.2.2.2         199  0x80000002 0x7e63
Summary 0.0.0.2         5.5.5.5         2.2.2.2         199  0x80000002 0x3c3d
Summary 0.0.0.2         10.1.2.0        2.2.2.2         199  0x80000002 0x9252
Summary 0.0.0.2         10.1.3.0        2.2.2.2         199  0x80000002 0x730c
Summary 0.0.0.2         10.1.5.0        2.2.2.2         199  0x80000002 0x5d20
Summary 0.0.0.2         10.2.4.0        2.2.2.2         199  0x80000002 0x7071
Summary 0.0.0.2         10.3.4.0        2.2.2.2         199  0x80000002 0x502c
-------------------------------------------------------------------------------
No. of LSAs: 13
===============================================================================


*A:R6# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
0.0.0.0/0                                     Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     101
1.1.1.1/32                                    Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     200
2.2.2.2/32                                    Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     100
3.3.3.3/32                                    Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     300
4.4.4.4/32                                    Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     200
5.5.5.5/32                                    Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     300
6.6.6.6/32                                    Local   Local     01h39m00s  0
       system                                                       0
10.1.2.0/24                                   Remote  OSPF      00h00m44s  10
       10.2.6.2                                                     200
10.1.3.0/24                                   Remote  OSPF      00h00m45s  10
       10.2.6.2                                                     300
10.1.5.0/24                                   Remote  OSPF      00h00m45s  10
       10.2.6.2                                                     300
10.2.4.0/24                                   Remote  OSPF      00h00m45s  10
       10.2.6.2                                                     200
10.2.6.0/24                                   Local   Local     01h38m38s  0
       toR2                                                         0
10.3.4.0/24                                   Remote  OSPF      00h00m45s  10
       10.2.6.2                                                     300
-------------------------------------------------------------------------------
No. of Routes: 13
```

# OSPF Totally Stub Area

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/6847/21639405.11b/0_83cbd_8d766fa0_XL.png" alt="" width="800" height="427" />](http://img-fotki.yandex.ru/get/6847/21639405.11b/0_83cbd_8d766fa0_orig.png)

ABR router participating in a _Totally stub_ area blocks not only _Type 4 ASBR Summary_ and _Type 5 AS External LSA_ but also _Type 3 Summary LSA_. This drastically reduces LSDB and route tables on Area 2 routers. As of this moment we have Area 2 configured as s_tub_area, lets configure it to be_totally stub_. To make Area 2_totally stub_ we need to configure ABR (R2) with keyword `no summaries` option:

```txt
*A:R2# configure router ospf area 2 stub no summaries</pre>

Take a look at R6's LSDB and route table

```*A:R6# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.2         2.2.2.2         2.2.2.2         482  0x80000004 0x9497
Router  0.0.0.2         6.6.6.6         6.6.6.6         518  0x80000004 0x1cd4
Summary 0.0.0.2         0.0.0.0         2.2.2.2         222  0x80000007 0x4b05
-------------------------------------------------------------------------------
No. of LSAs: 3
===============================================================================




*A:R6# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
0.0.0.0/0                                     Remote  OSPF      00h02m16s  10
       10.2.6.2                                                     101
6.6.6.6/32                                    Local   Local     02h11m29s  0
       system                                                       0
10.2.6.0/24                                   Local   Local     02h11m07s  0
       toR2                                                         0
-------------------------------------------------------------------------------
No. of Routes: 3
```

Now Area 2 router R6 has only 3 LSAs in its LSDB. All _Type 3 Summary LSA_ for networks inside Area 0 were substituted by _Summary default route_ from ABR (R2).

# Not So Stubby Area (NSSA)

![pic](http://img-fotki.yandex.ru/get/3114/21639405.11b/0_83cbf_2795355_orig.png)
  <small>There is a typo on the pic. No type4 lsa will be advertised in Area0 by R1. Only Type5</small>

Not so stubby areas are basically stub areas with an ASBR inside it. It inherits the same rule of blocking Type 4 and Type 5 LSA. But, in order to distribute external routes from ASBR another LSA this area leverages _Type 7_ LSA.

We will configure Area 1 to be NSSA by adding the following commands to R1 (ABR):

```
# prior to configuring NSSA on R5 lets check that we have active neighbor - R1

A:R5# show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR1                             1.1.1.1         Full       1    0       35
   0.0.0.1
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================

#configuring Area 1 on R5 to NSSA state

A:R5# configure router ospf area 1 nssa


# Re-check neighbor status

*A:R5# show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
No. of Neighbors: 0
===============================================================================
```

As soon we configured Area 1 on R5 to be NSSA we lost R1 as neighbor. This is the effect of a mismatched _Area_ type in OSPF _Hello_ messages between the two routers. Recall that R1 is maintaining Area 1 as a basic area, and Area 1 on R5 was reconfigured to NSSA.

We will fix neighboring by moving R1's Area 1 to NSSA operation as well:

```txt
A:R1# configure router ospf area 1 nssa


# Now check neighboring one more time

*A:R1# show router ospf neighbor "toR5"

===============================================================================
OSPFv2 (0) neighbors for interface "toR5"
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR5                             5.5.5.5         Full       1    0       33
   0.0.0.1
-------------------------------------------------------------------------------
No. of Neighbors: 1
```

Now when R1 and R5 are neighbors again lets see what has changed in their LSDBs:

R5 LSDB prior to NSSA config:

```
A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         1911 0x80000004 0x50ea
Router  0.0.0.1         5.5.5.5         5.5.5.5         1690 0x80000006 0x4bb4
Summary 0.0.0.1         1.1.1.1         1.1.1.1         2160 0x80000004 0x1939
Summary 0.0.0.1         2.2.2.2         1.1.1.1         2145 0x80000003 0xd812
Summary 0.0.0.1         3.3.3.3         1.1.1.1         1697 0x80000003 0xaa3c
Summary 0.0.0.1         4.4.4.4         1.1.1.1         669  0x80000004 0x6617
Summary 0.0.0.1         6.6.6.6         1.1.1.1         1529 0x80000003 0xc6a
Summary 0.0.0.1         10.1.2.0        1.1.1.1         997  0x80000003 0x9055
Summary 0.0.0.1         10.1.3.0        1.1.1.1         142  0x80000004 0x8360
Summary 0.0.0.1         10.2.4.0        1.1.1.1         1824 0x80000003 0x5a24
Summary 0.0.0.1         10.2.6.0        1.1.1.1         2092 0x80000003 0x4438
Summary 0.0.0.1         10.3.4.0        1.1.1.1         459  0x80000004 0x4c30
Summary 0.0.0.1         192.168.3.0     1.1.1.1         1824 0x80000003 0x5039
AS Ext  n/a             192.168.5.1     5.5.5.5         1369 0x80000003 0x5fec
AS Ext  n/a             192.168.5.2     5.5.5.5         1491 0x80000003 0x55f5
AS Ext  n/a             192.168.5.3     5.5.5.5         934  0x80000003 0x4bfe
-------------------------------------------------------------------------------
No. of LSAs: 16
===============================================================================
```

R5 LSDB after NSSA config:

```
*A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         539  0x80000002 0xa884
Router  0.0.0.1         5.5.5.5         5.5.5.5         538  0x80000004 0x6d96
Summary 0.0.0.1         1.1.1.1         1.1.1.1         538  0x80000002 0x3b1b
Summary 0.0.0.1         2.2.2.2         1.1.1.1         538  0x80000002 0xf8f4
Summary 0.0.0.1         3.3.3.3         1.1.1.1         538  0x80000002 0xca1f
Summary 0.0.0.1         4.4.4.4         1.1.1.1         538  0x80000002 0x88f8
Summary 0.0.0.1         6.6.6.6         1.1.1.1         538  0x80000002 0x2c4d
Summary 0.0.0.1         10.1.2.0        1.1.1.1         538  0x80000002 0xb038
Summary 0.0.0.1         10.1.3.0        1.1.1.1         538  0x80000002 0xa542
Summary 0.0.0.1         10.2.4.0        1.1.1.1         538  0x80000002 0x7a07
Summary 0.0.0.1         10.2.6.0        1.1.1.1         538  0x80000002 0x641b
Summary 0.0.0.1         10.3.4.0        1.1.1.1         538  0x80000002 0x6e12
Summary 0.0.0.1         192.168.3.0     1.1.1.1         538  0x80000002 0x701c
NSSA    0.0.0.1         192.168.5.1     5.5.5.5         577  0x80000001 0xe74a
NSSA    0.0.0.1         192.168.5.2     5.5.5.5         577  0x80000001 0xdd53
NSSA    0.0.0.1         192.168.5.3     5.5.5.5         577  0x80000001 0xd35c
-------------------------------------------------------------------------------
No. of LSAs: 16
===============================================================================
```

As we see, all _Type 5 AS External LSA_ were substituted by _Type 7 NSSA LSA_. And if we had any other external routes we wouldn't see them in R5 database, since NSSA areas can not contain External routes.

# Totally NSSA

![pic](http://img-fotki.yandex.ru/get/6300/21639405.11b/0_83cc0_5d4047c9_orig.png)
<small>There is a typo on the pic. No type4 lsa will be advertised in Area0 by R1. Only Type5</small>

As with totally stubby areas, NSSA could be configured in a way that no _Type 3 Summary LSA_ will present in such area. Totally NSSA configuration adds two additional commands on ABR:

On R1:

```txt
*A:R1>config>router>ospf>area# info
----------------------------------------------
                nssa
                exit
                interface "toR5"
                    interface-type point-to-point
                    no shutdown
                exit
----------------------------------------------

# Configuring NSSA to be totally NSSA
*A:R1>config>router>ospf>area# nssa no summaries</pre>
```

On R5:

```txt
# As a result - no Type 3 Summary LSA are present in R5's database

*A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         1305 0x80000003 0xa685
Router  0.0.0.1         5.5.5.5         5.5.5.5         1550 0x80000005 0x6b97
NSSA    0.0.0.1         192.168.5.1     5.5.5.5         1654 0x80000002 0xe54b
NSSA    0.0.0.1         192.168.5.2     5.5.5.5         852  0x80000002 0xdb54
NSSA    0.0.0.1         192.168.5.3     5.5.5.5         816  0x80000002 0xd15d
-------------------------------------------------------------------------------
No. of LSAs: 5
===============================================================================
```

ABR configured with _Totally NSSA_ area filters Type 3 LSA as totally stubby area does. But notice one major difference - there is **no default route** injected by ABR. This is the cause of ping failure to any _Area 0_ address:

```
*A:R5# ping 4.4.4.4
PING 4.4.4.4 56 data bytes
No route to destination. Address: 4.4.4.4, Router: Base
```

To resolve this issue you should add another command to NSSA context:

```
*A:R1>config>router>ospf>area# nssa originate-default-route
```

This will cause R1 to inject Type 3 Summary LSA in Area 1:

```
*A:R5# show router ospf database

===============================================================================
OSPFv2 (0) Link State Database (Type : All)
===============================================================================
Type    Area Id         Link State Id   Adv Rtr Id      Age  Sequence   Cksum
-------------------------------------------------------------------------------
Router  0.0.0.1         1.1.1.1         1.1.1.1         1652 0x80000003 0xa685
Router  0.0.0.1         5.5.5.5         5.5.5.5         264  0x80000006 0x6998
Summary 0.0.0.1         0.0.0.0         1.1.1.1         53   0x80000001 0x75e4
NSSA    0.0.0.1         192.168.5.1     5.5.5.5         172  0x80000003 0xe34c
NSSA    0.0.0.1         192.168.5.2     5.5.5.5         1199 0x80000002 0xdb54
NSSA    0.0.0.1         192.168.5.3     5.5.5.5         1163 0x80000002 0xd15d
-------------------------------------------------------------------------------
No. of LSAs: 6
===============================================================================


*A:R5# ping 4.4.4.4
PING 4.4.4.4 56 data bytes
64 bytes from 4.4.4.4: icmp_seq=1 ttl=62 time=19.6ms.
```

# Debugging OSPF adjacency issues

For two OSPF routers to become neighbors several parameters should be matched. And most of them - are the parameters communicated via OSPF Hello messages. If you do not see a neighbor on the other side there is a good chance that one of these parameters mismatches.

When you need to investigate the reason casing a neighboring relationships to break leverage the debug commands available.

Consider the following example where R1 lost its neighbor R5 in Area 1:

```
*A:R1# show router ospf neighbor "toR5"

===============================================================================
OSPFv2 (0) neighbors for interface "toR5"
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
No. of Neighbors: 0
===============================================================================
```

To see what is going wrong, lets create a logging instance and capture _Hello_ packets to analyze their content:

```txt
# Creating log #55
*A:R1# configure log log-id 55

# Configuring capture log messages from debug to memory 
*A:R1>config>log>log-id$ from debug-trace
*A:R1>config>log>log-id$ to memory


# Specifying what "debug" should process. We are hunting OSPF Hello packets
# adding "detail" to see more verbose output

*A:R1# debug router ospf packet hello detail
```

Now that we have **log** and **debug** objects configured, we could drill down to the contents of Hello messages:

```txt
*A:R1# show log log-id 55

===============================================================================
Event Log 55
===============================================================================
Description : (Not Specified)
Memory Log contents  [size=100   next event=22  (not wrapped)]

20 2015/01/01 03:11:31.28 UTC MINOR: DEBUG #2001 Base OSPFv2
"OSPFv2: PKT DROPPED
hello interval mismatch"

19 2015/01/01 03:11:31.28 UTC MINOR: DEBUG #2001 Base OSPFv2
"OSPFv2: PKT

>> Incoming OSPF packet on I/F toR5 area 0.0.0.1
OSPF Version      : 2
Router Id         : 5.5.5.5
Area Id           : 0.0.0.1
Checksum          : ec98
Auth Type         : Null
Auth Key          : 00 00 00 00 00 00 00 00
Packet Type       : HELLO
Packet Length     : 44

Network Mask      : 255.255.255.0
Hello Interval    : 5
Options           : 08 -----N----
Rtr Priority      : 1
Dead Interval     : 40
Designated Router : 0.0.0.0
Backup Router     : 0.0.0.0
```

Now the problem is clear - incoming OSPF packet came in with Hello timer set to 5sec. And R1 tells us that this value mismatches its configured _Hello timer_ value.

This debug technique should indicate every discrepancy in OSPF values that should match, be it authentication mismatch or Area ID mismatch.

And that is all for the moment.
