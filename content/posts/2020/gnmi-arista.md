---
date: 2020-07-25T07:00:00Z
comment_id: gnmi-arista
keywords:
- gnmi
- openconfig
- arista
- gnmic
- yang

tags:
- gnmi
- openconfig
- arista
- gnmic
- yang

title: Arista vEOS gNMI Tutorial
---
We were pleasantly surprised by the way community appreciated [gNMIc](https://netdevops.me/2020/gnmic-gnmi-cli-client-and-collector/) release. Thank you 🙏! That solidifies the fact that a well-formed, documented and easy to use gNMI tool was needed.

Now with gNMIc available to everybody its easy like never before to test gNMI implementation of different routing OSes. And in this post we will get our hands on **Arista vEOS**.
<!--more-->

For this journey we pack:

1. vEOS router (either physical or virtual)
2. gNMIc [documentation](https://gnmic.kmrd.dev/)
3. and a [gNMI-map](https://github.com/hellt/gnmi-map) to navigate through the gNMI realm.

Arista vEOS-for-labs is freely distributed and you can download the vmdk image from the official [software portal](https://www.arista.com/en/support/software-download).

**Table of contents**

1. [vEOS configuration](#veos-configuration)
2. [gNMI Capabilities](#gnmi-capabilities)
3. [Getting to know Arista YANG models](#getting-to-know-arista-yang-models)
4. [gNMI Get](#gnmi-get)
5. [gNMI Set](#gnmi-set)
6. [gNMI Subscribe](#gnmi-subscribe)
  1. [Sample subscriptions](#sample-subscriptions)
  2. [ON_CHANGE subcriptions](#on-change-subscriptions)

## vEOS configuration
Once your vEOS starts with a blank config (credentials: `admin` and an empty pass) we ought to add a minimal config to it before gNMI fun starts:

```txt
username admin privilege 15 secret admin
!
interface Ethernet1
   no switchport
   ip address 10.2.0.21/24
!
management api gnmi
   transport grpc default
```

With this config snippet we do a few things important from the gNMI standpoint:

* enabling password for `admin` to authenticate with a router
* configuring IP address for the `Ethernet1` interface to let gNMIc reach the router
* enabling `gnmi` management interface with the default transport config
  * default transport doesn't enforce TLS usage and uses `6030` port

That is all it takes to configure vEOS to start replying to our first gNMI RPCs, ridiculously easy!

## gNMI Capabilities
With gNMIc [installed](https://gnmic.kmrd.dev/install/), our first stop would be trying out the gNMI Capabilities RPC. The Capabilities RPC is quite instrumental as it uncovers which gNMI version the device runs, what models it is loaded with and which encoding it understands.

```bash
# 6030 - the default gNMI port on vEOS
# credentials are admin:admin
# --insecure mode is used to not enforce the TLS transport
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure capabilities
gNMI version: 0.7.0
supported models:
  - openconfig-rib-bgp, OpenConfig working group, 0.7.0
  - arista-qos-augments, Arista Networks, Inc., 
  - arista-srte-deviations, Arista Networks, Inc., 
  
<CLIPPED>

  - openconfig-platform-linecard, OpenConfig working group, 0.1.1
  - openconfig-if-tunnel, OpenConfig working group, 0.1.1
supported encodings:
  - JSON
  - JSON_IETF
  - ASCII
```

Judging by the output returned we see that 

* vEOS 4.24.1.1F in my lab runs the latest gNMI version 0.7.0
* it is configured with both openconfig and native models
* it supports two variants of JSON encoding with a useless ASCII

## Getting to know Arista YANG models
Before we can dive into the rest RPCs of gNMI service we have to get to know the YANG models vEOS listed as supported in Capabilities response.

Arista publishes its YANG models in the [aristanetworks/yang](https://github.com/aristanetworks/yang) repo and by the looks of it it seems they are OpenConfig believers. For the vEOS 4.24.1.1F release that I am running the [list of YANG](https://github.com/aristanetworks/yang/tree/master/EOS-4.24.0F) models is definitely angled towards OpenConfig models with native YANG models marked as experimental.

Browsing the source OC YANG files in this repo is one way to understand the structure of the models, or we can use [pyang](https://github.com/hellt/pyang-docker) or [goyang](https://github.com/openconfig/goyang) to generate a tree view. Michael Kashin shows [here](https://github.com/networkop/acb-oc) how to use goyang to quickly generate tree views of Arista models.

Once we know the structure of the OC YANG models vEOS is equipped with we can finally get to more advanced RPCs fetching, setting and subscribing.

> If YANG transformation topic is hard on you, ping me in comments and I will expand on this.

## gNMI Get
Now that we know which models our gear runs we can easily issue a gNMI Get RPC with [`get`](https://gnmic.kmrd.dev/cmd/get/) command. Lets pretend that we would like to know the configured IP addresses on the vEOS. All it takes is to carefully walk through the OC model to the right leaf:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure get \
        --path "/interfaces/interface[name=*]/subinterfaces/subinterface[index=*]/ipv4/addresses/address/config/ip"
{
  "source": "10.2.0.21:6030",
  "time": "1970-01-01T02:00:00+02:00",
  "updates": [
    {
      "Path": "/interfaces/interface[name=Ethernet1]/subinterfaces/subinterface[index=0]/ipv4/addresses/address[ip=10.2.0.21]/config/ip",
      "values": {
        "interfaces/interface/subinterfaces/subinterface/ipv4/addresses/address/config/ip": "10.2.0.21"
      }
    }
  ]
}
```

The returned output indicates that router has only one IPv4 address `10.2.0.21` configured and it is contained within the `/interfaces/interface[name=Ethernet1]/subinterfaces/subinterface[index=0]/ipv4/addresses/address[ip=10.2.0.21]/config/ip` path. The paths in its turn shows that the interfaces that has this IP is `Ethernet1`.

#### gNMI Get ALL
One particular trick that might come very handy is getting the entire config/state of the router with gNMI. That will likely output a lot of data but it will enable you to search through it and find the right path in the model for a more precise get/set/subscribe queries.

The trick is to specify the root `/` path for your Get RPC that will dump all the data from the router. Its better to redirect the output to a file:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure get --path / > /tmp/arista.all.json
```

[Here](https://gist.github.com/hellt/7f274d6ac65a88875e8eab1b5afef336) is the resulting JSON that I fetched from my lab router. This way you can "reverse engineer" the models tree view by letting a router send you all its state and config.

## gNMI Set
Our next RPC will change the configuration on a vEOS router. This is done with the gNMIc [`set`](https://gnmic.kmrd.dev/cmd/set/) command.

#### Updating configuration
A quick example would be to add a description to a port. But first lets ensure that its not set:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure get \
        --path "/interfaces/interface[name=Ethernet1]/config/description"
{
  "source": "10.2.0.21:6030",
  "time": "1970-01-01T02:00:00+02:00",
  "updates": [
    {
      "Path": "/interfaces/interface[name=Ethernet1]/config/description",
      "values": {
        "interfaces/interface/config/description": ""
      }
    }
  ]
}
```

All good, the description is empty, lets set it to `gnmic-example` value:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure set \
        --update-path "/interfaces/interface[name=Ethernet1]/config/description" \
        --update-value "gnmic-example"
{
  "source": "10.2.0.21:6030",
  "timestamp": 1595749808169752510,
  "time": "2020-07-26T10:50:08.16975251+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "/interfaces/interface[name=Ethernet1]/config/description"
    }
  ]
}
```

With the implicit-type kind of a set operation gNMIc will use the JSON encoding for the value specified with `--update-value` flag. The result we get back from the box confirms that the UPDATE operation has been applied. Now we can check if the value is indeed set by repeating the get command:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure get \
--path "/interfaces/interface[name=Ethernet1]/config/description"
{
  "source": "10.2.0.21:6030",
  "time": "1970-01-01T02:00:00+02:00",
  "updates": [
    {
      "Path": "/interfaces/interface[name=Ethernet1]/config/description",
      "values": {
        "interfaces/interface/config/description": "gnmic-example"
      }
    }
  ]
}
```

Now we see the description set to the value we specified.

> gNMIc supports many ways to provide the configuration values, check [`set`](https://gnmic.kmrd.dev/cmd/set/) command docs for all the options.

#### Deleting configuration
gNMI Set RPC allows not only to update/replace the configuration but also to delete it. Lets remove the description we set before with the [`delete`](https://gnmic.kmrd.dev/cmd/set/#delete) flag of the set command.:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure set \
        --delete "/interfaces/interface[name=Ethernet1]/config/description"
{
  "source": "10.2.0.21:6030",
  "timestamp": 1595750232015131720,
  "time": "2020-07-26T10:57:12.01513172+03:00",
  "results": [
    {
      "operation": "DELETE",
      "path": "/interfaces/interface[name=Ethernet1]/config/description"
    }
  ]
}
```

## gNMI Subscribe
And we managed to get to the end of it. The crown jewel of gNMI service - Subscribe RPC.

To demonstrate gNMI subscriptions done with the corresponding [`subscribe`](https://gnmic.kmrd.dev/cmd/subscribe/) command we will solve the following tasks:

* subscribe to interface counters and see the effect of SAMPLE subscriptions with different sampling intervals
* subscribe to a protocol admin status and see the effect of ON_CHANGE mode of subscription

The [`subscribe`](https://gnmic.kmrd.dev/cmd/subscribe/) command has a lot of options which are instrumental to tailor the command behavior to your needs.

#### Sample subscriptions
For the [sampled](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md#35152-stream-subscriptions) subscriptions we expect to receive the value of the subscribed data node with each sampling interval; doesn't matter if the data changes in-between the sampling timestamps or not, we will get it with the cadence specified by the sample-interval.

Samples subscriptions are useful for rapidly changing data, like interface counters. Lets subscribe to our only interface `Ethernet1` with 2 seconds sampling interval.

> Note, we had to disable QoS marking by setting it to 0, since vEOS does not support marking for gNMI messages.

```text
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure subscribe \
        --path "/interfaces/interface[name=Ethernet1]/subinterfaces/subinterface/state/counters/in-octets" \
        --stream-mode sample --sample-interval 2s \
        --qos 0
```

> ![sample](https://gitlab.com/rdodin/pics/-/wikis/uploads/43e9b925c7d8f6ce1703b06e823971d3/CleanShot_2020-07-26_at_10.33.24.gif)

<center><small>_sampled subscriptions arriving with 2s interval_</small></center>

#### On Change subscriptions
The other popular subscription mode is ON_CHANGE where the router pushes the data towards the collector when the data changes. With such a mode you don't push the data unnecessarily.

A popular use case for ON_CHANGE subscriptions is to subscribe to oper/admin state of control plane protocols to get notified when the state changes (aka trap).

To demonstrate this behavior we will
* configure BGP process on vEOS
* subscribe with ON_CHANGE mode to the BGP AS leaf effectively watching its value.

Our trivial BGP configuration:
```
!
ip routing
!
router bgp 2
```

Now lets subscribe to the AS number with:

```
$ gnmic -a 10.2.0.21:6030 -u admin -p admin --insecure subscribe \
        --path "/network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=BGP]/bgp/global/config/as" \
        --stream-mode on_change \
        --qos 0

{
  "source": "10.2.0.21:6030",
  "subscription-name": "default",
  "timestamp": 1595753683536455210,
  "time": "2020-07-26T11:54:43.53645521+03:00",
  "updates": [
    {
      "Path": "network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=BGP]/bgp/global/config/as",
      "values": {
        "network-instances/network-instance/protocols/protocol/bgp/global/config/as": 2
      }
    }
  ]
}
```

Our subscription will stand still, as the AS number doesn't change, the router will not update it, unless the value changes.

Lets remove the BGP process from the router and see what happens:

> ![on_change](https://gitlab.com/rdodin/pics/-/wikis/uploads/4055ac6cf3cd588a0623e7ac8750b381/CleanShot_2020-07-26_at_10.58.52.gif)

<center><small>_on change subscriptions arrive when data changes_</small></center>

Here we receive a notification update about the deletion of the data we subscribed to immediately when the deletion happens.

## Summary
In this post we put [gNMIc](https://gnmic.kmrd.dev/) to a good use against Arista vEOS. All of the gNMI service RPCs have been successfully tested against vEOS, we have identified which encoding vEOS supports, found out that it uses OpenConfig models mostly and it can't use QoS markings.

On the bright side, vEOS supports ON_CHANGE subscriptions and is capable of delivering subsecond updates.

