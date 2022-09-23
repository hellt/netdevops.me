---
date: 2020-04-29
comment_id: nokia yang tree
url: nokia-yang-tree
keywords:
- nokia
- sros
- yang
tags:
- nokia
- sros
- yang

title: Nokia YANG tree and Path Browser
---
_Automation Is as Good as the Data Models_ is a chapter's name in the great book titled ["Network Programmability With YANG"](https://www.amazon.com/Network-Programmability-YANG-Modeling-driven-Management/dp/0135180392). These days you won't bedazzle anyone by just providing the set of YANG models for the flagship network products. The models alone, albeit a great step forward, do not guarantee that programmability will start flourish.  
The automation tools leveraging YANG is often a missing link and in this post I am talking about the [Nokia YANG tree and Path Browser](https://github.com/hellt/nokia-yangtree) tools which help both our internal automation squad and our customers to be more effective working with our YANG models.
<!--more-->

## 1 Models for machines

At Nokia we distribute the YANG models via our [nokia/7x50_YangModels](https://github.com/nokia/7x50_YangModels) repository. This enables us to allow users to simplify the way they get the models. The challenge with these models, or any models provided in `.yang` format for that matter, is that its extremely hard for a naked eye to browse/evaluate these models when doing network automation. They are great for compilers, and not as much for us - automation engineers.

```cpp
// first lines of ietf-interfaces.yang module
module ietf-interfaces {
  yang-version 1.1;
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  import ietf-yang-types {
    prefix yang;
  }
  revision 2018-02-20;
  container interfaces {
    description
      "Interface parameters.";
    list interface {
      key "name";
      leaf name {
        type string;
      }
      leaf description {
        type string;
      }
      leaf enabled {
        type boolean;
        default "true";
      }
```

Likely, browsing the [`ietf-interfaces.yang`](https://github.com/YangModels/yang/blob/master/standard/ietf/RFC/ietf-interfaces%402018-02-20.yang) file won't make you sweat, yet it shouldn't led you to a false conclusion that YANG code representation is easy. The reality hits hard when YANG exposes its features such as `groupings` and `uses`, custom `typedefs` and multiple `identityrefs`, solid layer of `XPATH` here and there, twisted `imports` and a composition with dozens of `submodules`.

For example, our combined model for the configuration-only data ([nokia-conf-combined.yang](https://raw.githubusercontent.com/nokia/7x50_YangModels/master/latest_sros_20.2/nokia-combined/nokia-conf-combined.yang)) is 15MB in size and has 331000 lines. That is like the opposite of _easy_. But why is it important to peer inside the models in the first place?

### 1.1 Why browsing models is important?

Truth is that every model driven (MD) interface you have in mind such as NETCONF, gNMI, RESTCONF operates on the data that is modelled in YANG. Thus every single operation you make with these interfaces eventually aligned with the underlying YANG model to access the data.

And unless your automation suite leverages some advanced orchestrator-provided abstractions or code generated classes, you literally **need to look** at the YANG modules when using those management interfaces.

1. NETCONF operations must have the XML envelopes created in conformance with the YANG model ([example](https://gitlab.com/rdodin/pics/-/wikis/uploads/45fd09db73543f94f6937655db3f70ff/image.png))
2. gNMI paths are XPATH-like paths modelled after the underlying YANG model ([example](https://gitlab.com/rdodin/pics/-/wikis/uploads/789429d8fec1d721e04d6024df5f883b/image.png))
3. RESTCONF URL embeds a model path as dictated by the YANG model ([example](https://gitlab.com/rdodin/pics/-/wikis/uploads/1b9d45fd859ee7a66f382bab0f02621c/image.png))

## 2 YANG representations

Make no mistake: regardless of the interface you pick, you end browsing YANG models and as you can imagine, scrambling through the raw YANG model representation is not an easy task. Luckily, the better looking representations of the very same models exist.

### 2.1 Tree

The [RFC8340 YANG tree](https://tools.ietf.org/html/rfc8340) representation is the one you see everywhere in the documentation and blogs. By passing the same `ietf-interfaces.yang` snippet through the `pyang` tool we transform the module to a better looking tree-like view:

```txt
+--rw interfaces
 |  +--rw interface* [name]
 |     +--rw name                        string
 |     +--rw description?                string
 |     +--rw type                        identityref
 |     +--rw enabled?                    boolean
```

Compared to the `.yang` raw view, the _tree_ makes it way easier to glance over the model and understand the parent-child relationships of the data entry nodes and their types.

Still, it has some serious UX drawbacks an engineer will face:

- **the path information is missing.** By looking at a certain leaf/container/list of a tree you can't easily say what is the path of that element starting from the root?  
  Yet it is very important to have this information, since it enables you to create XPATH filters for xCONF or paths to subscribe to with gNMI.
- **it is hard to navigate the large models.** Since its the text file you are looking at, you can't expand/collapse the data nodes on request. Its flushed to you in its entirety, and if the model is big enough you will easily loose the sense of where you are.  
  Consider the following [snippet](https://gist.github.com/hellt/b0496895ae1d2a3323283d35904aa17a) of a single screen of text I captured from a real YANG module; is it easy to understand where are you standing at?

### 2.2 HTML tree

Fortunately for us, `pyang` supports many output formats and one of them - `jstree` - is a mix of the model's tree structure with HTML features. The outcome of this mixture is the self-contained, offline HTML page that crosses off the drawbacks outlined in the previous section.

<div align="center">
    <img style="width:65%" src="https://gitlab.com/rdodin/pics/-/wikis/uploads/5f76c41d72bfd320851518848d1ce7c7/image.png" />
</div>

In this mode we are having the full control on which part of the model we want to explore and which branches we want to leave collapsed to not clutter the view. This might sound like a small thing, but actually it boosts the user experience quite substantially.

Another improvement over the textual tree view is the path information that is provided for each element of the model. As explained above, these paths are essential to have for the following reasons:

- understand the parental path of the element of interest to, say, create the NETCONF XML envelope.
- use these paths in gNMI subscribe paths.
- use these paths with the tools that can generate data based on it (like [XML skeleton](https://netdevops.me/2020/getting-xml-data-sample-for-a-given-leaf-in-a-yang-model/)).

And HTML tree delivers on that promise by providing the path information for every element:
![tree2](https://gitlab.com/rdodin/pics/-/wikis/uploads/fefdc0a777450c42f2ed21fa3e1d568d/image.png)

Its does not really strike like a needed feature when you have a compact module like ietf-interface, but consider a heavier model where a certain leaf is sometimes 10 levels deep from the root:

<a href="https://gitlab.com/rdodin/pics/-/wikis/uploads/81312ae9d876853114df12f06276aeb4/image.png"><img src="https://gitlab.com/rdodin/pics/-/wikis/uploads/81312ae9d876853114df12f06276aeb4/image.png"></a>

On a model like this its dead obvious that a textual tree won't be of help due to the progressively increased nesting of the elements, thus "HTML tree" seems like a reasonable _view_ to use.

## 3 Nokia YANG tree repository

Nokia distributes the YANG models for 7x50 routers in two forms:

- **combined models:** all the submodules are grouped under the respective top level roots and the following [combined](https://github.com/nokia/7x50_YangModels/tree/sros_20.2.r2/YANG/nokia-combined) YANG modules are produced: `nokia-conf-combined.yang` and `nokia-state-combined.yang`
- **individual models:** the submodules are kept in their own YANG files.

The combined modules provide a unique one-stop shop for the `configuration` and `state` YANG view, therefore I always use the combined models as they have all the elements nicely grouped under a single root.

Due to the substantial size of the combined models it takes quite some time for `pyang` to generate the tree views; I quickly got tired of generating the tree views for each new minor release of SR OS myself. So I decided to generate them automatically for each new set of YANG modules Nokia pushes to the [nokia/7x50_YangModels](https://github.com/nokia/7x50_YangModels) repo.

That is how [hellt/nokia-yangtree](https://github.com/hellt/nokia-yangtree) repo was born. The repository features:

1. various _views_ of the Nokia combined YANG models (text tree, xml, html tree) as well as stores the XPATH paths extracted from the models. A user can clone the repo and gain access to all of these formats
2. [**YANG Browser**](#31-yang-browser) that serves the "HTML tree" views of the combined models so that our users could consume these models online without a need to generate them
3. [**Path Browser**](#32-path-browser) that enables search functionality over the extracted model paths

<div align="center">
    <img style="width:70%" src="https://gitlab.com/rdodin/pics/-/wikis/uploads/b49f71395d2ed2e2f17d6a31d7ddd4a9/image.png" />
    <small><i>repository directory layout</i></small>
</div>

The repo navigation is built on the basis of Git tags, that means that a certain set of YANG views will be shown to a user when they select a certain tag that matches the SR OS release number:

<div align="center">
    <img style="width:90%" src="https://gitlab.com/rdodin/pics/-/wikis/uploads/8e9e7582ff6b90fef02c9fd529d84303/CleanShot_2020-05-19_at_14.28.31.gif" />
</div>

### 3.1 YANG Browser

As briefly explained before, the YANG Browser is merely an HTTP server that serves the HTML tree views of the combined models generated with `pyang`. I foresee this to be the main interface for the SR OS automation engineers to consume the YANG models, it is always available, easy to navigate, free and requires just a browser.

How YANG Browser works:

1. A user selects an SR OS release as shown in animation above
2. Once the release is selected the `HTML tree` links in the [section 2](https://github.com/hellt/nokia-yangtree#2-yang-browser) for the relevant datastores will point to the right URLs.
3. Clicking on a link will open a new tab with the HTML Tree view (note, it might take a few minutes to a browser to load and render this big HTML file).

<div align="center">
    <img style="width:90%" src="https://gitlab.com/rdodin/pics/-/wikis/uploads/ad013fddf9a02ee430c5b5d3a69670ff/image.png" />
    <small><i>HTML tree view for the <code>nokia-state-combined</code> module</i></small>
</div>

Using this page a user can answer most of the questions related to the YANG modules used by the Nokia 7750 router.

The always on HTML tree view is amazing, but it still has some flaws. One particular case that can't be solved with YANG Browser is filtering the model's paths with a keyword. To answer that request we created the **Path Browser**.

### 3.2 Path Browser

Imagine a request comes in asking to identify all the leaves that relate to the alarm status of the port/chassis/fan/optics/etc. Quite a standard task for every monitoring activity, which is not easy to answer without the proper tooling.

How would you use a YANG Browser if you don't know which containers have or haven't the alarm related leaves inside? Opening all of them will become a nightmare, as well as expanding all the elements and perform a full-text search. What would be nice to have is a search actions on the paths that have some keywords inside them, like _alarm_.

For that particular set of the use cases we created the Path Browser.

> The Path Browser links are in the [section 2](https://github.com/hellt/nokia-yangtree#2-yang-browser) of the repo readme.

First, my colleague wrote a tool that extracts a list of XPATH compatible paths for a given model. The text file with the list of paths is part of the [hellt/nokia-yangtree](https://github.com/hellt/nokia-yangtree) repo.

```
$ head -10 sros_20.2.r2-nokia-state-combined-paths.txt
nokia-state | /state/aaa/radius/statistics/coa/dropped/bad-authentication | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/dropped/missing-auth-policy | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/dropped/invalid | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/dropped/missing-resource | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/received | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/accepted | yang:counter32
nokia-state | /state/aaa/radius/statistics/coa/rejected | yang:counter32
nokia-state | /state/aaa/radius/statistics/disconnect-messages/dropped/bad-authentication | yang:counter32
nokia-state | /state/aaa/radius/statistics/disconnect-messages/dropped/missing-auth-policy | yang:counter32
nokia-state | /state/aaa/radius/statistics/disconnect-messages/dropped/invalid | yang:counter32
```

The format of the path entries follows the pattern of `module_name | path | type`. And having this file alone allows you to leverage CLI tools magic to filter on this massive data set:

```bash
$ grep "/port.*alarm" sros_20.2.r2-nokia-state-combined-paths.txt | head -5
nokia-state | /state/port[port-id=*]/transceiver/digital-diagnostic-monitoring/temperature/high-alarm | decimal64
nokia-state | /state/port[port-id=*]/transceiver/digital-diagnostic-monitoring/temperature/low-alarm | decimal64
nokia-state | /state/port[port-id=*]/transceiver/digital-diagnostic-monitoring/transmit-bias-current/high-alarm | decimal64
nokia-state | /state/port[port-id=*]/transceiver/digital-diagnostic-monitoring/transmit-bias-current/low-alarm | decimal64
nokia-state | /state/port[port-id=*]/transceiver/digital-diagnostic-monitoring/transmit-output-power/high-alarm | decimal64
```

> The paths are XPATH and gNMI compatible. You can paste it to the telemetry collector and they would work.

The next step was to build a web service with the same functionality, so I added [datatables](https://datatables.net/) to the mix and generated the HTML pages with the filtering capabilities built-in.

<div align="center">
    <img style="width:100%" src="https://gitlab.com/rdodin/pics/-/wikis/uploads/14fcedd12a511674a1ff8829ab28390f/CleanShot_2020-05-19_at_17.37.55.gif" />
</div>

With a service like that you can efficiently and plain easy search through the Nokia modules for the leaves having certain keywords.

## 4 Summary

By leveraging the opensource tools and by writing our own paths extractor we have created a DIY YANG browsing set of instruments that greatly help network automation engineers working with Nokia gear. Understanding the utter importance of YANG, it was imperative for me to make these models more convenient to consume and, at the same time, keeping it open and free.

As a result of that effort, the community now can use [YANG Browser](#31-yang-browser) to breeze through the Nokia YANG modules and [Path Browser](#32-path-browser) comes to help when the users need to perform a search for the certain leaves.
