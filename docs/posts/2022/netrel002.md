---
date: 2022-01-26T06:00:00Z
comment_id: netrel002
keywords:
  - netrel
  - yang
tags:
  - netrel
  - yang

title: DIY YANG Browser
---

Here comes the second episode of the NetRel show: **NetRel episode 002 - DIY YANG Browser**. Be ready to dive into the paths we took to create a [YANG Browser for Nokia SR Linux platform](https://yang.srlinux.dev).

{{< youtube _d4hL7I2h1w >}}

YANG data models are the map one should use when looking for their way to configure or retrieve any data on SR Linux system. A central role that is given to YANG in SR Linux demands a convenient interface to browse, search through, and process these data models.

To answer these demands, we created a web portal - https://yang.srlinux.dev - it offers:

- Fast Path Browser to effectively search through thousands of available YANG paths
- Beautiful Tree Browser to navigate the tree representation of the entire YANG data model of SR Linux
- Source `.yang` files neatly stored in nokia/srlinux-yang-models repository for programmatic access and code generation