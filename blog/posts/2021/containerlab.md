---
date: 2021-04-01
comments: true
keywords:
  - containerlab
  - srlinux
  - ceos
  - crpd
  - sonic
  - frr
  - nokia
  - juniper
  - cisco
  - arista
tags:
  - containerlab
  - srlinux
  - ceos
  - crpd
  - sonic
  - frr
  - nokia
  - juniper
  - cisco
  - arista

---

# Containerlab - your network-centric labs with a Docker UX

With the growing number of containerized Network Operating Systems (NOS) grows the demand to easily run them in the user-defined, versatile lab topologies. Unfortunately, container runtimes alone and tools like docker-compose are not a particularly good fit for that purpose, as they do not allow a user to easily create p2p connections between the containers.

[Containerlab](https://containerlab.srlinux.dev) provides a framework for orchestrating networking labs with containers. It starts the containers, builds a virtual wiring between them to create a topology of users choice and then manages a lab lifecycle.

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/xdi7rwdJgkg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></center>

Containerlab focuses on containerized Network Operating Systems such as:

- [Nokia SR-Linux](https://www.nokia.com/networks/products/service-router-linux-NOS/)
- [Arista cEOS](https://www.arista.com/en/products/software-controlled-container-networking)
- [Azure SONiC](https://azure.github.io/SONiC/)
- [Juniper cRPD](https://www.juniper.net/documentation/en_US/crpd/topics/concept/understanding-crpd.html)
- [FRR](http://docs.frrouting.org/en/latest/overview.html)

In addition to native containerized NOSes, containerlab can launch traditional virtual-machine based routers using [vrnetlab integration](https://containerlab.srlinux.dev/manual/vrnetlab/):

- Nokia virtual SR OS (vSim/VSR)
- Juniper vMX
- Cisco IOS XRv
- Arista vEOS

And, of course, containerlab is perfectly capable of wiring up arbitrary linux containers which can host your network applications, virtual functions or simply be a test client. With all that, containerlab provides a single IaaC interface to manage labs which can span contain all the needed variants of nodes:

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:1,&quot;zoom&quot;:1.5,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/srl-wim/container-lab/diagrams/index.md&quot;}"></div>

<!-- more -->

## The WHY

As it often happens, <https://containerlab.srlinux.dev> was created by engineers to address their needs.

In containerlab's case the need was simple - to be able to create networking topologies with containerized Network Operating Systems

As you might know, the off-the-shelf tools like docker-compose are not really fit-for-purpose of defining a multi-interfaced containers, therefore many of us created the bespoke bash scripts ruling a web of veth pairs between containers.

Containerlab solves this, and helps many other pain points you might have seen while running your labs.

## The WHAT

Containerlab is what docker-compose would be if it was created with networking topologies in mind.

We use so-called `clab files` to define a topology that is then deployed by containerlab anywhere, where docker runs without any 3rd party dependencies.

![p1](https://pbs.twimg.com/media/Ex1F03XWUAE16Ws?format=jpg&name=4096x4096)

The `clab file` is a YAML in disguise, it offers a way to define your topology top-to-bottom.

Balancing between the simplicity, conventionality and expressiveness it allows users to define topologies that are both easy to read/write and yet are not limited in features)

```yaml
name: srlceos01

topology:
  nodes:
    srl:
      kind: srl
      image: srlinux:20.6.3-145
      license: license.key
    ceos:
      kind: ceos
      image: ceos:4.25.0F

  links:
    - endpoints: ["srl:e1-1", "ceos:eth1"]
```

## The HOW

This `clab file` is all that is needed to spin up a lab of the two interconnected nodes - Nokia SR Linux and Arista cEOS.

Yes, that is all that's needed. No bulky emulators, no bespoke datapaths. A pure container-based lab powered by linux networking primitives.

That is what you get:

![p2](https://pbs.twimg.com/media/Ex1J3PRWgAEZyMc?format=jpg&name=4096x4096)

All the heavy lifting of launching the containerized NOS is abstracted by containerlab kinds. It knows how to start SR Linux and cEOS. Just tell it which kind you need and what image to use

No need to keep handy those endless ENV vars or lengthy  commands.

Interconnecting the nodes is as easy as writing a string of text.
Tell containerlab which interfaces you want to be interconnected, and it will create the veth pairs blazingly fast.

![p3](https://pbs.twimg.com/media/Ex1K9C6W8AIiEpI?format=jpg&name=4096x4096)

And surely enough, that is just the tip of an iceberg, containerlab packs a ton of features which I won't repeat here, as they are all mentioned in the [docs site](https://containerlab.srlinux.dev/#features) we carefully maintain.

## Multivendor capabilities

### Arista cEOS

Although containerlab was born in Nokia, it is now truly multivendor.

Arista folks reading this? Here is a full blown support for [cEOS](https://containerlab.srlinux.dev/manual/kinds/ceos/)

Run cEOS as a first class citizen, it even makes cEOS to respect the docker assigned IP address.

<center><blockquote class="twitter-tweet"><p lang="en" dir="ltr">Although containerlab was born in Nokia, it is now truly multivendor.<br><br>Arista folks, you there? <a href="https://twitter.com/burneeed?ref_src=twsrc%5Etfw">@burneeed</a> <a href="https://twitter.com/flat_planet?ref_src=twsrc%5Etfw">@flat_planet</a> <a href="https://twitter.com/TiTom73?ref_src=twsrc%5Etfw">@TiTom73</a> <a href="https://twitter.com/loopback1?ref_src=twsrc%5Etfw">@loopback1</a> <a href="https://t.co/N9OJQByszR">https://t.co/N9OJQByszR</a><br><br>Containerlab can run cEOS as a first class citizen, it even makes cEOS to respect the docker assigned IP address <a href="https://t.co/HWFpMSyiAE">pic.twitter.com/HWFpMSyiAE</a></p>&mdash; Roman Dodin (@ntdvps) <a href="https://twitter.com/ntdvps/status/1377514634962464769?ref_src=twsrc%5Etfw">April 1, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></center>

### Juniper cRPD

We don't pick sides in our choice of containerized NOS support, so [Juniper cRPD](https://containerlab.srlinux.dev/manual/kinds/crpd/) is as welcome as any other NOS.

![p4](https://pbs.twimg.com/media/Ex1Q0URXAAM5UsR?format=jpg&name=large)

### SONiC

Yes, [SONiC](https://containerlab.srlinux.dev/manual/kinds/sonic-vs/) is there as well and we spent some time to make it beautifully integrated and start up just as any other NOS.

A perfect candidate to be paired with Nokia SR Linux and see a modern DC interop use cases through and through.

![p5sonic](https://gitlab.com/rdodin/pics/-/wikis/uploads/4dc93d33005a5b005b72fde2645e70de/image.png)

### FRR

Coming from the free OSS NOS camp? FRR [is also under containerlab](https://containerlab.srlinux.dev/lab-examples/srl-frr/) umbrella.

Basically, any Linux based NOS that you can image will be able to be run by containerlab, as it is agnostic to the packages inside the linux container.

Containerlab is extensible, and if anything that is dear to your heart is missing it definitely can be added.

## Network node + regular containers

Also remember that the same clab file can really be like docker-compose file.

- ✅ Need to bind mount files/dirs to your network node
- ✅ Want to expose a port to a container host
- ✅ Maybe set ENV vars
- ✅ Or change/augment the CMD the node runs

I am repeating myself, but can't stress this enough, containerlab clab files are a mix of a docker-compose and some networking stardust.
That means that you can define a topology that will have both linux containers and network nodes.

A perfect example - a telemetry lab.

![tele](https://pbs.twimg.com/media/Ex1S7F3WEA8KeWi?format=jpg&name=4096x4096)

The above topology is defined in [a single clab file](https://github.com/srl-labs/srl-telemetry-lab/blob/main/st.yml) that has your networking nodes and regular linux container defined.

A single gittable, versionable lightweight text file defines a ready-made topology that is spinnable in 15 seconds.

## What about my VM-based routers?

I can imagine how @ioshints says that this container-ish thingy can't stand a chance vs real-deal qcow2 packaged VMs.

Yes, a valid concern, but we are lucky that guys like @plajjan did some splendid work that we leveraged in containerlab.

Watch my hands.

Containerlab can run classic VMs like Nokia SR OS, Cisco IOS-XR, Juniper vMX, Arista vEOS in the container packaging. Yes, defined in the same clab file.

This is possible by using our adapted version of vrnetlab project - <https://github.com/hellt/vrnetlab>

![vr](https://pbs.twimg.com/media/Ex1Wq4FWQAQZrzo?format=jpg&name=4096x4096)

```yaml
name: vr04

topology:
  nodes:
    srl:
      kind: srl
      image: srlinux:20.6.3-145
      license: license.key
    xrv9k:
      kind: vr-xrv9k
      image: vr-xrv:7.2.1

  links:
    - endpoints: ["srl:e1-1", "xrv9k:eth1"]
```

With this you can turn any EVE-NG or GNS lab that you have into a clab file. By packaging your routers into container images you can push them into a registry and enjoy your labs with a docker UX.

Total control about reproducibility.

![reg](https://pbs.twimg.com/media/Ex3iqvCWYAAJ-Wh?format=jpg&name=large)

In fact, in Nokia many engineers already transitioned from virsh/EVE/GNS to containerlab and they helped us refine containerlab to make it play nicely with classic VM-based products.

The benefits of treating a router VM as a container are quite compelling.

<center><blockquote class="twitter-tweet"><p lang="en" dir="ltr">In fact, in Nokia many engineers already transitioned from virsh/EVE/GNS to containerlab and they helped us refine containerlab to make it play nicely with classic VM-based products.<br><br>The benefits of treating a router VM as a container are quite compelling. <a href="https://t.co/B5LnDpxDtX">pic.twitter.com/B5LnDpxDtX</a></p>&mdash; Roman Dodin (@ntdvps) <a href="https://twitter.com/ntdvps/status/1377514683947696128?ref_src=twsrc%5Etfw">April 1, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></center>

## Sharing lab access

Ok, so in the same containerlab file we can

- run any linux container
- run most popular containerized NOSes
- run VM-based routers

what else?

Globe with meridians here goes the story about our collab with @atoonk and his @mysocketio service

There is a thing about 'em labs. They usually run in a closed, isolated environments, with a handful of ppl having access to it.

But quite often you find yourself in need to share access to this lab. And then it becomes a battle of a hundred SSH tunnels and exposed credentials.

By integrating mysocketio service into containerlab we achieved an on-demand, stable & secure and lab access sharing.

Check out this short video that explains the concepts:

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/6t0fPJtwaGM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></center>

Just like this, adding a single line to your node definition, you make it available via Internet over the anycast network with optional strict OAuth rules for a fine grained access control.

![mysock](https://pbs.twimg.com/media/Ex3lFm0XEAAz4De?format=jpg&name=4096x4096)

## What are the use cases?

The usecases where containerlab can shine are not only limited to labs.

It is a perfect demo tool, you have a guarantee that your lab will run just like it always was thanks to strict versioning and immutable container images. With a very small footprint, requiring only Docker

Another domain where we see containerlab be of a great help is CI/CD.
Github Actions and Gitlab CI both have docker installed on their runners, so you can launch topologies and test them in your CI easily.

![ci](https://pbs.twimg.com/media/Ex3ns2hWYAIfshN?format=jpg&name=4096x4096)

## Any examples?

Definitely, we also launched a satellite repo for containerlab based labs - <https://clabs.netdevops.me>

This catalog is meant to be an open collection of labs built with containerlab.
Anything you build with containerlab I will gladly feature there with full attribution to an author.

You will likely find more use cases that fit your need, so give <https://containerlab.srlinux.dev> a nice spin and let us know how it goes.

## Special thanks

I want to thank [@WHenderickx](https://twitter.com/WHenderickx) and [@Karimtw_](https://twitter.com/Karimtw_) who started this thing and created the core architecture.

Then our internal users and contributors for always providing feedback and thus making containerlab better. It was a truly team work.

A special kudos goes to [@networkop1](https://twitter.com/networkop1) who is always ahead of time and had a similar tool (docker-topo) created years ago.
We took inspiration from it when were creating the containerlab topo file schema.

Found this awesome, do not hesitate to star our repo - <https://github.com/srl-labs/containerlab> as a way of saying thanks.

Want to contribute? That is awesome and appreciated!

PS. The original announcement was made via this tweet-series.

<center><blockquote class="twitter-tweet"><p lang="en" dir="ltr">🚨 I&#39;ve been sitting on my hands for 3 months, but now the time has finally come...<br><br>🥼We are releasing containerlab - the open source CLI tool that may redefine the way you run networking labs.<a href="https://t.co/WZQGFWEttB">https://t.co/WZQGFWEttB</a><br><br>It will be a long 🧵but I guarantee, you will dig it.</p>&mdash; Roman Dodin (@ntdvps) <a href="https://twitter.com/ntdvps/status/1377514559653748737?ref_src=twsrc%5Etfw">April 1, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></center>

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
