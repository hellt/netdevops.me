---
date: 2020-07-08T07:00:00Z
comment_id: gnmic
keywords:
- gnmi
- openconfig
- go

tags:
- gnmi
- openconfig
- go

title: gNMIc - gNMI CLI client and collector
---
Despite the fact that [gNMI](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md) is defacto the go-to interface for a model-driven telemetry collection, we, as a community, had no gNMI tool that was easy to install, pleasure to use, documented and pre-built for common platforms. Until now.

I am excited to announce the public release of [`gnmic`](https://gnmic.kmrd.dev/) - a CLI client and a collector that talks gNMI to your devices.
<!--more-->

### Problem statement
I am not exaggerating, there is a shortage of open source gNMI clients one can find. And when I say gNMI clients I mean the CLI clients that allow you to invoke gNMI service RPCs.

Earlier this year I bragged about it, in hope that my google-foo is just broken and the community knows of a gNMI client that I could download and use right away without jumping through hoops:

<center>{{< tweet 1229845496660922368>}}</center>

But that was not my google-foo, unfortunately. For the sake of completeness allow me to summarize the landscape of gNMI clients in a pre-gnmic era:

* [OpenConfig gNMI CLI client](https://github.com/openconfig/gnmi) - thats the google search top result one gets when looking for gNMI client. A reference implementation which lacks some essential features:
    * no documentation, no [usage examples](https://github.com/openconfig/gnmi/issues/7) - you really better know how to read Go code to understand how to use it.
    * Get requests will require you to [write in proto](https://github.com/openconfig/gnmi/issues/67) syntax instead of a simple `get` command with a path.
    * additional options like Encoding, Models are not exposed via flags.
    * no ready-made binaries - you need to have a Go tool chain to build the tool.
    * no _insecure_ support - you can kiss goodbye your lab installations without PKI.
* [Google gnxi](https://github.com/google/gnxi) - Googles gNxI tools that include gNMI, gNOI.
    * the gNMI RPCs are split to different CLI tools which is not convenient
    * a list of flags is all you got when it comes to documentation
    * no releases to download, Go toolchain is needed
* [cisco-gnmi-python](https://github.com/cisco-ie/cisco-gnmi-python#cli-usage) - a Cisco Innovative Edge project that is quite decent and complete, good job! But a few improvements could have been made:
    * client doesn't allow to use insecure gRPC transport, PKI is mandatory.
    * Set requests can't set values specified on the command line.
    * CLI structure is not consistent across the commands
    * No option exposed to set the Subscription mode.
* [Telegraf](https://github.com/influxdata/telegraf) and [Ansible gNMI module](https://github.com/nokia/ansible-networking-collections/tree/master/grpc) are not qualified to be considered as CLI tools.

### What makes gNMI tool nice to use?

Looking at this landscape, the following essential features a nice gNMI client should have come to mind:

* provide a clean and vendor independent interface to gNMI RPCs
* expose all configuration options the gNMI RPCs have via flags or file-based configurations
* allow multi-target operations: i.e. a subscription made to a number of the devices
* implement both TLS enabled and non-secure transport
* support different output formats (JSON, proto) and destinations (stdout, file, streaming/messaging buses)
* be documented
* provide an easy way to install the tool without requiring a dev toolchain to be present.

With these essential features in mind we started to work on [gnmic](https://gnmic.kmrd.dev/).

### gNMIc and its features
<p align=center><img src=https://gitlab.com/rdodin/pics/-/wikis/uploads/46e7d1631bd5569e9bf289be9dfa3812/gnmic-headline.svg?sanitize=true/></p>

The work on `gnmic` started with analysis of the existing tools shortcomings coupled with collecting requirements from our fellow engineers and our past user experience.

> For the `gnmic` features run down go to our beautiful documentation portal - https://gnmic.kmrd.dev. In this post I will go a bit deeper on some core features and design choices we made, so please refer to the documentation if you are looking for a basic usage or command reference guide.

#### Consistent command line interface
It is easy to spot a CLI tool that got some love from its developers by looking at the way it is composed. Since most of the `gnmic` users will use it as a CLI tool we took an extra step and wrote it with a [Cobra](https://github.com/spf13/cobra) framework that adds a great layer of consistency to the command line applications.

With Cobra `gnmic` gets extra powers such as consistent global and local flags, multi-tiered subcommands, auto-generated and accurate help and overall a "proper" CLI behavior.

```text
$ gnmic get --help
run gnmi get on targets

Usage:
  gnmic get [flags]

Flags:
  -h, --help            help for get
      --model strings   get request model(s)
      --path strings    get request paths
      --prefix string   get request prefix
  -t, --type string     the type of data that is requested from the target. one of: ALL, CONFIG, STATE, OPERATIONAL (default "ALL")

Global Flags:
  -a, --address strings             comma separated gnmi targets addresses
      --config string               config file (default is $HOME/gnmic.yaml)
  -d, --debug                       debug mode
  -e, --encoding string             one of [json bytes proto ascii json_ietf]. Case insensitive (default "json")
```

#### Alignment to gNMI specification
For a tool to be generic it must not deviate from a reference specification. Adhering to that promise, we made `gnmic` commands modelled strictly after the gNMI RPCs. Each RPC has a command with a clear and concise name, and each command's flags are named after the fields of the corresponding proto message. No ambiguous flag names or questionable subcommands, it is clear and guessable what each command and flag does without looking at the documentation:

```text
$ gnmic -h
<snipped>

Available Commands:
  capabilities query targets gnmi capabilities
  get          run gnmi get on targets
  help         Help about any command
  listen       listens for telemetry dialout updates from the node
  path         generate gnmi or xpath style from yang file
  set          run gnmi set on targets
  subscribe    subscribe to gnmi updates on targets
  version      show gnmic version

<snipped>
```

Moreover, we tried to expose every configuration knob gNMI specification has to offer. Again, a generic tool should not limit your capabilities, so if you want to, say, restrict the YANG models the gNMI target should use when replying back to the client - there is a [flag](https://gnmic.kmrd.dev/cmd/get/#model) for that!

#### TLS and non-TLS transports
We allowed ourselves to step away from the specification to add one additional generic purpose feature - a [insecure](https://gnmic.kmrd.dev/global_flags/#insecure) transport fo gRPC connection.

The need for the non-secured connections is quite reasonable, its cumbersome in many cases to deal with certificates and keys generation if all one is up to is a quick gNMI test.

```text
gnmic -a 10.1.0.11:57400 -u admin -p admin --insecure capabilities
gNMI_Version: 0.7.0
supported models:
  - nokia-conf, Nokia, 19.10.R2
  - nokia-state, Nokia, 19.10.R2
  - nokia-li-state, Nokia, 19.10.R2
  - nokia-li-conf, Nokia, 19.10.R2
<< SNIPPED >>
supported encodings:
  - JSON
  - BYTES
```

#### Flexible configuration options
Due to a sheer amount of configuration options `gnmic` has, it can sometimes be tedious to specify all of them as CLI flags. For such cases we leveraged [viper](https://github.com/spf13/viper) and added support for [file-based configuration](https://gnmic.kmrd.dev/advanced/file_cfg/) that is consistent with both local and global flags. Its up to a user to choose the configuration file format: YAML, JSON, HCL - all are welcome!

```yml
$ cat ~/gnmic.yml
address: "10.0.0.1:57400"
username: admin
password: admin
insecure: true
```
```bash
# now gnmic can read this cfg file and get the params from it
$ gnmi get --path /configure/system/name
```

#### Automation friendly output
Its quite common to use gnmic in a setting where the output it provides is used as an input to another command. The simple example is getting something out of the network element and processing the result with some other tool.

Keeping that case in mind we modelled gnmic output to default to JSON format, so that you can quickly `jq` the results out and feed it to other tools or processes.

```json
gnmic -a 10.1.0.11:57400 -u admin -p admin --insecure \
      get --path /state/system/platform

{
  "source": "10.1.0.11:57400",
  "timestamp": 1592829586901061761,
  "time": "2020-06-22T14:39:46.901061761+02:00",
  "updates": [
    {
      "Path": "state/system/platform",
      "values": {
        "state/system/platform": "7750 SR-1s"
      }
    }
  ]
}
```

#### Multiple subscriptions
To expand on `gnmic` subscription capabilities and not limiting users to a single subscription per target we added a way to decouple subscriptions from the targets. The [Multiple subscriptions](https://gnmic.kmrd.dev/advanced/subscriptions/) feature allows to defined as many subscriptions as needed and later associate them to the targets:

```yaml
targets:
  router1.lab.com:
    subscriptions:
      - port_stats
      - service_state
  router2.lab.com:
    subscriptions:
      - service_state
username: admin
password: nokiasr0s
insecure: true

subscriptions:
  port_stats:
    paths:
      - "/state/port[port-id=1/1/c1/1]/statistics/out-octets"
      - "/state/port[port-id=1/1/c1/1]/statistics/in-octets"
    stream-mode: sample
    sample-interval: 5s
  service_state:
    paths:
       - "/state/service/vpls[service-name=*]/oper-state"
       - "/state/service/vprn[service-name=*]/oper-state"
    stream-mode: on-change
```

With this approach subscriptions stay decoupled from the targets, while being fully configurable.

#### Documentation
Writing documentation is hard, but it felt necessary to provide a full-blown [documentation portal](https://gnmic.kmrd.dev) with basic usage, command reference and advanced use cases examples.

Knowing how problematic it might be for a novice to get started with gNMI, we added a lot of examples to each command `gnmic` has. The documentation portal is built with [mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme and is open, so you can request additions or contribute via [issues](https://gitlab.com/kmrdi/gnmiclient-docs).

#### Distribution via binaries
Not only having documentation is an essential step to break the steep entry barrier, but also the installation process in our opinion must be welcoming and inclusive.

Being written in Go, `gnmic` is distributed as a single binary built for most common architectures and OSes. Our single-command [installation script](https://gnmic.kmrd.dev/install/) makes it extremely easy to install or upgrade.

```
curl -sL https://github.com/karimra/gnmic/raw/master/install.sh | sudo bash
```

### Summary
At the end of the day, I tend to believe that `gnmic` will successfully fill the void of standalone gNMI tools available to the public. Starting from a consistent CLI layer with all the gNMI RPCs nicely exposed and finishing with the proper docs and easy installation it checks all the marks I had in mind for a decent gNMI client, and hope it will be to community's satisfaction as well.

Oh, and `gnmic` also has [collection capabilities](https://gnmic.kmrd.dev/advanced/multi_outputs/output_intro/) allowing you to export the metrics collected via gNMI to Kafka, NATS, Influx, Prometheus. But that is for another post.

### Authors
The team behind `gnmic` consists of [Karim Radhouani](https://github.com/karimra) and [Roman Dodin](https://twitter.com/ntdvps), but we are welcome contributors of all sorts. Be it code, documentation, bug reports or feature requests!

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>