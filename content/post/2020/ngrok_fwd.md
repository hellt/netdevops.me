---
date: 2020-04-25T06:00:00Z
comment_id: ngrok_fwd
keywords:
- ngrok
- fwd
- gnmi
- grpc
- netconf
- ssh
tags:
- ngrok
- fwd
- gnmi
- grpc
- netconf
- ssh

title: Easily exposing your local resources with ngrok and fwd
---
I bet every one of you was in a situation when you bloody needed to expose some local resource over internet. Letting a remote colleague to look at your work, delivering a demo being off-VPN, or any other reason to have your service be reachable over Internet.

And it was never easy; corporate firewalls stand on-guard ensuring you can't be agile and productive 😉

In this post I'll share with you how I glue [`ngrok`](https://ngrok.io) and [`fwd`](https://github.com/kintoandar/fwd) tools together to make my routers management interfaces exposed over Internet in a few clicks for free.
<!--more-->

My story will be based on the following "network-automation engineer's" requirement:

1. Make router's management interfaces available over internet (SSH, Netconf, gNMI)
2. Make this "exposure" process quick to set up/tear down
3. Make it free of charge

> In my case I am talking about management interfaces of a router, but it can be any application that relies on TCP/UDP transport that you can expose that way.

By the end of this post you will see that we deliver on all of these requirements.

## You shall (not) pass
You have a router with these shiny management interfaces. But this poor thing is so locked up...

![locked](https://gitlab.com/rdodin/pics/-/wikis/uploads/a14cab59b1e2f965a6ad256a1809da42/image.png)

Most of the times there are zero chances you can configure ingress access due to the myriads of elements out of your control (corp firewall being the most tricky one).

There might even not be any EVE-NG or Openstack in the picture, but this BFF9000 fella will be there, and we are about to penetrate it.

## Enter ngrok
Since opening the ports or configuring the port forwarding is not gonna help us much, we will use the reverse technique: opening the connections in the egress direction. Sending traffic in the egress direction is usually not a problem, we can leverage [ngrok](https://ngrok.io) and expose the needed ports through it:

![ngrok](https://gitlab.com/rdodin/pics/-/wikis/uploads/61cae41c73bb0878f0ca784e0375d145/image.png)

> If you never heard of `ngrok`, I suggest you go through their [website](https://ngrok.io), its a very powerful tool to setup tunnels.

That way we can expose any TCP/UDP port of a machine that runs `ngrok` client via publicly accessible sockets (`tcp://xx.ngrok.io:<port>`) for free.

That looks like a nice idea and quite a realistic one, but not that many routers allow users to install ELF binaries and run them. This means that we can't run `ngrok` client on the router itself and establish tunnels.

But we can definitely install ngrok on a machine that can reach our routers. In my case that will be the EVE-NG hypervisor/VM, since it can reach all the routers that run inside of it.

## Enter fwd
Since `ngrok` is only capable of exposing the ports of the host the client runs on, we would end up with ports of the Linux host exposed, but not the router's. The missing piece is the forwarder process that will stitch the `ngrok`-exposed ports of the linux host with the respective ports of the remote router.

![fwd](https://gitlab.com/rdodin/pics/-/wikis/uploads/66790fdb54115b1ae1bc364821098345/image.png)

Let's dissect this two stage process of setting the tunnels up:

1. expose the local ports of the linux VM with `ngrok`. This linux VM can reach the router.
2. run `fwd` tool that will forward the traffic appearing on the local ports we exposed with `ngrok` in step 1

That way we bridge the linux ports exposed with `ngrok` with the ports on the router. If that sounds confusing, lets go through the example.

## socat vs fwd
If you (as me) will experience some issues with `fwd` reporting broken pipes there is an old-school alternative - `socat`. As with `fwd`, you can concatenate connections in the following way:
```bash
# requests coming to localhost:11122 will be forwarded to 10.2.0.11:22
socat tcp-listen:11122,reuseaddr,fork tcp:10.2.0.11:22
```

## Practical example
We start first with exposing the ports of the machine that runs `ngrok` client and has IP reachability with our router. To expose multiple ports in a quick and easy way, I suggest you leverage the `ngrok` configuration file which can resemble smth like this:

```yml
# cat ngrok.cfg
authtoken: "MYTOKEN"
log_level: warn
log: /tmp/ngrok.log
region: eu
tunnels:
  gnmi_r1:
    addr: 57401
    proto: tcp
  nc_r1:
    addr: 11831
    proto: tcp
  ssh_r1:
    addr: 11122
    proto: tcp
```

With this configuration we command `ngrok` to expose the TCP ports `57401, 831, 11122` on the linux VM.

```bash
ngrok start -config ngrok_cfg.cfg --all
```

And voilá, these ports are now Internet-reachable:
```text
ngrok by @inconshreveable

Session Status                online
Account                       cats_admin (Plan: Free)
Version                       2.3.35
Region                        Europe (eu)
Web Interface                 http://127.0.0.1:4040
Forwarding                    tcp://0.tcp.eu.ngrok.io:13621 -> localhost:11831
Forwarding                    tcp://0.tcp.eu.ngrok.io:16704 -> localhost:57401
Forwarding                    tcp://0.tcp.eu.ngrok.io:19968 -> localhost:11122

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

But this won't work yet as we wanted.

```bash
ssh -p 19968 admin@0.tcp.eu.ngrok.io
ssh_exchange_identification: Connection closed by remote host
```

As we clarified before, nothing listens on these ports, since they are not of router' but of the linux machine running `ngrok` client.

There is one step left. Start the `fwd` processes and stitch the local ports with the router' ports. Since `fwd` cant read (yet) the configuration file, I created a dumb script:
```bash
fwd --from localhost:57401 --to 10.1.0.11:57400 &
fwd --from localhost:11831 --to 10.1.0.11:830 &
fwd --from localhost:11122 --to 10.1.0.11:22 &
```

Thats the missing piece to propagate our tunnels all the way to the router with IP address of `10.1.0.11` in my example. And now we're in business!

**ssh:**
```text
$ ssh -p 19968 admin@0.tcp.eu.ngrok.io

admin@0.tcp.eu.ngrok.io's password:

 SR OS Software
 Copyright (c) Nokia 2019.  All Rights Reserved.
[]
A:admin@R1#
```

**netconf:**
```
$ ssh -p 13621 admin@0.tcp.eu.ngrok.io -s netconf

admin@0.tcp.eu.ngrok.io's password:
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:netconf:base:1.1</capability>
```

**gNMI:**
```
$ myAwesomegNMIClient -a 0.tcp.ngrok.io:16704 -u admin -p admin --insecure cap
gNMI_Version: 0.7.0
supported models:
  - nokia-conf, Nokia, 19.10.R2
  - nokia-state, Nokia, 19.10.R2
  - nokia-li-state, Nokia, 19.10.R2
  - nokia-li-conf, Nokia, 19.10.R2
```

Now to stop this we simply kill the `fwd` processes and ngrok:
```
pkill fwd && pkill ngrok
```

## Summary

* With `ngrok` and `fwd` we have been able to expose the local router' ports with two clicks in the terminal.
* The tunnels are persistent and free to use.
* Tear down process is as simple as `pkill fwd && pkill ngrok`
* you can monitor established tunnels with ngrok console (free)
* you can try inlets or argo tunnels for similar capabilities

What are your ways to reach your routers in a lab, share in the comments?

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>
<a href="https://www.buymeacoffee.com/ntdvps" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/lato-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>