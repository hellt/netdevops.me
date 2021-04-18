---
date: 2020-06-28T06:00:00Z
comment_id: gnmi-map
keywords:
- gnmi
- openconfig
tags:
- gnmi
- openconfig

title: gNMI Map
---
Lately I've been involved in project that required quite a deep understanding of OpenConfig gRPC Network Management Interface (gNMI). Going over the [gNMI specification](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md) multiple times made me realize that I can't fully build a mental map of all the messages and encapsulations without having a visual representation of it. So I've made one, lets see what it has to offer.
<!--more-->

[gNMI Map](https://github.com/hellt/gnmi-map) is essentially a visual guide to the [gNMI service](https://github.com/openconfig/gnmi/blob/d19cebf5e7be48e7a6fa9fbdff668d18ad87be9d/proto/gnmi/gnmi.proto#L44).

[![map](https://gitlab.com/rdodin/pics/-/wikis/uploads/6a9d18f9cb2240656aad5d224aa757df/rsz_image.png)](https://gitlab.com/rdodin/pics/-/wikis/uploads/6cf03cf18ae6a9e69fc1360d6c8a0796/gnmi_0.7.0_map.pdf)

It lays out the protobuf data types that compose the gNMI service and provides the references to the relevant sections of the reference guide and code definitions. For example, if you wondered what are the messages the client sends when it needs to query the Capabilites of the remote gNMI target, you can easily zoom into the Capabilities RPC and identify all the messages and types involved in this RPC:

[![cap](https://gitlab.com/rdodin/pics/-/wikis/uploads/65d05f945796da5e2649c82286460b9f/image.png)](https://gitlab.com/rdodin/pics/-/wikis/uploads/65d05f945796da5e2649c82286460b9f/image.png)

The visual connectors help you unwrap the nested messages and collect the whole picture.

Moreover, each message and type "card"0 has a link to a relevant documentation piece of the reference along with the link to its definition in the `gnmi.proto` file:
<p align=center><img src="https://gitlab.com/rdodin/pics/-/wikis/uploads/61e7fa143e5898653c1edb9b42b936f3/image.png" style="width:70%" /></p>

allowing you to quickly jump either to the explanation paragraph of the spec or dive into the proto definition code piece.

Currently the latest gNMI version (0.7.0.) has been "mapped", my intention is to release another map when a new version of the gNMI will be available, keeping the old ones versioned. That will allow having a map for each release after 0.7.0.

The map comes in a PDF format and is stored at https://github.com/hellt/gnmi-map, you can quickly access the latest version with a shortcut: https://bit.ly/gnmi-map.

Happy mapping!

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>