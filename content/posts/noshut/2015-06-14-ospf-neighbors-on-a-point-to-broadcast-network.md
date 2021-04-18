---
title: OSPF. Neighbors on a "point-to-broadcast" network
date: 2015-06-14T11:02:45+00:00
url: /2015/06/ospf-neighbors-on-a-point-to-broadcast-network/
toc: true
draft: false
comment_id: ospf-p2b
tags:
  - OSPF
---

When it comes to basic OSPF troubleshooting the first-aid kit is _Neighbor states_ and _things, that should match to form an adjacency_. And on one early morning while refreshing my memory on OSPF neighbor states I accidentally ran into quite interesting problem.

But before we start, answer the short question:

<p style="padding-left: 30px;">
  Will adjacency be formed between directly connected via Gig. Ethernet interfaces routers R1 and R2 if
</p>

<li style="padding-left: 30px;">
  R1&#8217;s OSPF interface type configured as point-to-point
</li>
<li style="padding-left: 30px;">
  R2&#8217;s OSPF interface type configured as broadcast
</li>

<p style="padding-left: 30px;">
   Time&#8217;s up. The answer is &#8211; yes and no. Wanna know why? Jump in, I have to show you something.
</p>

<!--more-->

Take a look at this topology which consists of two directly connected Cisco routers.

<img class="aligncenter" src="http://img-fotki.yandex.ru/get/6827/21639405.11b/0_836e1_87245d32_L.png" alt="" width="500" height="396" /> 

At first, topology seems as simple as a first figure in a CCNA book. But take a closer look at this OSPF interfaces, their types are different. Hm, definitely not a case you would find covered in an everyday OSPF configuration guide.

I will not go into details about what are all the differences between various OSPF interface types, you already know it, or can read about 1-click away. Though I should remind you the key difference between **point-to-point** and **broadcast** interfaces behavior which is the necessity to elect DR/BDR routers for the latter.

Also it is worth mention that it is best-practice nowadays to set &#8220;broadcast-by-nature&#8221; Ethernet interfaces to operate in a point-to-point fashion. Why would one do it? To reduce convergence time. Ethernet interface once configured as point-to-point won&#8217;t go into DR/BDR election which effectively means that neighbor relationships will reach FULL state 40 seconds faster (40s is the default _wait_ interval for interface to elect DR/BDR routers_)_.

Therefore this particular case with different interface types isn&#8217;t some artificial Lab exercise, you can easily meet this interface mix in the real world. Let&#8217;s say you simply forgot to configure another interface with p2p type, or your neighbor is under administration of the 3rd party who knows nothing about best practices and leave you with default broadcast behavior.

Ok, different link types mean different networks with different behavior, rules and so forth, there is every indication that adjacency should not form. But it is not that simple. Let&#8217;s Lab!

# Lab time

I booted up two Cisco routers running IOS 15.2(4)S simultaneously and first thing checked R1&#8217;s OSPF neighbors, expecting to see zero active neighbors:

```
R1#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           0   FULL/  -        00:00:36    10.1.2.2        GigabitEthernet1/0
```

Look at this, R1 has a neighbor in FULL state, which means that it has recognized R2 as a valid neighbor and successfully accomplished exchange of _Link State Updates_! As a precaution lets check OSPF interfaces parameters on both routers to confirm that they indeed operate in different types:

On R1:
```txt
R1# show ip ospf interface gi1/0
GigabitEthernet1/0 is up, line protocol is up
  Internet Address 10.1.2.1/24, Area 0, Attached via Interface Enable
  Process ID 1, Router ID 1.1.1.1, Network Type POINT_TO_POINT, Cost: 1
  Topology-MTID    Cost    Disabled    Shutdown      Topology Name
        0           1         no          no            Base
  Enabled by interface config, including secondary ip addresses
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    oob-resync timeout 40
    Hello due in 00:00:00
  Supports Link-local Signaling (LLS)
  Cisco NSF helper support enabled
  IETF NSF helper support enabled
  Index 1/1, flood queue length 0
  Next 0x0(0)/0x0(0)
  Last flood scan length is 1, maximum is 1
  Last flood scan time is 0 msec, maximum is 0 msec
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 2.2.2.2
  Suppress hello for 0 neighbor(s)
```

