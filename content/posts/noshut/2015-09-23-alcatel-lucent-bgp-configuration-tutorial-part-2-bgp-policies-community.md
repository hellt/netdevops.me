---
title: Nokia (Alcatel-Lucent) BGP configuration tutorial. Part 2 - Communities
date: 2015-09-23T16:41:58+00:00
author: Roman Dodin
comment_id: bgp-communities
url: /2015/09/alcatel-lucent-bgp-configuration-tutorial-part-2-bgp-policies-community/
tags:
  - Nokia
  - SROS
  - BGP
---

In the [first part of this BGP tutorial](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/) we prepared the ground by configuring eBGP/iBGP peering. We did a good job overall, yet the _plain_ BGP peering is not something you would not normally see in production. The power of BGP is in its ability for granular management of multiple routes from multiple sources. And the tools that help BGP to handle this complex task are BGP policies at their full glory.

In this part we will discuss and practice:

  * BGP export/import policies for route advertisement/filtering
  * BGP communities operations
  * BGP routes aggregation: route summarization and the corresponding `aggregate` and `atomic-aggregate` path attributes

<!--more-->

# What are BGP policies for?

The BGP peering configuration process is simple, you saw it in [Part 1](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/), but, frankly, no network engineer leaves a BGP router in a default "receive all, advertise all" state. We use BGP policies to tell the router which routes to accept and which to advertise.

This is just an example on where the BGP policies play a part, but they are used for many other tasks as well.

In BGP you can define two types of policies: Import and Export. To demonstrate where and when does a particular policy take place I paste here the BGP route processing diagram:

![pic](http://img-fotki.yandex.ru/get/4109/21639405.11c/0_84d72_94e5a74a_orig.png)

**Export polices** are used for:

  * export routes from different protocols to BGP (like IGP routes being exported to BGP in [Part 1](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/))
  * granular control of the advertised routes
      * prohibit unwanted prefixes advertising
      * set the path attributes to a desired NLRI
  * reducing control plane traffic by advertising aggregate routes

**Import policies** are used for:

  * filtering unwanted NLRI 
      * by prefix, prefix-length, community value
  * manipulation with the outbound traffic
      * applying `Local-Pref` attribute to desired prefixes
      * modifying/setting `MED` value or any other transitive attribute

In SROS BGP policy configuration takes place in a router's policy-options context - `configure router policy-options`.

To practice with BGP policies configuration we will go through a set of tasks that an ISP engineer can be expected to do in theirs day-to-day operations. We will simulate a simple ISP scenario using the following network topology:

![pic](http://img-fotki.yandex.ru/get/9263/21639405.11c/0_85519_aeed2105_orig.png)

Network interfaces, IGP and basic BGP configuration are done exactly the same as in the [Part 1 of this series](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp). If you are interested in the final configuration output, please refer to the [Wrapping up section](http://netdevops.me/2015/08/alcatel-lucent-bgp-configuration-tutorial-part-1-basic-ebgp-ibgp/#Wrapping_up).

# Community attribute

Lets statr with _BGP communities_ introduction. A BGP community (not [extended](https://tools.ietf.org/html/rfc4360)) is an **optional transitive BGP Path attribute** that is _a group of destinations which share some common property_ as per the [RFC 1997](https://tools.ietf.org/html/rfc1997).

I like to think of a community as _a label (or a tag)_ which BGP speaker puts on a NLRI to give it a context. These labels could serve different purposes, for example:

* to mark/identify the prefixes originated from a specific geographic region, customer or service,
* or to indicate that a specific treatment is desired like for the prefixes with the use of `no-export` or `no-advertise` community values
* or could mean any other property which BGP speaker wants to communicate within an NLRI.

BGP Communities are just the means to augment the specific prefixes with the metadata, they are useless until you bind some actions to them.  
For example, you tag some prefixes with a `community A` value and others with a `community B`; then you could tell your BGP peers to, say, set the `Local Preference 200` attribute for the prefixes that have `community A` value and leave Local Preference intact for the ones marked with `community B` value. In this examples communities allowed us to set a specific action based on the community value associated with the prefixes.

Communities are represented by a **community string** which is a 32 bit value. **First two bytes** of a community attribute **have to** be encoded with an AS number where community was born, and the other two bytes are set by an AS network engineer as he pleases (or in other words, the community string follows this template `<2byte-asnumber:community-value>`).


> The community attribute values range from `0x0000000 (0:0)` through `0x0000FFFF (0:65535)`.  
> The range from `0xFFFF0000 (65535:0)` through `0xFFFFFFFF (65535:65535)` is reserved.


Lets run our lab and refer to the following diagram before we start configuring community attributes:

![pic](http://img-fotki.yandex.ru/get/6442/21639405.11c/0_8551a_fa9ce1ee_orig.png)

We will introduce three different communities for our customer routes:

  * `65510:100` - community for every route originated from the West side of AS 65510
  * `65510:200` - community for every route originated from the East side of our AS 65510
  * `65510:2` - community for the `Customer_2` routes

## Adding community

Community strings are configured under the `policy-options` context. Before we will be able to add communities to the prefixes, we need to: 

1. Specify the `prefix-lists` for our the routes we would like to mark with a community
2. Declare the community strings we want to refer later to.

R5 policy config:
```txt
*A:R5>config>router>policy-options# info
----------------------------------------------
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
----------------------------------------------
```

The same `policy-options` configuration block is applied to R6.

To tag the routes with a community value we have to additionally configure a `policy-statement` which will associate a community string with the selected prefixes. This policy will be later referenced in the BGP configuration as the **export policy**.

Consider the following `policy-statement "Adv_Customers_nets"` that is configured on R5:

```txt
*A:R5>config>router>policy-options# info
----------------------------------------------
<prefix-lists and community strings are omitted>

            policy-statement "Adv_Customers_nets"
## =======================================================================
                entry 10 
                    from
                        protocol direct ## matches every connected network
                    exit
                    action next-entry 
## next-entry means that upon successful completion of this action 
## we DON'T stop the policy evaluation process and proceed to the next entry
                        community add "West" ## adding community to every direct connected route
                                             ## matched by the "from" statement
                    exit
                exit
## =======================================================================
                entry 20
                    from
                        prefix-list "Customer_2" ## matches Customer_2 routes
                    exit
                    action accept
## action "accept" stops policy evaluation effective immediately
## and its okay in this situation, since we have only two customers
## so if we matched "Customer_2" and marked it with its community, 
## then we have nothing to do else and can stop policy evaluation
                        community add "Customer_2"
                    exit
                exit
## =======================================================================
                entry 30
                    from
                        prefix-list "Customer_1"
                    exit
                    action accept
## we do not need to add communities for the Customer_1 routes, but we need to create
## an "action accept" for its prefixes, since the default action is deny-all
                    exit
                exit
            exit
----------------------------------------------
```
The same policy statement configuration should be created on R6 router.

In the example above we added the community string using the `community add` operation; SROS also has additional operations provided for the community strings:

```
- community add <name> [<name>...(upto 28 max)]
- community remove <name> [<name>...(upto 28 max)]
- community replace <name> [<name>...(upto 28 max)]
- no community
```

As was explained before, the policy statement should then be applied as an `export` policy in the respective BGP configuration on both R5 and R6:

```
*A:R5# configure router bgp group "iBGP"
*A:R5>config>router>bgp>group# export "Adv_Customers_nets"

*A:R6# configure router bgp group "iBGP"
*A:R6>config>router>bgp>group# export "Adv_Customers_nets"
```

Now take a look at the `show router bgp summary` command on R5. There are 2 routes advertised to every iBGP neighbor and 2 rotes received from its fellow - R6:

```txt
===============================================================================
BGP Summary
===============================================================================
Neighbor
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.10.10.1
                65510     593    0 04h55m11s 0/0/2 (IPv4)
                          595    0
10.10.10.2
                65510     593    0 04h55m09s 0/0/2 (IPv4)
                          595    0
10.10.10.6
                65510     592    0 04h53m51s 2/2/2 (IPv4)
                          592    0
-------------------------------------------------------------------------------
```
The BGP summary output does not disclose if any community attributes were applied to the NLRIs a BGP speaker sent or received, to verify that we should ask for a specific prefix details.

## Show communities

To ensure that the correct communities were passed along with the NLRI we can leverage the `show router bgp routes <prefix> detail` command and check the `Community` column in its output:

```txt
A:R1# show router bgp routes 172.10.55.0/24 detail
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
Original Attributes

Network        : 172.10.55.0/24
Nexthop        : 10.10.10.5
Path Id        : None
From           : 10.10.10.5
Res. Nexthop   : 10.10.99.5
Local Pref.    : 100                    Interface Name : toR5
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : 65510:2 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.5
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP
Route Source   : Internal
AS-Path        : No As-Path
Route Tag      : 0
Neighbor-AS    : N/A
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0





A:R1# show router bgp routes 10.10.55.0/24 detail
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
Original Attributes

Network        : 10.10.55.0/24
Nexthop        : 10.10.10.5
Path Id        : None
From           : 10.10.10.5
Res. Nexthop   : 10.10.99.5
Local Pref.    : 100                    Interface Name : toR5
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.5
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP
Route Source   : Internal
AS-Path        : No As-Path
Route Tag      : 0
Neighbor-AS    : N/A
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0
```

Everything works as expected. `Customer_1` routes are tagged with just the "West" community, and the `Customer_2` routes are being tagged with both "West" and "Customer_2" communities. Lets go a bit deeper and see how the community strings are carried in the BGP Updates messages:

![pic](http://img-fotki.yandex.ru/get/4214/21639405.11c/0_8551b_9f4430f3_orig.png)

Community path attribute propagates across eBGP links as well. To check this we can filter the routes with a specfic community that R3 has in its BGP routes tables. Note, that R3 resides in the AS 65520 and thus is a eBGP peer:

```txt
## show BGP routes labelled with a specific community string

A:R3# show router bgp routes community 65510:2
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
u*>i  172.10.55.0/24                                     None        None
      10.0.99.0                                          None        -
      65510
*i    172.10.55.0/24                                     100         None
      10.20.20.4                                         None        -
      65510
u*>i  172.10.66.0/24                                     None        None
      10.0.99.0                                          None        -
      65510
*i    172.10.66.0/24                                     100         None
      10.20.20.4                                         None        -
      65510
-------------------------------------------------------------------------------
Routes : 4
===============================================================================
```

And of course you can use `show router bgp routes <prefix> hunt` to see the verbose output of a given BGP route.

## Operation replace & Well-known communities

[RFC 1997](https://tools.ietf.org/html/rfc1997) specifies the following well-known communities as the well-known communities:

* `NO_EXPORT (0xFFFFFF01)` All routes received carrying a communities attribute containing this value MUST NOT be advertised outside a BGP confederation boundary (a stand-alone autonomous system that is not part of a confederation should be considered a confederation itself).
* `NO_ADVERTISE (0xFFFFFF02)` All routes received carrying a communities attribute containing this value MUST NOT be advertised to other BGP peers.
* `NO_EXPORT_SUBCONFED (0xFFFFFF03)` All routes received carrying a communities attribute containing this value MUST NOT be advertised to external BGP peers (this includes peers in other members autonomous systems inside a BGP confederation).

You will encounter `no-export` and `no-advertise` communities quite often, as they are naturally used for route advertisement manipulations.

To demonstrate the power of the default communities I would like to introduce you to another AS 65530 which has the single-homed peering with AS 65520:

![pic](http://img-fotki.yandex.ru/get/4214/21639405.11c/0_8551c_4c86f63e_orig.png)

Router R7 residing in AS 65530 has the default BGP configuration:

```txt
A:R7>config>router>bgp# info 
----------------------------------------------
            group "no_export_example"
                peer-as 65520
                split-horizon
                neighbor 10.0.99.4
                    local-address 10.0.99.5
                exit
            exit
            no shutdown
----------------------------------------------
```

As a result of this configuration it receives **all** BGP routes that R3 has in its BGP Rib-Out database:

R3 BGP routes:
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
u*>i  10.10.55.0/24                                      None        None
      10.0.99.0                                          None        -
      65510                                                           
*i    10.10.55.0/24                                      100         None
      10.20.20.4                                         None        -
      65510                                                           
u*>i  10.10.66.0/24                                      None        None
      10.0.99.0                                          None        -
      65510                                                           
*i    10.10.66.0/24                                      100         None
      10.20.20.4                                         None        -
      65510                                                           
u*>i  172.10.55.0/24                                     None        None
      10.0.99.0                                          None        -
      65510                                                           
*i    172.10.55.0/24                                     100         None
      10.20.20.4                                         None        -
      65510                                                           
u*>i  172.10.66.0/24                                     None        None
      10.0.99.0                                          None        -
      65510                                                           
*i    172.10.66.0/24                                     100         None
      10.20.20.4                                         None        -
      65510                                                           
-------------------------------------------------------------------------------
Routes : 8
===============================================================================
```

R7 BGP routes:
```txt
A:R7# show router bgp routes 
===============================================================================
 BGP Router ID:10.30.30.7       AS:65530       Local AS:65530      
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
u*>i  10.10.55.0/24                                      None        None
      10.0.99.4                                          None        -
      65520 65510                                                     
u*>i  10.10.66.0/24                                      None        None
      10.0.99.4                                          None        -
      65520 65510                                                     
u*>i  172.10.55.0/24                                     None        None
      10.0.99.4                                          None        -
      65520 65510                                                     
u*>i  172.10.66.0/24                                     None        None
      10.0.99.4                                          None        -
      65520 65510                                                     
-------------------------------------------------------------------------------
Routes : 4
===============================================================================
```

Moreover, R7 receives all the community values with the received NLRIs. For instance, the community string `65510:100` is present for the `10.10.55.0/24` prefix:

```txt
A:R7# show router bgp routes 10.10.55.0/24 detail 
===============================================================================
 BGP Router ID:10.30.30.7       AS:65530       Local AS:65530      
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked
 Origin codes  : i - IGP, e - EGP, ? - incomplete, > - best, b - backup

===============================================================================
BGP IPv4 Routes
===============================================================================
Original Attributes
 
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.4
Path Id        : None                   
From           : 10.0.99.4
Res. Nexthop   : 10.0.99.4
Local Pref.    : n/a                    Interface Name : toR4
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None                 
Community      : 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.20.20.3
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : External
AS-Path        : 65520 65510 
Route Tag      : 0                      
Neighbor-AS    : 65520
Orig Validation: NotFound               
Source Class   : 0                      Dest Class     : 0
 
```

Lets see how by tagging the `10.10.55.0/24` prefix with the `no-export` community we can change the BGP route advertisement process. To do so I will add a policy-statement to our border router R1 which will replace the community string `65510:100` of the  `10.10.55.0/24` prefix with the `no-export` one:

![pic](http://img-fotki.yandex.ru/get/3902/21639405.11c/0_8551d_e4cb7869_orig.png)

Lets track the community mutations of a `10.10.55.0/24` prefix. R3 receives this prefix from R1 and installs in its RIB. Community value for this prefix is `65510:100`:

```txt
A:R3# show router bgp routes 10.10.55.0/24 detail 
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
Original Attributes
 
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.0
Path Id        : None                   
From           : 10.0.99.0
Res. Nexthop   : 10.0.99.0
Local Pref.    : n/a                    Interface Name : toR1
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None                 
Community      : 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.1
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : External
AS-Path        : 65510 
Route Tag      : 0                      
Neighbor-AS    : 65510
Orig Validation: NotFound               
Source Class   : 0                      Dest Class     : 0
```

In order to replace the existing community value with a new one, we need to go to R1 and add the necessary policy configuration:

```txt
*A:R1>config>router>policy-options# info 
----------------------------------------------
            prefix-list "Customer_1_55_network"
                prefix 10.10.55.0/24 exact
            exit
            ## We have to specify community strings 
            ## we want to use with policy-statements
            community "West" members "65510:100"
            community "no-export" members "no-export"
            policy-statement "replace_with_no_exp"
                entry 10
                    from
                        prefix-list "Customer_1_55_network"
                    exit
                    action accept                      ## it is allowed to set up to 28 communities 
                        community replace "no-export"  ## which will replaces all the current ones
                    exit                              
                exit
            exit
----------------------------------------------

## add new policy-statement as "export" policy on R1 
A:R1>config>router>bgp# group "eBGP"
A:R1>config>router>bgp>group# export "replace_with_no_exp"


*A:R1>config>router>bgp>group# info 
----------------------------------------------
                export "replace_with_no_exp" 
                peer-as 65520
                split-horizon
                neighbor 10.0.99.1
                    local-address 10.0.99.0
                exit
----------------------------------------------
```

Ok, lets see if this change was casted properly, examine R1's RIB-In and RIB-Out tables and watch closely the `Community` value:

```txt
*A:R1>config>router>bgp>group# show router bgp routes 10.10.55.0/24 hunt 
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
Nexthop        : 10.10.10.5
Path Id        : None                   
From           : 10.10.10.5
Res. Nexthop   : 10.10.99.5
Local Pref.    : 100                    Interface Name : toR5
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None
Community      : 65510:100  ## R1 receives this community from R5
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.5
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : Internal
AS-Path        : No As-Path
Route Tag      : 0                      
Neighbor-AS    : N/A
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
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None
Community      : no-export  ## R1 replaced community string 65510:100 with no-export
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

Good, R1 **modified** the community attribute of this prefix and replaced the value it had received with a `no-export` well known community. It is important to note that `community replace` removes all communities for a prefix and sets a `no-export` instead them. So if we had >1 communities for the `10.10.55.0/24` prefix we would end up with just one `no-export` in the end.

Well, lets check with R3, how is this fella doing?

```txt
A:R3# show router bgp routes 10.10.55.0/24 detail 
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
Original Attributes
 
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.0
Path Id        : None                   
From           : 10.0.99.0
Res. Nexthop   : 10.0.99.0
Local Pref.    : n/a                    Interface Name : toR1
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None                 
Community      : no-export
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.1
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : External
AS-Path        : 65510 
Route Tag      : 0                      
Neighbor-AS    : 65510
Orig Validation: NotFound               
Source Class   : 0                      Dest Class     : 0
```

R3 receives and uses this prefix with the `no-export` community!

Before we jump to R7 let the dust to settle and think about the propagation path of the examined prefix.

* R5 originates this prefix and sets community `West "65510:100"`.
* R5 then advertise via its _BGP UPDATE_ message this prefix with this community to all of its iBGP peers (R1, R2 and R6 are the iBGP peers of R5).
* R1 (since we configured it this way) replaces community `West` with `no-export` for its eBGP peer R3, but **R2 does not**.

This leads to an interesting situation when R2 advertises `10.10.55.0/24` prefix with its original community `West "65510:100"` so R4 selects this route as the best (because R4 prefers eBGP routes over iBGP):

```txt
A:R4# show router bgp routes 10.10.55.0/24 detail 
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
Original Attributes
 
Network        : 10.10.55.0/24
Nexthop        : 10.0.99.2
Path Id        : None                   
From           : 10.0.99.2
Res. Nexthop   : 10.0.99.2
Local Pref.    : n/a                    Interface Name : toR2
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None                 
Community      : 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.2
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : External
AS-Path        : 65510 
Route Tag      : 0                      
Neighbor-AS    : 65510
Orig Validation: NotFound               
Source Class   : 0                      Dest Class     : 0
```

This highlights the fact that if you have more then one eBGP peers and want to communicate specific community value - you should do this on **every BGP border router**.

Check R7 BGP routes now. We expect that R3 does not advertise the prefix `10.10.55.0/24` to its eBGP peer R7, since it is instructed to do so by the `no-export` community:

```txt
## making sure R3 does not advertise 10.10.55.0/24 to R7

A:R3# show router bgp neighbor 10.0.99.5 advertised-routes
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
i     10.10.66.0/24                                      n/a         None
      10.0.99.4                                          None        -
      65520 65510
i     172.10.55.0/24                                     n/a         None
      10.0.99.4                                          None        -
      65520 65510
i     172.10.66.0/24                                     n/a         None
      10.0.99.4                                          None        -
      65520 65510
-------------------------------------------------------------------------------
Routes : 3
===============================================================================



## Now check R7

A:R7# show router bgp routes 10.10.55.0/24 
===============================================================================
 BGP Router ID:10.30.30.7       AS:65530       Local AS:65530      
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

As expected, no `10.10.55.0/24` prefix is advertised by R3. That is what `no-export` community for.

> Note, R3 **does not** advertise a route with the `no-export` to its eBGP peers, but it **does advertise** it to its iBGP peers:

```txt
## R3 advertises 10.10.55.0/24 with no-export community to iBGP peer R4
A:R3# show router bgp neighbor 10.20.20.4 advertised-routes
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
i     10.10.55.0/24                                      100         None
      10.20.20.3                                         None        -
      65510
i     10.10.66.0/24                                      100         None
      10.20.20.3                                         None        -
      65510
i     172.10.55.0/24                                     100         None
      10.20.20.3                                         None        -
      65510
i     172.10.66.0/24                                     100         None
      10.20.20.3                                         None        -
      65510
-------------------------------------------------------------------------------
Routes : 4
===============================================================================
```

The `no-advertise` community works a bit different - if a router receives a route with the `no-advertise` community it will **not advertise it at all** even to its iBGP peers.

## Removing community

Currently R2 does not modify any routes flying off to its eBGP peer R4. Lets imagine that we now have to remove the community `Customer_2` from all the Customer_2 routes on R2 before advertising them to the AS 65520. To do so we have to perform a community **remove operation**.

To filter all the routes with a community string `65510:2` we could use prefix lists or filter by the community string value:

```txt
*A:R2>config>router>policy-options# info
----------------------------------------------
            community "Customer2" members "65510:2"
            policy-statement "remove_Cust2_community"
                entry 10
                    from
                        community "Customer2" ## filter routes with specific community value
                    exit
                    action accept
                        community remove "Customer2"
                    exit
                exit
            exit
----------------------------------------------


*A:R2>config>router>bgp>group# export "remove_Cust2_community"
*A:R2>config>router>bgp>group# info
----------------------------------------------
                export "remove_Cust2_community"
                peer-as 65520
                split-horizon
                neighbor 10.0.99.3
                    local-address 10.0.99.2
                exit
----------------------------------------------
```

Now R2 selects the routes with the community value of `65510:2` and removes it before sending it to its eBGP peer R4:

The following output verifies this behavior:
```txt
*A:R2# show router bgp routes 172.10.55.0/24 hunt
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
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
Network        : 172.10.55.0/24
Nexthop        : 10.10.10.5
Path Id        : None
From           : 10.10.10.5
Res. Nexthop   : 10.10.99.0
Local Pref.    : 100                    Interface Name : toR1
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : 65510:2 65510:100   ## R2 receives this prefix with 2 communities
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.5
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP
Route Source   : Internal
AS-Path        : No As-Path
Route Tag      : 0
Neighbor-AS    : N/A
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
Network        : 172.10.55.0/24
Nexthop        : 10.0.99.2
Path Id        : None
To             : 10.0.99.3
Res. Nexthop   : n/a
Local Pref.    : n/a                    Interface Name : NotAvailable
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None
Connector      : None
Community      : 65510:100    ## on export operation R2 removes Customer_2 community
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.20.20.4
Origin         : IGP
AS-Path        : 65510
Route Tag      : 0
Neighbor-AS    : 65510
Orig Validation: NotFound
Source Class   : 0                      Dest Class     : 0

-------------------------------------------------------------------------------
Routes : 2
===============================================================================


## same thing happened to another Customer_2 route

A:R2# show router bgp routes 172.10.66.0/24 hunt 
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
-------------------------------------------------------------------------------
RIB In Entries
-------------------------------------------------------------------------------
Network        : 172.10.66.0/24
Nexthop        : 10.10.10.6
Path Id        : None                   
From           : 10.10.10.6
Res. Nexthop   : 10.10.99.3
Local Pref.    : 100                    Interface Name : toR6
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None
Community      : 65510:2 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.10.10.6
Fwd Class      : None                   Priority       : None
Flags          : Used  Valid  Best  IGP  
Route Source   : Internal
AS-Path        : No As-Path
Route Tag      : 0                      
Neighbor-AS    : N/A
Orig Validation: NotFound               
Source Class   : 0                      Dest Class     : 0
 
-------------------------------------------------------------------------------
RIB Out Entries
-------------------------------------------------------------------------------
Network        : 172.10.66.0/24
Nexthop        : 10.0.99.2
Path Id        : None                   
To             : 10.0.99.3
Res. Nexthop   : n/a
Local Pref.    : n/a                    Interface Name : NotAvailable
Aggregator AS  : None                   Aggregator     : None
Atomic Aggr.   : Not Atomic             MED            : None
AIGP Metric    : None                   
Connector      : None
Community      : 65510:100
Cluster        : No Cluster Members
Originator Id  : None                   Peer Router Id : 10.20.20.4
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

Remove operation removes a single community per action. Like in this example R2's RIB-In had the prefix `172.10.55.0/24` with both `65510:2` and `65510:200` values set the remove operation removed the `65510:2` community only.

## Matching community

The whole thing with the communities is about performing the actions against the prefixed matched with it. As you saw previously, the action based on a community should first match the community by its value and there are several ways to do the matching.

How can you pick the routes with the different communities and modify them altogether? One way would be to write multiple policy-statements with the same action and different `from community <name>` statements. This is a bruteforce. There are far more elegant techniques we are going to explore.

### "AND" and "OR" operators
To create a community that matches some of the community values you can use the `|` operator like that: `community West_or_Customer_2 members 65510:2|65510:100`. This community statement will match prefixes with the community strings like `65510:2`, `65510:2 65510:100` or `65510:2 63300:2 54487:200`.

To create a community statement that will match on a string that has multiple community values (aka `AND` operator) you can compose the following community statement: `community "A_and_B" members "65510:2" "65510:100"`. This community will match `65510:2 65510:100` or `100:100 200:200 65510:2 65510:100` but **not** `65510:2` or `100:100 65510:2`.

### Expressions

Nokia SR-OS has the built-in expressions engine equipped with a set of most commonly used operators. The Expressions syntax is described in the Routing Protocols guide:

```txt
community <name> expression <expression> [exact]

<expression>         : [900 chars max] - <expression> is one of the following:
                       <expression> {AND|OR} <expression>
                       [NOT] ( <expression> )
                       [NOT] <comm-id>
<exact>              : keyword
```

A good example on the expressions syntax is demonstrated by the statement below which matches exactly the prefixes with agiven list of communities attached to them:

```
community "West_and_Cust_2_ONLY" expression "65510:2 AND 65510:100" exact
```

This community, once used in the `from` statement of a policy will match prefixes with the community string `65510:2 65510:100` only (enforced by the `exact` statement).

### Regular Expressions

Another filtering technique is based on the regular expressions.

Let me show you how easy it is to filter the routes with a community string containing `65510:100` **or** `65510:2` values:

```txt
*A:R1>config>router>policy-options# info
----------------------------------------------
            prefix-list "Customer_1_55_network"
                prefix 10.10.55.0/24 exact
            exit
            community "West" members "65510:100"
            community "no-export" members "no-export"
            community "no-advertise" members "no-advertise"

            ## this community string equals to the form:
            ## members list contains 65510:2 OR 65510:100
            community "Customer_2_from_West" members "65510:(2|100)"
            
            <...omitted...>

            policy-statement "test_regexp_community"
                entry 10
                    from
                        community "Customer_2_from_West"
                    exit
                    action accept
                        community replace "no-advertise"
                    exit
                exit
            exit
----------------------------------------------
```

Here I defined the `Customer_2_from_West` community and used a simple regular expression for to match on the communities `65510:100` **or** `65510:2`. This regexp community string will match strings like  `65510:2` , `65510:2 65510:100` , `65510:2 63300:2 54487:200`

Of course you can create a far more complex regexps, check the table of the supported operators of the Routing Protocols Guide to build a regexp that meets your needs.

# Wrapping up

As usual, check out the full config that you will have at the end of this tutorial:

R1:
```txt
A:R1>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
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
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            prefix-list "Customer_1_55_network"
                prefix 10.10.55.0/24 exact
            exit
            community "West" members "65510:100"
            community "no-export" members "no-export"
            community "no-advertise" members "no-advertise"
            community "Customer_2_from_West" members "65510:(2|100)"
            policy-statement "replace_with_no_exp"
                entry 10
                    from
                        prefix-list "Customer_1_55_network"
                    exit
                    action accept
                        community replace "no-export"
                    exit
                exit
            exit
            policy-statement "test_regexp_community"
                entry 10
                    from
                        community "Customer_2_from_West"
                    exit
                    action accept
                        community replace "no-advertise"
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
                export "replace_with_no_exp" "test_regexp_community"
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
```

R2:
```
A:R2>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
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
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
            community "Customer2" members "65510:2"
            policy-statement "remove_Cust2_community"
                entry 10
                    from
                        community "Customer2"
                    exit
                    action accept
                        community remove "Customer2"
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
                export "remove_Cust2_community"
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
----------------------------------------------
```

R3:
```txt
A:R3>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
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
        interface "toR7"
            address 10.0.99.4/31
            port 1/1/5
            no shutdown
        exit
        autonomous-system 65520
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
            group "no_export_example"
                peer-as 65530
                split-horizon
                neighbor 10.0.99.5
                    local-address 10.0.99.4
                exit
            exit
            no shutdown
        exit
----------------------------------------------
```

R4:
```txt
A:R4>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
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
----------------------------------------------
```

R5:
```txt
A:R5>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "R5_Customer_1"
            address 10.10.55.1/24
            loopback
            no shutdown
        exit
        interface "R5_Customer_2"
            address 172.10.55.1/24
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
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
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
            policy-statement "Adv_Customers_nets"
                entry 10
                    from
                        protocol direct
                    exit
                    action next-entry
                        community add "West"
                    exit
                exit
                entry 20
                    from
                        prefix-list "Customer_2"
                    exit
                    action accept
                        community add "Customer_2"
                    exit
                exit
                entry 30
                    from
                        prefix-list "Customer_1"
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
            group "iBGP"
                export "Adv_Customers_nets"
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
----------------------------------------------
```

R6:
```txt
A:R6>config>router# info
----------------------------------------------
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "R6_Customer_1"
            address 10.10.66.1/24
            loopback
            no shutdown
        exit
        interface "R6_Customer_2"
            address 172.10.66.1/24
            loopback
            no shutdown
        exit
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
#--------------------------------------------------
echo "Policy Configuration"
#--------------------------------------------------
        policy-options
            begin
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
            policy-statement "Adv_Customers_nets"
                entry 10
                    from
                        protocol direct
                    exit
                    action next-entry
                        community add "West"
                    exit
                exit
                entry 20
                    from
                        prefix-list "Customer_2"
                    exit
                    action accept
                        community add "Customer_2"
                    exit
                exit
                entry 30
                    from
                        prefix-list "Customer_1"
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
            group "iBGP"
                export "Adv_Customers_nets"
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
----------------------------------------------
```

R7:
```txt
A:R7>config>router# info
#--------------------------------------------------
echo "IP Configuration"
#--------------------------------------------------
        interface "system"
            address 10.30.30.7/32
            no shutdown
        exit
        interface "toR4"
            address 10.0.99.5/31
            port 1/1/5
            no shutdown
        exit
        autonomous-system 65530
#--------------------------------------------------
echo "BGP Configuration"
#--------------------------------------------------
        bgp
            group "no_export_example"
                peer-as 65520
                split-horizon
                neighbor 10.0.99.4
                    local-address 10.0.99.5
                exit
            exit
            no shutdown
        exit
----------------------------------------------
```

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>