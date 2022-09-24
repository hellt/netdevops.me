---
date: 2021-07-21
comments: true
keywords:
  - srlinux
  - containerlab
  - nokia
tags:
  - srlinux
  - containerlab
  - nokia

---
# Nokia SR Linux goes public

It's been almost two years since Nokia announced its [Data Center Fabric solution](https://www.nokia.com/networks/solutions/data-center-switching-fabric/). The three-layered solution ranged from hardware platforms all the way up in the stack to the DC fabric lifecycle management suite - [Fabric Services System (FSS)](https://www.nokia.com/networks/products/fabric-services-system/).

![pic1](https://gitlab.com/rdodin/pics/-/wikis/uploads/25f1ebe301b17296975c165fc2889d2a/image.png)

At the very heart of the DC Fabric solution lies a purpose-built, modern Network OS - [SR Linux](https://www.nokia.com/networks/products/service-router-linux-NOS/).

[![pic2](https://gitlab.com/rdodin/pics/-/wikis/uploads/96e2a0b880aede62dbaf1152608d6119/image.png)](https://gitlab.com/rdodin/pics/-/wikis/uploads/96e2a0b880aede62dbaf1152608d6119/image.png)

SR Linux comes with quite some interesting and innovative ideas. By being able to design the NOS from the ground up, the product team was freed from the legacy burdens which will be there have they decided to built the NOS on top of the existing one. Features like:

- YANG-first APIs
- Protobuf based SDK
- Disaggregated application stack
- Programmable CLI

are the result of taking a fresh look at the modern data center networks and building the NOS for the Netdevops era.

No wonders engineers around the world wanted to play with SR Linux and take those features for a spin first hand. And today it is finally possible!

<!-- more -->

## Public SR Linux container

I am a firm believer that Network Operating Systems should be available for testing to everybody. The reality, unfortunately, is quite different, with vendors either not allowing you to download virtual NOS at all, or requiring you to have an account, a registration with their system or a license file to run it.

With SR Linux, we are making a big step into the openness by pushing SR Linux container to the [public container registry](https://github.com/orgs/nokia/packages/container/package/srlinux) so everyone can it pull without any registration, payments, or active service accounts. Absolutely free and open.

```bash
docker pull ghcr.io/nokia/srlinux
```

### Running light

Containerized NOSes have a lot of benefits that come from the container packaging. One of them being lightweight compared to the VM-based counterparts.

On average, a single SR Linux container will consume about 0.5vCPU and ~1GB RAM[^2]. That allows you to spin up labs of decent size having only an entry-level VM at your disposal.

For example, one of the most typical labs is a Clos fabric with a few leafs and spines. The lab like that will fit into 2vCPU and 6GB RAM VM.

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:15,&quot;zoom&quot;:1.5,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/srl-wim/container-lab/diagrams/containerlab.drawio&quot;}"></div>

You can even run this lab on a free Github Actions runner, which has 8GB RAM. Imagine the sheer possibilities in writing CI pipelines for testing your DC features which can run in the public cloud for free.

### Full feature parity

When working with virtual networking products one needs to be aware of any limitations the virtual appliance imposes. Quite often the virtual images we work with in labs are crippled both in dataplane and control plane functions.

These limitations of the virtual images make it hard to create a reliable and "real" automated testing pipeline.

<center><blockquote class="twitter-tweet"><p lang="en" dir="ltr">When you say vNOS, do you mean as a separate standalone product or as a virtual version of an image that will be sold to run on hardware only?</p>&mdash; Joe Neville 🌻 (@joeneville_) <a href="https://twitter.com/joeneville_/status/1417855086076760066?ref_src=twsrc%5Etfw">July 21, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></center>

SR Linux container has the same code inside that actually runs on our hardware platforms. There is no control or data plane deviations[^1], so by using this image in your CI pipelines you can be sure that when deployed to production, it will behave the same.

And all that with a small resource footprint. Imagine running a fully functional 3-stage mini-Clos fabric with 6 nodes on a machine with 2vCPU and 6GB RAM? That will fit into a free GitHub runner!

### No license strings attached

Being able to pull SR Linux NOS as any other container image is big on its own, but we also wanted to make sure that you can use right away. To do that, we made licensing optional, so once you pulled an image you can use it to its full extent!

!!!info
    When running without a license users can enjoy all the features of SR Linux, but dataplane interfaces will have a 1000pps throughput limitation and running time is limited by 2 weeks.

### Versioning

We plan to push every public release of SR Linux to the container registry so that you can pull a specific version or the `:latest` one. The SR Linux version is a tag on the container image, so there is an easy way to match a release to its image.

We will keep all versions available for you to pull.

### GitHub container registry

The decision use GitHub container registry was made specifically to allow you to get the image without facing the pull restrictions that Docker has in place.

We do that because we think that one of the very promising applications for public SR Linux container is to use it in CI pipelines. And in CI your jobs can pull the images quite frequently, so having limitations for pulling, is an important improvement.

## Learn SR Linux

SR Linux was designed to answer the needs of today and tomorrow, with a strong focus on automation teams. With that forward-looking design, it is clear that many things will look *new* to the users who worked with traditional Networks OSes in the past.

<center><img src=https://gitlab.com/rdodin/pics/-/wikis/uploads/f1941800bd3dd0c2e45165dc6989a934/learn-srlinux-logo.png/></center>

To help you navigate the SR Linux world, we are launching a community-oriented documentation portal - [learn.srlinux.dev](https://learn.srlinux.dev)

### Learn by doing

The main goal of the portal is to introduce you to the SR Linux by means of the interactive [tutorials](https://learn.srlinux.dev/tutorials/about/). All the tutorials are based on a certain lab scenario that we go through explaining the technology and how SR Linux implements it.

The lab scenarios are deployed with [containerlab](https://containerlab.srlinux.dev) so both the tutorial authors and the readers follow along the same path and can reproduce the whole tutorial.

We start with explaining how to actually [run SR Linux container](https://containerlab.srlinux.dev/quickstart/) and build arbitrary topologies, and then offer you to follow one of the use-cases centric tutorials.

### Not your usual tutorials

One of the objectives for the tutorials that we put on this portal was to make them stand out, and this is achieved with the following:

1. **Backed by runnable labs**  
    As have already been mentioned, every tutorial is actually created using a lab deployed with SR Linux containers. And we share those labs for you to follow along the configuration journey.  
    That is very important to us, because completing a hands-on tutorial beats reading experience every day.

2. **Complete, top-to-bottom explanations**  
    Every tutorial is built from the ground-up, with every step explained and demonstrated. If there are any pre-requisites which needs to be met, we explain how to do that.  
    For example, if there is a routing underlay that we use to deploy overlay services on top, we always explain how this is configured and provide you with config snippets to achieve the same required state.

3. **Control & Data planes verification**
    A large part of the tutorials are dedicated to control plane and data plane verifications. It is not enough to just configure a feature, we want to show you also how to verify that the applied configuration results in a proper control/data plane function.

4. **PCAPs**  
    Yes, where applicable we will also share the PCAP files with control and data plane traffic captured. The truth is always in PCAPs, so by analyzing them we can see how control plane protocols operate and what encapsulations are used in the data plane.

## Always-ON SR Linux

Although it is extremely easy to run SR Linux on your own system, it is always nice to have a system running on the Internet which you can access.

Please welcome, an [**Always ON SR Linux instance**](https://learn.srlinux.dev/alwayson/).

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:1,&quot;zoom&quot;:2,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/learn-srlinux/site/diagrams/alwayson&quot;}"></div>

As the diagram shows, we are exposing every management interface the NOS has for you to explore them.

- The modern-looking CLI is accessible via SSH
- The fully potent gNMI interface is open for everyone to try out getting information with gNMI Get and stream it with gNMI Subscribe
- The third interface - JSON-RPC over HTTP - is a REST API like interface for teams who prefer to deliver automation via it, or those who find gNMI specification limiting.

!!!warning "Be a good citizen"
    Please, act in good faith and do not try to oversubscribe the instance by streaming massive amounts of data. This is a shared instance, and we want everyone to have a good experience with it.

### Pre-configured services

The Always-ON SR Linux instance has a few pre-configured services that you can explore either via CLI, or with other interfaces such as gNMI.

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:0,&quot;zoom&quot;:2,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/learn-srlinux/site/diagrams/alwayson&quot;}"></div>

The pre-configured services are:

1. Layer 2 EVPN with VXLAN dataplane with `mac-vrf-100` network instance
2. Layer 3 EVPN with VXLAN dataplane with `ip-vrf-200` network instance

## SR Linux community

SR Linux has lots to offer to various groups of engineers...

Those with a strong networking background will find themselves at home with proven routing stack SR Linux inherited from Nokia SR OS.

Automation engineers will appreciate the vast automation and programmability options thanks to SR Linux NetOps Development Kit and customizable CLI.

Monitoring-obsessed networkers would be pleased with SR Linux 100% YANG coverage and thus through-and-through gNMI-based telemetry support.

We are happy to chat with you all! And the chosen venue for our new-forming SR Linux Community is the [**SR Linux Discord Server which everyone can join**](https://discord.gg/tZvgjQ6PZf)!

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

[^1]: since dataplane for the SR Linux container is simulated, there are some edge cases where the real dataplane would behave differently, but this is only true for 5% of the overall cases.
[^2]: still, it is required to have at least 4GB RAM VM and preferably >1 vCPU
