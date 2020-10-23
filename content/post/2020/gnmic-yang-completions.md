---
date: 2020-10-22T06:00:00Z
comment_id: gnmic-yang-completions
keywords:
- gnmi
- openconfig
- yang
tags:
- gnmi
- openconfig
- yang

title: gNMIc got better with YANG-completions
---
[`gnmic`](https://gnmic.kmrd.dev) was the first opensource project that I've been part of that got widely adopted. As the maintainers of a public project, Karim and I were wondering when would we get the first external contribution.

To our surprise, the very [first external contribution](https://github.com/karimra/gnmic/pull/136) laid out the foundation to one of the most exciting features of `gnmic` - YANG-Completions.
<!--more-->

I thought that the best way to describe what YANG-completions is showing you a quick demo augmented with some comments. This resulted in this twitter-series:

<center>{{<tweet 1318933113951715334>}}</center>


> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>