On R2:
```txt
R2#show ip ospf interface gi1/0
GigabitEthernet1/0 is up, line protocol is up
  Internet Address 10.1.2.2/24, Area 0, Attached via Interface Enable
  Process ID 1, Router ID 2.2.2.2, Network Type BROADCAST, Cost: 1
  Topology-MTID    Cost    Disabled    Shutdown      Topology Name
        0           1         no          no            Base
  Enabled by interface config, including secondary ip addresses
  Transmit Delay is 1 sec, State DR, Priority 1
  Designated Router (ID) 2.2.2.2, Interface address 10.1.2.2
  Backup Designated router (ID) 1.1.1.1, Interface address 10.1.2.1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    oob-resync timeout 40
    Hello due in 00:00:09
  Supports Link-local Signaling (LLS)
  Cisco NSF helper support enabled
  IETF NSF helper support enabled
  Index 1/1, flood queue length 0
  Next 0x0(0)/0x0(0)
  Last flood scan length is 2, maximum is 2
  Last flood scan time is 0 msec, maximum is 4 msec
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 1.1.1.1  (Backup Designated Router)
  Suppress hello for 0 neighbor(s)
```

Yes, interfaces operate in different types as seen in highlighted strings above. And R2&#8217;s output also says us that R2 elected DR (itself) and BDR (R1).  But what about R2, does it have a neighbor?

```
R2#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1           1   FULL/BDR         00:00:33    10.1.2.1        GigabitEthernet1/0
```

Apparently, yes, its neighbor is R1 with RID 1.1.1.1 and the state of this adjacency is also FULL. Well, does it mean that despite routers R1 and R2 have different OSPF interface types configured adjacency will be successfully formed and OSPF routes will populate the routing table? To ensure this conclusion lets check routers OSPF databases:

R1 OSPF DB:

```
R1# show ip ospf database

            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum Link count
1.1.1.1         1.1.1.1         514         0x80000002 0x00FFF6 3
2.2.2.2         2.2.2.2         515         0x80000002 0x00A545 3

                Net Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum
10.1.2.2        2.2.2.2         515         0x80000001 0x0021F5
```

R2 OSPF DB:
```
R2# show ip ospf database

            OSPF Router with ID (2.2.2.2) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum Link count
1.1.1.1         1.1.1.1         1160        0x80000002 0x00FFF6 3
2.2.2.2         2.2.2.2         1159        0x80000002 0x00A545 2

                Net Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum
10.1.2.2        2.2.2.2         1159        0x80000001 0x0021F5
```

Both routers (as they must) have identical databases: 2 _Router LSA_ (one from each router) and one _Network LSA_ produced by Designated Router R2. Healthy-looking OSPF database. Now lets see if we have OSPF routes in each router&#8217;s routing table to wrap this case up:

R1's route table:
```
R1#show ip route ospf
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       + - replicated route, % - next hop override

Gateway of last resort is not set
```

R2's route table:
```
R2#show ip route ospf
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       + - replicated route, % - next hop override

Gateway of last resort is not set</pre>
```

Oops, no OSPF routes in routing tables for both routers, how this even possible if we have just seen OSPF databases? Lets examine them one more time, now with detailed look to neighbor&#8217;s _Router LSA_:

On R1:
```txt
R1#show ip ospf database router 2.2.2.2

            OSPF Router with ID (1.1.1.1) (Process ID 1)

		Router Link States (Area 0)

  Adv Router is not-reachable in topology Base with MTID 0
  LS age: 827
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 2.2.2.2
  Advertising Router: 2.2.2.2
  LS Seq Number: 80000002
  Checksum: 0xA545
  Length: 48
  Number of Links: 2

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 2.2.2.2
     (Link Data) Network Mask: 255.255.255.255
      Number of MTID metrics: 0
       TOS 0 Metrics: 1

    Link connected to: a Transit Network
     (Link ID) Designated Router address: 10.1.2.2
     (Link Data) Router Interface address: 10.1.2.2
      Number of MTID metrics: 0
       TOS 0 Metrics: 1
```

On R2:
```txt
R2#show ip ospf database router 1.1.1.1

            OSPF Router with ID (2.2.2.2) (Process ID 1)

		Router Link States (Area 0)

  Adv Router is not-reachable in topology Base with MTID 0
  LS age: 995
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 1.1.1.1
  Advertising Router: 1.1.1.1
  LS Seq Number: 80000005
  Checksum: 0x6777
  Length: 60
  Number of Links: 3

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 1.1.1.1
     (Link Data) Network Mask: 255.255.255.255
      Number of MTID metrics: 0
       TOS 0 Metrics: 1

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 2.2.2.2
     (Link Data) Router Interface address: 10.1.2.1
      Number of MTID metrics: 0
       TOS 0 Metrics: 1

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 10.1.2.0
     (Link Data) Network Mask: 255.255.255.0
      Number of MTID metrics: 0
       TOS 0 Metrics: 1
```

