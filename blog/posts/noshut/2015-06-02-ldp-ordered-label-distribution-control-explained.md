---

date: 2015-06-02
# url: /2015/06/ldp-ordered-label-distribution-control-explained/
comments: true
tags:
  - LDP
  - MPLS
---
# LDP. Ordered Label Distribution Control explained

Major network vendors (except Cisco) default to the following modes of Label Distribution Protocol (LDP) operation (as per <a href="https://tools.ietf.org/html/rfc5036" target="_blank">RFC 5036 LDP Specification</a>):

- Label Distribution (Advertisement): Downstream Unsolicited (section 2.6.3)
- Label Control: Ordered (section 2.6.1)
- Label Retention: Liberal (section 2.6.2)

This topic focuses on Ordered Label Distribution Control procedure to help you better understand when LSR actually assigns labels and initiates transmission of a label mapping.

<!-- more -->

Both [RFC 3031 Multiprotocol Label Switching Architecture](https://tools.ietf.org/html/rfc3031#section-3.19) and <a href="https://tools.ietf.org/html/rfc5036" target="_blank">RFC 5036 LDP Specification</a> give definition for_Ordered Label Distribution Control_ mode:

<p style="padding-left: 30px;">
  <strong>RFC 3031:</strong> In Ordered LSP Control, an LSR only binds a label to a particular FEC if it is the egress LSR for that FEC, or if it has already received a label binding for that FEC from its next hop for that FEC.
</p>

<p style="padding-left: 30px;">
  <strong>RFC 5036: </strong>When using LSP Ordered Control, an LSR may initiate the transmission of a label mapping only for a FEC for which it has a label mapping for the FEC next hop, or for which the LSR is the egress. For each FEC for which the LSR is not the egress and no mapping exists, the LSR MUST wait until a label from a downstream LSR is received before mapping the FEC and passing corresponding labels to upstream LSRs.
</p>

Lets break this definition into distinct sentences:

  1. In case LSR is the egress router for a FEC _X_ then LSR maps label to FEC _X_ and transmits this label mapping to its LDP peers;
  2. In case LSR is not the egress router for a FEC _X_ then in order to map a label for this FEC and to propagate this label mapping to its peers, **it has to wait** until it receives a label mapping for this particular FEC _X_ from its downstream LDP peer.

In this manner the entire LSP is established before MPLS begins to map data onto the LSP, preventing early data mapping from occurring on the first LSR in the path.

Let's take a look at this simple topology to illustrate these steps.

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/15557/21639405.11b/0_8342d_43f8a67c_XL.png" alt="" width="800" height="382" />](http://img-fotki.yandex.ru/get/15557/21639405.11b/0_8342d_43f8a67c_orig.png)

Routers R1-R2-R3 have OSPF enabled on their interfaces and announce their loopback (or system, as long as we&#8217;re using with Alcatel-Lucent routers in this example) IP addresses. So every router has a route to other router&#8217;s loopback address.

```
A:R1# show router route-table

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
10.1.2.0/24                                   Local   Local     00h08m36s  0
       toR2                                                         0
10.2.3.0/24                                   Remote  OSPF      00h04m20s  10
       10.1.2.2                                                     200
10.10.10.1/32                                 Local   Local     00h08m36s  0
       system                                                       0
10.10.10.2/32                                 Remote  OSPF      00h08m05s  10
       10.1.2.2                                                     100
10.10.10.3/32                                 Remote  OSPF      00h01m22s  10
       10.1.2.2                                                     200
-------------------------------------------------------------------------------
No. of Routes: 5
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================
```

To investigate label mappings creation and propagation processes lets dive into step-by-step LDP operation for the particular Forward Equivalence Class (FEC) `10.10.10.1/32` &#8211; which is the loopback address of the router R1.

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/5105/21639405.11b/0_8342e_cd5af88f_XL.png" alt="" width="800" height="344" />](http://img-fotki.yandex.ru/get/5105/21639405.11b/0_8342e_cd5af88f_orig.png)

&nbsp;

Everything starts with R1 which is an Egress router for the FEC 10.10.10.1/32. According to abovementioned _Ordered Distribution Control_ mode definition R1 (again, as an Egress router) has a right to create a binding for the FEC 10.10.10.1/32. Such bindings, created for the FECs which are local to a router often called &#8220;Local bindings&#8221;.

Let&#8217;s check that R1 actually has this _local_ label mapping in its Label Information Base:

```
A:R1# show router ldp bindings

===============================================================================
LDP Bindings (IPv4 LSR ID 10.10.10.1:0)
             (IPv6 LSR ID ::[0])
===============================================================================
LDP IPv4 Prefix Bindings
===============================================================================
Prefix                                      IngLbl                    EgrLbl
Peer                                        EgrIntf/LspId
EgrNextHop
-------------------------------------------------------------------------------
10.10.10.1/32                               131071U                     --
10.10.10.2:0                                  --
  --
<-- omitted -->
```

Yep, there it is &#8211; R1 tells us that he assigned a **local label 131071** for the FEC `10.10.10.1/32`. Local bindings appear in the &#8220;IngLbl&#8221; column. Ingress label 131071 means that R1 expects its LDP peers to send their MPLS packets destined to the FEC 10.10.10.1/32 equipped with the label 131071 on top of MPLS label stack.

Another benefit for being an Egress router for the FEC 10.10.10.1/32 is that R1 could **send** his locally created binding to its peers **right away**. Therefore, R1 sends this mapping to its LDP peer **10.10.10.2:0** (R2).

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/6723/21639405.11b/0_83430_8d08d0d0_XL.png" alt="" width="800" height="368" />](http://img-fotki.yandex.ru/get/6723/21639405.11b/0_83430_8d08d0d0_orig.png)

&nbsp;

When R2 receives this label mapping message from R1 regarding the FEC 10.10.10.1, it follows this logic: I have received the label mapping for the FEC 10.10.10.1 sent from R1. Thanks to [Liberal Retention mode](https://tools.ietf.org/html/rfc5036#section-2.6.2.2) I place this label binding into my LIB under &#8220;EgrLbl&#8221; column without further investigation. Such label mapping is often called **remote label** mapping since it came from the remote LDP peer.

```
*A:R2# show router ldp bindings prefixes prefix 10.10.10.1/32

===============================================================================
LDP Bindings (IPv4 LSR ID 10.10.10.2:0)
             (IPv6 LSR ID ::[0])
===============================================================================
Legend: U - Label In Use,  N - Label Not In Use, W - Label Withdrawn
        WP - Label Withdraw Pending, BU - Alternate For Fast Re-Route
===============================================================================
LDP IPv4 Prefix Bindings
===============================================================================
Prefix                                      IngLbl                    EgrLbl
Peer                                        EgrIntf/LspId
EgrNextHop
-------------------------------------------------------------------------------
10.10.10.1/32                                 --                      131071
10.10.10.1:0                                1/1/1
10.1.2.1

< omitted >
```

But in order to be able to make its own label mapping for the 10.10.10.1/32 _Ordered Label Distribution Control procedure_ demands R2 to check **if remote binding was received from a <u>downstream</u> router** for this particular FEC. Yes, it is, R1 is downstream router regarding data flow destined to the FEC 10.10.10.1/32.

Good, R2 recognized R1 as a downstream router and therefore allowed to make its own label mapping (recall ordered control mode definition) for this FEC and propagate its mapping update to R3.

R2 did not send this update to R1, because R1 is the owner of 10.10.10.1/32 and will never be a transit label switching router for this FEC.

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/5410/21639405.11b/0_83431_78b4c1c6_XL.png" alt="" width="800" height="403" />](http://img-fotki.yandex.ru/get/5410/21639405.11b/0_83431_78b4c1c6_orig.png)

&nbsp;

Lets see R2&#8217;s LIB:

```
*A:R2# show router ldp bindings prefixes prefix 10.10.10.1/32

===============================================================================
LDP Bindings (IPv4 LSR ID 10.10.10.2:0)
             (IPv6 LSR ID ::[0])
===============================================================================
Legend: U - Label In Use,  N - Label Not In Use, W - Label Withdrawn
        WP - Label Withdraw Pending, BU - Alternate For Fast Re-Route
===============================================================================
LDP IPv4 Prefix Bindings
===============================================================================
Prefix                                      IngLbl                    EgrLbl
Peer                                        EgrIntf/LspId
EgrNextHop
-------------------------------------------------------------------------------
10.10.10.1/32                                 --                      131071
10.10.10.1:0                                1/1/1
10.1.2.1

10.10.10.1/32                               131070U                   131070
10.10.10.3:0                                  --
  --

-------------------------------------------------------------------------------
No. of IPv4 Prefix Bindings: 2
===============================================================================
```

Take a look at the highlighted strings, R2 chose a label value of 131070 for the FEC and sent this binding to LDP peer with identifier 10.10.10.3:0 (which is R3). We will cover the reason behind existence of the label 131070 in &#8220;EgrLbl&#8221; for peer 10.10.10.3:0 a bit later.

Ok, R2 sent his mapping for 10.10.10.1/32 to R3, what happens next?

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/5407/21639405.11b/0_83432_190b68c1_XL.png" alt="" width="800" height="413" />](http://img-fotki.yandex.ru/get/5407/21639405.11b/0_83432_190b68c1_orig.png)

R3 follows the same logic as R2 did when it receives label mapping message from R2. In the same manner R3 installs remote label binding from R2, checks that R2 positioned downstream regarding data flow to address 10.10.10.1/32 and assigns local label binding for this FEC. But one thing is different with R3 &#8211; since R2 is not an owner for the FEC 10.10.10.1 then R3 can send label mapping message backward to R2 &#8211; see timestamp E.

&nbsp;

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/3611/21639405.11b/0_83434_635118c2_XL.png" alt="" width="800" height="323" />](http://img-fotki.yandex.ru/get/3611/21639405.11b/0_83434_635118c2_orig.png)

Lets take a look at R3&#8217;s LIB:

```
A:R3# show router ldp bindings prefixes prefix 10.10.10.1/32

===============================================================================
LDP Bindings (IPv4 LSR ID 10.10.10.3:0)
             (IPv6 LSR ID ::[0])
===============================================================================
Legend: U - Label In Use,  N - Label Not In Use, W - Label Withdrawn
        WP - Label Withdraw Pending, BU - Alternate For Fast Re-Route
===============================================================================
LDP IPv4 Prefix Bindings
===============================================================================
Prefix                                      IngLbl                    EgrLbl
Peer                                        EgrIntf/LspId
EgrNextHop
-------------------------------------------------------------------------------
10.10.10.1/32                               131070N                   131070
10.10.10.2:0                                1/1/2
10.2.3.2

-------------------------------------------------------------------------------
No. of IPv4 Prefix Bindings: 1
===============================================================================
```

When R2 receives this label mapping message from R3 regarding FEC 10.10.10.1, it follows the same logic: I have received the label mapping for the FEC 10.10.10.1. I will place this label binding into my LIB no matter what. This explains the egress label value 131070 in R2&#8217;s LIB (see Listing #4) from peer 10.10.10.3:0.

Although R3 installed a label, it will not take any actions regarding this update since it came from **R3**, which **is not a downstream router** for the FEC 10.10.10.1/32.

This completes label propagation for the FEC 10.10.10.1/32.

## Downstream or not?

You may have already noticed that the key in making a decision to create a label mapping for a FEC is if the label mapping came from a downstream router? But how does a router decide if its peer is downstream router or upstream? Let&#8217;s think about it&#8230;

Rewind to Timestamp B. R2 receives a label mapping message from R1 and needs to decide if R1 is a downstream router regarding FEC 10.10.10.1/32? It looks into Forwarding Information Base for this prefix and sees the next-hop address for it is 10.1.2.1:

```
*A:R2# show router fib 1 10.10.10.1/32

===============================================================================
FIB Display
===============================================================================
Prefix [Flags]                                              Protocol
    NextHop
-------------------------------------------------------------------------------
10.10.10.1/32                                               OSPF
    10.1.2.1 (toR1)
-------------------------------------------------------------------------------
Total Entries : 1
-------------------------------------------------------------------------------
```

So what? We have a next-hop, but how do we know if IP address 10.1.2.1 belongs to R1? To asnswer this question we need to open <a href="https://tools.ietf.org/html/rfc5036" target="_blank">RFC 5036 LDP Specification</a> once again. Navigate to [section 2.7](https://tools.ietf.org/html/rfc5036#section-2.7)  LDP Identifiers and Next Hop Addresses:

<p style="padding-left: 30px;">
  To enable LSRs to map between a peer LDP Identifier and the peer&#8217;s addresses, LSRs advertise their addresses using <strong>LDP Address</strong> and Withdraw Address messages.
</p>

Well, it seems LDP peers share _LDP Address messages_ where they communicate all of their configured IP addresses, let&#8217;s see under the hood:

[<img class="aligncenter" src="http://img-fotki.yandex.ru/get/5201/21639405.11b/0_83441_d97a2240_XL.png" alt="" width="800" height="505" />](http://img-fotki.yandex.ru/get/5201/21639405.11b/0_83441_d97a2240_XXL.png)

That is the answer. LDP speaker should tell its peers about the addresses it has configured. This info communicated via Address Messages and helps remote peers to map LDP indentifier to an IP address.

With this information provided R2 now can tell for sure that next-hop address it has in its Forwarding Information Base belongs to R1. And that is how R2 can tell that R1 is a downstream router &#8211; by matching its next-hop address from FIB with an IP addresses provided in an Address Message from R1.

And this is all for this time. If you have any questions regarding this topic &#8211; do not hesitate, I will gladly address them.
