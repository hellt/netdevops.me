---
date: 2022-10-04
comments: true
tags:
  - gnmic
  - gnmi
  - openconfig
---

# gNMIc joins Openconfig 🚀

Two years ago, a dozen contributors less, 400 Pull Requests, and 2000 commits behind, another pet project appeared on a vast GitHub landscape. It was a learning exercise by [Karim Radhouani][karim-github] to sharpen his skills in [gNMI][gnmi-ref] - a niche network management protocol promoted by the [Openconfig][oc] group.

Initially named `gnmi_client`, it had a noble but narrow scope of providing a feature-rich, complete, yet intuitive CLI for gNMI-enabled routers. Fast forward two years, and we have the [**gNMIc**][gnmic-main-site] software suite that **is much more than just a CLI** for gNMI.

<div class="img-shadow">
<video width="100%" autoplay muted loop controls><source src="https://gitlab.com/rdodin/pics/-/wikis/uploads/d3a08c2f03c2d15db2074967e4ef268f/gnmic-oc.mp4" type="video/mp4"></video>
</div>

Today, Nokia donates the gNMIc project to Openconfig, and with that move, we expect to see gNMIc adopted by even more companies and organizations :partying_face:

<div class="grid cards" markdown>

- :material-home:{ .lg .middle } **gNMIc new address**

    ---

    :material-github: [openconfig/gnmic][gnmic-repo]

    :material-book: [https://gnmic.openconfig.net][gnmic-main-site]

</div>

In this post I'd like to give you a brief overview of gNMIc's core features and share my thoughts on what we expect to happen with gNMIc moving under the Openconfig's wing.

<!-- more -->

Over the past two years, gNMIc became a feature-rich gNMI-focused software suite. Both its CLI and collection capabilities matured with lots of new integrations added. Moreover, gNMIc had quite some air time in production networks, not to mention lab deployments and dev testbeds.

I would like to briefly highlight gNMIc's current feature set for those who aren't familiar with it yet. Broadly, we split gNMIc capabilities into the following three domains:

- CLI
- Collector
- API

!!!note
    Each of those domain areas packs a hefty number of neat features, and I will only highlight some of them to keep the introduction short and sweet.

    gNMIc cherishes documentation; readers are encouraged to follow the links provided in this post to get more information on particular topics.

<p markdown align=center>![logo](https://gitlab.com/rdodin/pics/-/wikis/uploads/46e7d1631bd5569e9bf289be9dfa3812/gnmic-headline.svg?sanitize=true#only-light)
![logo](https://gitlab.com/rdodin/pics/-/wikis/uploads/f54d2cfdde13193cedab7b60203a2a9a/gnmic-headline-for-dark-bg.svg?sanitize=true#only-dark)
</p>

## CLI

gNMIc provides an intuitive yet full-featured CLI for interacting with gNMI-capable targets. It fully implements [gNMI v0.7+ specification][gnmi-ref] with extensions[^1], and with the move under Openconfig, it becomes a standard gNMI CLI tool.

In 2020 I [wrote about gNMIc](../2020/gnmic.md) highlighting its CLI capabilities. Since then CLI side of gNMIc has only become better with the following changes:

- Added [template-based payloads][template-set] to simplify complex and data-driven configuration use cases.
- [GetSet command][getset-cmd] introduced to allow conditional execution of a Set RPC based on a received Get response.
- Implemented [`diff` command][diff-cmd] to compare configurations between two different targets and identify configuration drift.
- Added [`prompt` mode][prompt-cmd] for a guided CLI experience.
- Added [generation of paths][path-gen] out of the YANG modules.
- Support configuration via any of the following methods: CLI flags, environment variables, or file.
- Integrated prototext and protojson output options to display raw requests and responses.

!!!tip "gNMIc CLI"
    Easy one-click installation, multi-arch/multi-OS hermetic binary, full feature parity with gNMI spec and intuitive commands layout make `gnmic` tool a perfect choice for the task.

[[[ header_divider ]]]

## Collector

Having a great CLI was just the beginning; the lion's share of changes happened in the collector area of gNMIc.

![collector](https://gitlab.com/rdodin/pics/-/wikis/uploads/9f535d6b64cc5794d995104e37a8c04a/image.png){: class="img-shadow"}  
<center><small>gNMIc as a collector in a typical open-source streaming telemetry deployment</small></center>

With the growing interest in Streaming Telemetry, we saw an opportunity to create an open-source telemetry collector to meet the demand. Not just _a collector_, but the open-source collector that can survive a production deployment with all its requirements. I'd like to believe that gNMIc succeeded in delivering on that promise.

Given the central piece that collection capabilities take in gNMIc, it makes sense to spend some additional time on collector's core components.

### Clustering

Streaming Telemetry is often perceived as glorified monitoring that can tolerate outages. Not really, no.

Modern telemetry systems are essential for observability, diagnostics and starting to play a vital role in network automation; Because of that importance, an outage is undesired and should be avoided. For that reason, a Streaming Telemetry collector needs to support High Availability and resiliency.

![clustering](https://gitlab.com/rdodin/pics/-/wikis/uploads/35bb5adedc647ef532aaa09584008af1/image.png)

gNMIc comes with automatic [cluster formation][clustering] routines that enable [**high availability**][ha], [**scaling**][scaling], and [**target redistribution**][target-distrib].

A cluster of gNMIc instances distributes the load by locking the targets to certain instances of the cluster. When the cluster is healthy and operational, targets are assigned to specific gNMIc nodes; in the case of a gNMIc node failure, its targets are going to be moved to a healthy gNMIc node.

![load-balancing](https://gitlab.com/rdodin/pics/-/wikis/uploads/13a2add813af9896deeba7e01b99bfe5/image.png){: class="img-shadow"}
<center><small>A view on Consul service key/value store with targets distributed across gNMIc instances</small></center>

### Target loaders

Adding gNMI targets to the config file works as long as the number of targets stays reasonable and constant. More often than not, in production deployments, the number of targets is quite large. And what is even more critical, targets are being added/removed over time.  
Consequently, it is desirable for a controller to be able to discover and load targets automatically.

gNMIc supports the [dynamic loading of gNMI targets][target-load] from external systems and services. This feature allows adding and deleting gNMI targets without the need to restart gnmic.

<center>![fileloader](https://gitlab.com/rdodin/pics/-/wikis/uploads/9aa7cfdeb42ec808dd88960d39af5664/image.png){: style="width:500px"}</center>

Targets can be loaded from the following sources:

- [file:][file-loader] watch for the changes done to a local file containing gNMI targets definitions.
- [consul:][consul-loader] read targets registered in the Consul service registry.
- [docker:][docker-loader] retrieve available targets using Docker API.
- [http:][http-loader] read target definition from an HTTP server.

### Processors

No collection service can live without a data processing pipeline. Data that the users typically collect from the network elements often requires some processing before it can be stored in a database.

<div class="img-shadow">
<video width="100%" autoplay muted loop controls><source src="https://gitlab.com/rdodin/pics/-/wikis/uploads/ed1b92e82c436a7d942da9f90825a7f4/2022-10-06_12-09-43.mp4" type="video/mp4"></video>
</div>

Let's have a look at a few examples where processing is mandatory:

- **Units normalization/conversion**: in a multivendor network it may be needed to normalize units for, say, utilization rate, from various vendors to a common unit. MB, KB to Bytes, or various time formats to a common epoch time or datetime format.
- **Filtering metrics**: when dealing with a wildcard-based subscription, a collector may receive more data than needed. To optimize for space in the database, processors can be used to allow/drop the needed metrics and give you control over what is going to be written to it.
- **Data conversion**: depending on the telemetry encoding or vendor's implementation, a collector might receive data in a string format, while it needs to be an integer. A conversion processor can automatically convert such metrics so that users can run operations on them in the database.
- **Tag extraction**: For certain metrics collected via gNMI, users may need to extract specific values and promote them to metric's tags to enable a nice layout in the database.

gNMIc employs a large [set of processors][processors] that can help you transform and shape your data the way you need it. Processors can form processing pipelines and be associated with any configured output to enable flexible data pipelines.

| [Processors][processors] |           |                  |              |             |
| ------------------------ | --------- | ---------------- | ------------ | ----------- |
| Add Tag                  | Allow     | Convert          | Data Convert | Date String |
| Delete                   | Drop      | Duration Convert | Extract Tags | Group By    |
| Jq                       | Merge     | Override TS      | Strings      | To Tag      |
| Trigger                  | Value Tag | Write            |              |             |

Processors become invaluable when Streaming Telemetry leaves the lab's sandbox and gets applied in production where dragons lie.

### Outputs

A Streaming Telemetry typically doesn't store collected data; instead, it pushes the collected and processed data to an output, such as a Time Series Database (TSDB), a message bus, or a file.

Various supported outputs make a streaming telemetry collector versatile because it can be deployed in different data pipelines. gNMIc supports a solid [number of outputs][outputs] categorized as databases, message queues, and files.

![outputs](https://gitlab.com/rdodin/pics/-/wikis/uploads/544494827edd88215fef9c0831afd4e9/image.png)

Most popular and used [outputs][outputs] are already supported by gNMIc:

- **Time Series Databases**
    - InfluxDB
    - Prometheus (pull and remote write models)
    - and others working with Prometheus or Influx wire protocols.
- **Message queues**
    - NATS
    - STAN
    - Kafka
- **Raw outputs**
    - TCP, UDP (for example in conjunction with ElasticSearch database)

With a powerful concept of multiple outputs, users can write their metrics to different data stores and create advanced data pipelines.

### Inputs

Complex telemetry pipelines might be built using gNMIc's concept of [inputs][inputs]. With inputs, gNMIc is able to receive gNMI data not from an end-device such as a router but from another gNMIc instance.

This powerful technique enables users to build [a distributed cluster of gNMIc][distrib-cluster] collectors that export the data to a single collector upstream.

![input-clustering](https://gitlab.com/rdodin/pics/-/wikis/uploads/c823664e68265c3f466a521a621f6988/image.png)

Or create a so-called [data-reuse pipeline][data-reuse] where multiple outputs receive the same telemetry data.

![data-reuse](https://gitlab.com/rdodin/pics/-/wikis/uploads/3bae7c583db932a6c972a2828348296c/image.png)

### Tunnel server (gNMI dial-out)

Dial-out Streaming Telemetry has been a custom thing for quite some time. gNMI specification only specifies the dial-in model where a collector initiates the session towards the gNMI-enabled targets, and not the other way around. But being able to initiate a connection from the router towards a collector is sometimes desirable or even mandatory.

To accommodate for that deployment scenario, vendors implemented custom gRPC services that catered to this use case. And recently, the Openconfig group proposed a standard approach to enable dial-out gNMI telemetry using [:material-github: openconfig/grpc-tunnel project][grpctunnel-repo].

![dialout](https://gitlab.com/rdodin/pics/-/wikis/uploads/114526863c6ce60b23f232bf88310363/image.png)

gNMIc is the first open-source collector that [implements grpc-tunnel specification][grpctunnel-gnmic] and thus can support deployment scenarios where dial-out is needed using a proposed standard approach.

### Deployment examples

All those features make gNMIc quite versatile and powerful, but at the same time, it might be _overwhelming_ for newcomers. With that thought in mind, gNMIc packs many [deployment examples][deployment-examples] that should help users get going quickly and smooth.

<center>![example](https://gitlab.com/rdodin/pics/-/wikis/uploads/7facfa7b11895c5432f9adf03a7e5d15/image.png){: style="width:600px"}</center>
<center><small>A deployment topology from one of the examples</small></center>

gNMIc deployment examples provide users with a complete use case explanation. Moreover, every example comes with a ready-made virtual testbed[^2] so that you can try the scenario for yourself.  
The examples typically include a gNMIc instance with its configuration, the rest of the Telemetry stack (TSDB of choice plus Grafana), and a virtual network to extract the data.

### What else?

Many other things and improvements were made to gNMIc, making it even more powerful.

- **[gNMI Server][gnmi-server]** that makes gNMIc act as a gNMI target itself to build hierarchical collector deployments.
- **[Actions][actions]** allow gNMIc to invoke reactions based on the received telemetry data and, to some extent, help users build reactive systems.
- **[REST API][restapi]** to automate target provisioning and lifecycle.

### Why Not Telegraf?

This question may very well still be on your mind when you reach this chapter. And now, when we walked over the collector's features, it is evident that most of those features are simply not available in Telegraf. Clustering, high availability, target discovery, hierarchical deployments are all unique to gNMIc.

<center>![scalpel](https://gitlab.com/rdodin/pics/-/wikis/uploads/8108e0661fed0b930ba87745ec5812d7/image.png){: class="img-shadow" style="width: 600px"}</center>

Telegraf is an excellent product, don't get me wrong, but when it comes to gNMI it is a swiss knife vs. a surgical scalpel.

[[[ header_divider ]]]

## Go API

And finally, gNMIc provides a human-friendly [Go API for gNMI][goapi]. In contrast with the auto-generated gNMI API supplied by the `github.com/openconfig/gnmi` package, the API exposed by the gNMIc in the `github.com/openconfig/gnmic/api` package has abstractions in place that make interactions with gNMI targets less cumbersome and more intuitive.

=== "Create gNMI target"
    ```go
    router, err := api.NewTarget(
        api.Name("router1"),
        api.Address("10.0.0.1:57400"),
        api.Username("admin"),
        api.Password("S3cret!"),
        api.SkipVerify(true),
    )
    ```
=== "Create Get Request"
    ```go
    getRequest, err := api.NewGetRequest(
        api.Encoding("json_ietf"),
        api.DataType("config"),
        api.Path("interfaces/interface"),
        api.Path("network-instances/network-instance"),
    )
    ```
=== "Running request"
    ```go
    getResponse, err := router.Get(ctx, getRequest)
    ```

With a friendly API, we expect to see an uptake in gNMI as a network management protocol being used programmatically. Go get it!

[[[ header_divider ]]]

## Move to Openconfig

Now to the meat of it. Nokia donates gNMIc to the Openconfig group. But why moving?

[I believe](#disclaimer) there are several interdependent areas of improvement worth indicating.

1. The move will help gNMIc to gain more visibility across the expanding field of Streaming Telemetry users.
2. With the popularity gain, we might discover new use cases, new integration opportunities and get more feedback.
3. Close collaboration with Openconfig/Google might bring new contributors to the project and help with sustainability. It is an open-source project, and it will stay open.
4. Being under the wing of Openconfig should help users be less concerned about the project's health should they consider using it in production.

There is a lot of wishful thinking, and we don't know if everything we wish to accomplish will materialize, but we would like to give it a go.

Karim, as the sole developer, will still be at the helm of gNMIc development, but we expect more contributors appear in the future.

## Disclaimer

1. I contributed to gNMIc during the project's early days, but 99% of the effort came from Karim Radhouani[^3]. The credit goes to him for making gNMIc as we know it today. I would also like to thank our contributors who helped shape and form gNMIc with their valuable comments, feedback, and contributions.

2. The thoughts and statements I made in this post belong to me and do not necessarily match Nokia's.

[^1]: such as [History](https://github.com/openconfig/gnmi/blob/480bf53a74d21bb0a82d5d716264874de1070120/proto/gnmi_ext/gnmi_ext.proto#L32)
[^2]: powered by [containerlab][clab] or docker-compose.
[^3]: you can find him at [linkedin][karim_linkedin] and [github][karim-github].

[actions]: https://gnmic.openconfig.net/user_guide/actions/actions/
[clab]: https://containerlab.dev
[clustering]: https://gnmic.openconfig.net/user_guide/HA/
[consul-loader]: https://gnmic.openconfig.net/user_guide/targets/target_discovery/discovery_intro/#consul-server-loader
[data-reuse]: https://gnmic.openconfig.net/user_guide/inputs/input_intro/#data-reuse
[deployment-examples]: https://gnmic.openconfig.net/deployments/deployments_intro/
[diff-cmd]: https://gnmic.openconfig.net/cmd/diff/diff/
[distrib-cluster]: https://gnmic.openconfig.net/user_guide/inputs/input_intro/#clustering
[docker-loader]: https://gnmic.openconfig.net/user_guide/targets/target_discovery/discovery_intro/#docker-engine-loader
[file-loader]: https://gnmic.openconfig.net/user_guide/targets/target_discovery/discovery_intro/#file-loader
[getset-cmd]: https://gnmic.openconfig.net/cmd/getset/
[gnmi-ref]: https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md
[gnmi-server]: https://gnmic.openconfig.net/user_guide/gnmi_server/
[gnmic-main-site]: https://gnmic.openconfig.net/
[gnmic-repo]: https://github.com/openconfig/gnmic
[goapi]: https://gnmic.openconfig.net/user_guide/golang_package/intro/
[grpctunnel-gnmic]: https://gnmic.openconfig.net/user_guide/tunnel_server/
[grpctunnel-repo]: https://github.com/openconfig/grpctunnel
[ha]: https://gnmic.openconfig.net/user_guide/HA/#instance-failure
[http-loader]: https://gnmic.openconfig.net/user_guide/targets/target_discovery/discovery_intro/#http-loader
[inputs]: https://gnmic.openconfig.net/user_guide/inputs/input_intro/
[karim_linkedin]: https://www.linkedin.com/in/karim-radhouani/
[karim-github]: https://github.com/karimra
[oc]: https://openconfig.net/
[outputs]: https://gnmic.openconfig.net/user_guide/outputs/output_intro/
[path-gen]: https://gnmic.openconfig.net/cmd/path/
[processors]: https://gnmic.openconfig.net/user_guide/event_processors/intro/
[prompt-cmd]: https://gnmic.openconfig.net/user_guide/prompt_suggestions/
[restapi]: https://gnmic.openconfig.net/user_guide/api/api_intro/
[scaling]: https://gnmic.openconfig.net/user_guide/HA/#scalability
[target-distrib]: https://gnmic.openconfig.net/user_guide/HA/#target-distribution-process
[target-load]: https://gnmic.openconfig.net/user_guide/targets/target_discovery/discovery_intro/
[template-set]: https://gnmic.openconfig.net/cmd/set/#templated-set-request-file