# Busted

Gotcha, look at line #7, both routers tell us that they cant reach advertising router based on their calculated topology! And if we recall that every OSPF router builds its own network diagram based on LSA&#8217;s it received we should understand what happened behind the scenes.

R1 thinks that R2 is its directly connected on point-to-point network to R2, but R2 thinks the other way, that it is connected to a broadcast network. Given that, when Dijkstra algorithm comes in play to build a network topology it literally got lost, because **topology data does not match. **And this is the very reason behind the absence of OSPF routes in R1&R2 tables, SPF algorithm have not produced anything meaningful.

Now let me zip this all to a single sentence:

> Cisco routers successfully form neighbor relationships even if OSPF interfaces configured with different types, however no OSPF routes will be installed into routing tables since OSPF database information is inconsistent.

This was a totally strange behavior for me to see, yet Cisco didn't brake any rules. [RFC 2328 OSPFv2](https://tools.ietf.org/html/rfc2328) does not explicitly restrict to form adjacency for different network types, I think that authors thought it would be obvious not to mix different types on a single network segment. Moreover, OSPF _Hello_ message does not contain any field for interface type, so routers do not know what interface type is on the other side.

# And what about Alcatel-Lucent and Juniper?

But there are other vendors who managed to distinguish between different network interfaces to prevent such a bad situation when adjacency seems to be formed yet no routes are present. And we start with Alcatel-Lucent&#8217;s SR-OS v12.0.R8 (If you are new to ALU routers, check this [OSPF configuration tutorial](http://noshut.ru/2015/06/alcatel-lucent-ospf-configuration-tutorial/)).

<img class="aligncenter" src="http://img-fotki.yandex.ru/get/4314/21639405.11b/0_8372f_119bb606_L.png" alt="" width="500" height="291" /> 

Network topology and routers configuration area the same. Booting up routers simultaneously and checking adjacency right after that several times:

On R1:
```
*A:R1>config>router>ospf# /show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR2                             2.2.2.2         ExchStart  1    0       36
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================


*A:R1>config>router>ospf# /show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR2                             2.2.2.2         ExchStart  1    0       33
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================



*A:R1>config>router>ospf# /show router ospf neighbor

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

On R2:
```
*A:R2>config>router>ospf# /show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR1                             1.1.1.1         Two Way    1    0       30
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================


*A:R2>config>router>ospf# /show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR1                             1.1.1.1         Two Way    1    0       38
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================


*A:R2>config>router>ospf# /show router ospf neighbor

===============================================================================
OSPFv2 (0) all neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
toR1                             1.1.1.1         Init       1    0       39
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================
```

Look at this, R1 goes into Exchange Start phase very quickly, this is because its interface is operating in p-t-p mode and do not need to elect DR/BDR. Therefore right after R1 sees itself in received Hello message from R2 it immediately starts to send to R2 its _Database Description_ messages.

But R2 cant answer to R1, it needs to elect DR/BDR first, since it is thinking that it is on a broadcast network segment. At the same time R2 sees itself in coming _Hello_ messages &#8211; that is why R2 is in 2Way state for a period of time.

And then we see that R1 drops off its neighbor R1 (line #41), effectively putting adjacency to DOWN state. Why would R1 do this? Because it noticed that R2 operates in a different mode and there is no point to peer with it.

# How point-to-point interface detects broadcast interface?

But how did R1 figured out that R2&#8217;s interface is broadcast if _Hello_ messages do not communicate that information?  Well, it took some intellectual analysis from R1. And to get down to the truth we have to dig into debug output of R1:

```txt
18 2015/01/01 00:27:39.85 UTC MINOR: DEBUG #2001 Base OSPFv2
"OSPFv2: PKT
 
>> Incoming OSPF packet on I/F toR2 area 0.0.0.0
OSPF Version      : 2
Router Id         : 2.2.2.2
Area Id           : 0.0.0.0
Checksum          : f694
Auth Type         : Null
Auth Key          : 00 00 00 00 00 00 00 00
Packet Type       : HELLO
Packet Length     : 48
 
