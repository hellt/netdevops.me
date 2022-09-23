---
date: 2021-08-17T06:00:00Z
comment_id: scrapligo-kubectl
keywords:
  - scrapli
  - docker
  - kubernetes
  - go
tags:
  - scrapli
  - docker
  - kubernetes
  - go

title: Using scrapligo with kubectl exec
---

<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/hellt/drawio-js@main/embed2.js" async></script>

As the networking industry is (slowly) moving towards forklifting networking functions to the cloud-native space we often become the witnesses of mixing decade old tools with cloud-native approaches and architectures.

This post is about one such crazy mixture of using screen scraping library [scrapligo](https://github.com/scrapli/scrapligo) with `kubectl exec` and `docker exec` commands.

## What and Why?
I can imagine that for some readers the previous sentence makes no sense, why do you need a screen scraping library when working with standalone containers or kubernetes workloads? Shouldn't it be all covered with various APIs already?

It should, yes, but when networking workloads are being moved into _the cloud_ it is more often than not results in a compromised architecture which is not fully aligned with the behavior of the containerized workloads.

* For example, when deploying a network function on kubernetes you might realize that the container image doesn't use the IP address that container runtime provisions for its `eth0` interface.

* Or you might want to add some basic configuration to a Network OS running as a k8s pod without creating a service for its SSH/NETCONF/etc server.

* Or you need to generate self-signed certificates on the NOS side to enable programmable access via gNMI or HTTPS.

In all these cases you often resort to `kubectl/docker exec` commands to connect to a shell/CLI and do some CLI based configuration over that terminal interface. This makes `kubectl exec` pretty much a modern day Telnet.

Since these operations over a terminal interface allocated by `exec` commands are almost inevitable, it makes a lot of sense to be able to automate interactions over it.

## scrapligo and `kubectl exec`
Scrapligo, which is a [Go version of the famous Scrapli library](https://netdevops.me/2021/network-automation-options-in-go-with-scrapligo/), is now able to handle CLI based interactions over the terminal interface offered by `docker exec` or `kubectl exec` (or any other command that exposes a PTY actually).

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:0,&quot;zoom&quot;:2,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/hellt/diagrams.net/master/scrapligo-exec.drawio&quot;}"></div>

This is especially cool in conjunction with `kubectl exec`, since you might have your networking workloads live in a remote cluster and without any k8s services you could get programmatic access to the shell/CLI of the Network OS to perform some bootstrap or validation.

An approach like that can hugely simplify the operations of networking workloads in the remote clusters, and believe me, the tasks that you can't carry out otherwise still exist...

## Lab deployment
To demonstrate this new scrapligo capability I will use the following user story.

A user deployed a networking lab with Nokia SR Linux nodes on a remote k8s cluster. They intend to manage the nodes with gNMI interface, but in order to do that, a TLS certificate must be provisioned on a device which gNMI will use to secure the transport layer.

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;margin:0 auto; display:block;" data-mxgraph="{&quot;page&quot;:1,&quot;zoom&quot;:3,&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;check-visible-state&quot;:true,&quot;resize&quot;:true,&quot;url&quot;:&quot;https://raw.githubusercontent.com/hellt/diagrams.net/master/scrapligo-exec.drawio&quot;}"></div>

{{< admonition type=info open=true >}}
I am using SR Linux containers here because they are [available for pulling for everyone](https://netdevops.me/2021/nokia-sr-linux-goes-public/), but you can swap it with Arista cEOS or any other NOS easily.
{{< /admonition >}}

For various reasons, it is not possible to configure an Ingress service to enable external access for SR Linux workload, but cluster management is possible via `kubectl`. So we could configure TLS certificates over `kubectl exec`, and that is what we will do, but programmatically.

To replicate this scenario we will deploy two docker containers on a host
* the container named `gnmi` that hosts the [`gnmic`](https://gnmic.kmrd.dev) tool to test gNMI access
* and `srlinux` container that is our Network OS of choice.

On the docker host side we will run a [`scrapligo` program](https://github.com/hellt/scrapligo-pty-demo) that will provision TLS certificates and gNMI service over `docker exec` command (step 1).

Then container with `gnmic` inside will be able to use gNMI service on the srlinux container (step 2).

{{< admonition type=info open=true >}}
For simplicity we use `docker exec` and plain containers, but the same will work with `kubectl exec` without any deviations.
{{< /admonition >}}

### Deploy containers
First, start an srlinux container named `srlinux` in daemon mode, which is as easy as:

```shell
docker run -t -d --rm --privileged \
  -u $(id -u):$(id -g) \
  --name srlinux ghcr.io/nokia/srlinux \
  sudo bash /opt/srlinux/bin/sr_linux
```

Then add gnmi container:

```shell
docker run --rm -it --privileged \
  --name gnmic ghcr.io/hellt/network-multitool \
  bash
```

### Check gNMI
To ensure we are not cheating, let's verify that gNMI service is not configured on SR Linux, and we can't use it.

Since SR Linux cli is a process inside the container, we can provide a CLI command to that process and get its output:
```shell
docker exec srlinux sr_cli "info system gnmi-server"
    system {
        gnmi-server {
        }
    }
```

The gNMI config is indeed empty, as well as the TLS server profiles:

```shell
# provides empty output
docker exec srlinux sr_cli "info system tls"
    system {
        tls {
        }
    }
```

## Code walkthrough
Now it is time to run the Go program that will leverage scrapligo's abilities to execute commands over a terminal offered by `docker exec`.

On your host, clone [hellt/scrapligo-pty-demo](https://github.com/hellt/scrapligo-pty-demo) and explore its `main.go` file.

```
git clone https://github.com/hellt/scrapligo-pty-demo.git
```

The whole program is contained within the [`main.go`](https://github.com/hellt/scrapligo-pty-demo/blob/master/main.go) file, let's cover the main pieces of this short program.

### Network driver creation
We first start by creating an SR Linux driver, using [srlinux-scrapli package](https://github.com/srl-labs/srlinux-scrapli) providing scrapligo support for SR Linux.
```go
func main() {
	contName := "srlinux"
	tlsProfileName := "demo"

	d, err := srlinux.NewSRLinuxDriver(
		contName,
		base.WithAuthStrictKey(false),
		base.WithAuthBypass(true),
	)
```

We also set the container name our srlinux container has - `srlinux` - as well as set the name for the TLS profile we want to configure along the way.

The important part is `base.WithAuthBypass(true)`, this option disables the authentication that would normally happen should you try to SSH into the device. With `exec` command the authentication is not needed, as we execute the process directly inside the container.

{{< admonition type=info open=true >}}
Note, that no IP/DNS address is present, that is because we are not using SSH to access the node, instead we provide a container name that we will refer later within `docker exec` command.
{{< /admonition >}}

### Setting Open command
When we initialized our Network Driver we implicitly said to scrapligo that we would like to use the `System` transport.

The way `System` transport works is that it calls `ssh` program on your host and then works with the pseudo terminal the openssh offers.

In `docker exec` case what we need to do is to actually overwrite the default command that is used to call the `ssh` program and tell scrapligo to use `docker exec` instead. This is how its done:

```go
transport, _ := d.Transport.(*transport.System)
transport.ExecCmd = "docker"
transport.OpenCmd = []string{"exec", "-u", "root", "-it", contName, "sr_cli"}
```

Notice, that we simply state the CLI command that you would normally use in your terminal. That is exactly how `System` transport works, it calls the specified command an expects to be able to connect a pseudo terminal to the called process.

### Configuring certificates and gNMI
The rest of the code is not interesting at all, as all that happens next is just some tinkering with CLI commands to tell SR Linux to generate TLS certificates and use them for gNMI.

```go
err = srlinux.AddSelfSignedServerTLSProfile(d, tlsProfileName, false)
if err != nil {
	fmt.Println(err)
	os.Exit(1)
}

d.AcquirePriv("configuration")

fmt.Println("Enabling gNMI...")
gnmiCfg := []string{
	"set / system gnmi-server admin-state enable",
	"set / system gnmi-server timeout 7200",
	"set / system gnmi-server rate-limit 60",
	"set / system gnmi-server session-limit 20",
	"set / system gnmi-server network-instance mgmt admin-state enable",
	"set / system gnmi-server network-instance mgmt use-authentication true",
	"set / system gnmi-server network-instance mgmt port 57400",
	fmt.Sprintf("set / system gnmi-server network-instance mgmt tls-profile %s", tlsProfileName),
	"commit save",
}

_, err = d.SendConfigs(gnmiCfg)
```

## Running the program
Now all is ready to run that program that should result in configuring the TLS certs and gNMI service over `docker exec` on srlinux container.

```shell
❯ go run main.go
Configuring TLS certificate...
Enabling gNMI...
```

Let's see if TLS certs are now in place:

```
❯ docker exec srlinux sr_cli "info system tls"
    system {
        tls {
            server-profile demo {
                key $aes$7PkycPYrUtfg=$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
                certificate "-----BEGIN CERTIFICATE-----
MIIE+zCCAuOgAwIBAgIUPydqw851/QfI/nSER+MYsD457egwDQYJKoZIhvcNAQEL
BQAwDTELMAkGA1UEBhMCVVMwHhcNMjEwODE3MTQ1MjQzWhcNMjIwODE3MTQ1MjQz
WjANMQswCQYDVQQGEwJVUzCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIB
AM1wPwXpvoakWZFhtzrBVJ1qsO0qmsdEzZJBeZ0PQjL9xkM5JsS/rrybPXu5WNqa
dWMLB3OtWLuaJ+uchdt0rF1os6ALsNlHl4cZyrU2b+0tZkF+E7q/nz0E0NSjoT9O
U9Si10eWwRj1jI/DsUwJr+d9lDtjHGWG7SquF7b8423pDlhSrdtSTXb2Eh8g2Yrg
fKwvoqDsMrnLN4dtYb192NpjKo6SJFJozzrweICVqdNKcx5BaUredxA5FpdIZOmQ
Ec5K9eEBxpxAmmXoW1U1GEAUiqf9diJ6HPw5sXltjj87Fxher8NnT5R0bj0HlctY
KM+RWMxJzKZqs/FWGdpnti71v1bynT/O8LUiULk/6Ms1bSS1pe9sd3Co9HiZLnp1
LWTGFAmtjpFYq3lXYql/rwx4v9xqSVqMLyjDtVRXDxjaVLFNyQZsR4U+nlJ6tq6v
DIYj6h05MBAejXIo7YeEUkTZJDL7+cHgJU6YjPQKDw3p9keLJsPYA62AKikgnAfX
PAYll7kZxNT/rGM5emj0Kkr3cgJY22bowqvo36/GcJrte+It/27IwE5Lb53PD5BT
DiBo21BCYPFe8qX2dN10vDAm08naD59vA68FfmBXhM6voRGGcovK6itRuR6xSJWX
TRI4kP+E+9sGiGX5rMlWX1PjATWx+ygqLIfBxLMtFyhbAgMBAAGjUzBRMB0GA1Ud
DgQWBBTcUql90C5AYyryIncoCdOwvGPcxzAfBgNVHSMEGDAWgBTcUql90C5AYyry
IncoCdOwvGPcxzAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4ICAQBo
4Lr2gJQBQukNwEr8fSZNNhvuveo69nOvQRbQbAaMbWtyZlL4LKIfOg5vh6aD7Lcr
WbQK+4xNwvFoyKwa3DTqYUu2xO8DKPbP+Fnfv3WP4geYc3hexsjveE+64oAM/Te3
pzSW3bx1gLgS3LCRF8NT1ZBP+xwfs57tAXypoSbLr8y35cynFQkgd3Phwb6koUxg
j5OrsTrf8hOMvigJ6dSiwGwYZ77kyDsoHdQTaoQQoxhdz8RZWbvCr1JuCMXfqCSg
J1biwqTF8mpJ0EGUSlz2D1RKnxjsKZ5EgZ3X0s2v23A4GiMqCJDEyAA+rFzCq/ov
PmuNAXsioMdPk6C2VMNzyxq2GCSTweJnSMa+jpk/WkQok39jnx4kW7LoW555cT3+
weuT1pK1Kg1z1S1ytkn7q+AjNfaYZgRtKQ/FWaww97LCXrEoZQw0VMiuhTxFajyJ
iv5a6771qvnDbWSkZFqL08PU/24m6OrpNOfXzp9KMYBi7O83flCQbuvnpdAlDOEA
WyNOXHiIQ+jrfETSCWwD2ncKeucGlZqj3uZk1n+yEdMLuoFzOKfLg+OG5Lx+zU2D
lZ5hmj9IiQ7NSDXbSnDTUJ56XbKx92kkVOdKAKhML8mgtLFJMK2fy5K3ahinoLOK
8k4fIE+zVn7ld/LLf7MXdh1SvFLOF4/kxKUw9pRoEQ==
-----END CERTIFICATE-----"
                authenticate-client false
            }
        }
    }
```

And gNMI server has been configured to use the `tls-profile` that the program created:
```
❯ docker exec srlinux sr_cli "info system gnmi-server"
    system {
        gnmi-server {
            admin-state enable
            timeout 7200
            rate-limit 60
            session-limit 20
            network-instance mgmt {
                admin-state enable
                use-authentication true
                port 57400
                tls-profile demo # <- references the created TLS profile which has the generated cert/key
            }
        }
    }
```

All points out that we can now use gNMI service with a secured transport. To check that, let's go back to our gnmic container that we launched and try and get some data via gNMI.

{{< admonition type=info open=true >}}
Before doing that, we need to see which IP address the srlinux has on its management interface. It can be queried with the following show command:
```
❯ docker exec srlinux sr_cli "show interface mgmt0.0"
===============================================================
  mgmt0.0 is up
    Network-instance: mgmt
    Encapsulation   : null
    Type            : None
    IPv4 addr    : 172.17.0.2/16 (dhcp, preferred)
    IPv6 addr    : fe80::42:acff:fe11:2/64 (link-layer, preferred)
===============================================================
```
{{< /admonition >}}

Now in the bash shell of the gnmic container, craft the [`gnmic`](https://gnmic.kmrd.dev) command to get some data over gNMI:

```
gnmic -a 172.17.0.2 -u admin -p admin --skip-verify -e json_ietf \
      get --path /system/information/version
```

and that returns the version of the SR Linux NOS, yay!
```
[
  {
    "timestamp": 1629268834502587033,
    "time": "2021-08-18T06:40:34.502587033Z",
    "updates": [
      {
        "Path": "srl_nokia-system:system/srl_nokia-system-info:information/version",
        "values": {
          "srl_nokia-system:system/srl_nokia-system-info:information/version": "v21.6.1-250-g433be28615"
        }
      }
    ]
  }
]
```

## Summary
`kubectl exec` is the modern day's Telnet, it allows to get terminal access to applications running in k8s cluster, without having network access exposed on the workloads themselves.

Scrapligo (and later scrapli) allows us to programmatically use this terminal interfaces exposed by commands like `kubectl exec/docker exec/etc` to configure/interrogate the workloads over this OOB character based interface.

The approach demonstrated above is especially useful in the current days when networking workloads may still require some bootstrapping steps in order to come up ready to be managed.