Network Mask      : 255.255.255.0
Hello Interval    : 10
Options           : 02 -------E--
Rtr Priority      : 1
Dead Interval     : 40
Designated Router : 0.0.0.0
Backup Router     : 0.0.0.0
Neighbor-1        : 1.1.1.1
"
 
20 2015/01/01 00:27:44.85 UTC MINOR: DEBUG #2001 Base OSPFv2
"OSPFv2: PKT
 
>> Incoming OSPF packet on I/F toR2 area 0.0.0.0
OSPF Version      : 2
Router Id         : 2.2.2.2
Area Id           : 0.0.0.0
Checksum          : de8f
Auth Type         : Null
Auth Key          : 00 00 00 00 00 00 00 00
Packet Type       : HELLO
Packet Length     : 48
 
Network Mask      : 255.255.255.0
Hello Interval    : 10
Options           : 02 -------E--
Rtr Priority      : 1
Dead Interval     : 40
Designated Router : 10.1.2.2
Backup Router     : 10.1.2.1
Neighbor-1        : 1.1.1.1
"
 
22 2015/01/01 00:27:44.85 UTC MINOR: DEBUG #2001 Base OSPFv2
"OSPFv2: PKT DROPPED
interface type mismatch"
```

Debug shows incoming OSPF packets, I left only two of them which show the difference. Look, the second _OSPF Hello_ message has DR and BDR IP addresses filled in, and that is why **this packet got dropped**. R1 knows that it is operating on a point-to-point network, thus it should not receive any Hello messages with DR and BDR IP addresses other then 0.0.0.0. That is why R1 drops this packets and control plane never sees them. And if Hello packets are not coming for _Dead interval_, R1 thinks that neighbor is down and breaks the neighboring process.

This underlying logic effectively stops useless adjacency to form and keeps network administrators from unnecessary troubleshooting.

# JUNOS

<img class="aligncenter" src="http://img-fotki.yandex.ru/get/9743/21639405.11b/0_8372e_157fef29_L.png" alt="" width="500" height="281" />

Juniper routers (I am running Junos 14.1 on vMX) acts in the same as ALU manner. They reject &#8220;foreign&#8221; _Hello_ packets on point-to-point interface if they contain DR/BDR addresses.

```
Jun 11 10:14:57.781975 Received OSPF packet of type and wire_length 1, 60
Jun 11 10:14:57.782018 OSPF rcvd Hello 10.1.2.2 -> 224.0.0.5 (ge-0/0/0.0 IFL 329 area 0.0.0.0)
Jun 11 10:14:57.782026   Version 2, length 48, ID 2.2.2.2, area 0.0.0.0
Jun 11 10:14:57.782032   checksum 0x0, authtype 0
Jun 11 10:14:57.782039   mask 255.255.255.0, hello_ivl 10, opts 0x12, prio 128
Jun 11 10:14:57.782045   dead_ivl 40, DR 10.1.2.2, BDR 0.0.0.0
Jun 11 10:14:57.782065 OSPF restart signaling: Received hello with LLS data from nbr ip=10.1.2.2 id=2.2.2.2.
Jun 11 10:14:57.782075 OSPF packet ignored: configuration mismatch from 10.1.2.2 on intf ge-0/0/0.0 area 0.0.0.0
```

# Summary

  * Nowadays it is best-practice to configure Ethernet interfaces between directly connected OSPF routers in a point-to-point type to reduce convergence time.
  * It is possible to configure different interface&#8217;s type on a single network segment between OSPF routers. Especially interesting the case when one interface configured with point-to-point type and the other with broadcast.
  * Cisco routers form neighbor relationships even if OSPF interfaces configured with different types, however no OSPF routes will be installed into routing tables since OSPF database information is inconsistent.
  * This Cisco&#8217;s behavior can lead to unnecessary troubleshooting since adjacency seems up yet no OSPF routes will be seen in routing table.
  * Alcatel-Lucent and Juniper routers effectively prevent adjacency to form in such case. They drop incoming to point-to-point interface Hello packets if they contain DR/BDR IP addresses other then zero.

# Links

  * [OSPF Version 2](http://tools.ietf.org/html/rfc2328) (RFC)
  * [What is your OSPF neighbor doing? Adjacency problems in OSPF](https://inetzero.com/what-is-your-ospf-neighbor-doing-adjancency-problems-in-ospf/) (https://inetzero.com)

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>