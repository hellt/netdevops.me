---
date: 2021-06-09
comments: true
keywords:
  - scrapli
  - textfsm
  - netconf
tags:
  - scrapli
  - textfsm
  - netconf

title: Network automation options in Go with scrapligo
---

Just recently the network automation folks witnessed a great library to be ported from Python to Go - [scrapligo](https://github.com/scrapli/scrapligo).

<center>{{<tweet 1395048837656367105>}}</center>

For me personally this was a pivotal point because with scrapligo the Go-minded netengs can now automate their networks with a solid and performant library.

One of the things that scrapligo packs is, of course, the ability to reliably _talk_ to the network devices using the same command line interface as a human would normally do. That means that scrapligo would send and receive the pieces of data that an operator would send/receive if they were connected with a terminal over SSH.

As you may very well be aware, the typical output that a network device produces for a given command is unstructured, meaning that it is not presented in a way that can be _effortlessly_ parsed by a machine.

```bash
# output of a `show system information` command from Nokia SR OS

===============================================================================
System Information
===============================================================================
System Name            : sros
System Type            : 7750 SR-1
Chassis Topology       : Standalone
System Version         : B-20.10.R3
Crypto Module Version  : SRCM 3.1
System Contact         :
System Location        :
System Coordinates     :
System Up Time         : 8 days, 00:24:27.04 (hr:min:sec)
```

If we were to send `show system information` command with scrapligo towards a Nokia SR OS device, we would have not be able to get, say, the device version right away, since the response is basically the unstructured blob of text as the program sees it.

What can we do about it?

## use NETCONF/gNMI/API

In an ideal world, you would have stopped reading this post, because ALL your devices were equipped with some kind of programmatic interface that returns structured data. Like in the example above we connect to the SR OS node with scrapligo netconf subsystem and retrieve back a result of a NETCONF Get operation.

We then can run a query on this XML document we received and get the data out just nicely.

```go
package main

import (
 "fmt"
 "strings"

 "github.com/antchfx/xmlquery"
 "github.com/scrapli/scrapligo/driver/base"
 "github.com/scrapli/scrapligo/netconf"
 "github.com/scrapli/scrapligo/transport"
)

func main() {
 d, _ := netconf.NewNetconfDriver(
  "clab-scrapli-sros",
  base.WithAuthStrictKey(false),
  base.WithAuthUsername("admin"),
  base.WithAuthPassword("admin"),
  base.WithTransportType(transport.StandardTransportName),
 )

 d.Open()

 r, _ := d.Get(netconf.WithNetconfFilter(`
 <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
 <system><version><version-number/></version></system>
 </state>`))

 doc, _ := xmlquery.Parse(strings.NewReader(r.Result))

 ver := xmlquery.Find(doc, "//version-number")

 fmt.Println(ver[0].InnerText())

 d.Close()
}
```

Output:

```
❯ go run netconf.go
B-20.10.R3
```

Unfortunately we are not yet there, we have thousands of access devices in Service Providers network which do not have any of the fancy interface. We have Enterprise networks running decade old gear. And we also live in a harsh world where even if the Network OS has one of those fancy interface, the level of information you can query via them is **not on par with what you can do over CLI**.

## on-box JSON output

The next best thing is to leverage the device's ability to present the output as JSON. Then you can capture this output over SSH and let your JSON parser to do it's thing.

For example, on EOS every show command can be represented as a JSON blob:

```json
ceos>show inventory | json
{
    "fpgas": {},
    "storageDevices": {},
    "xcvrSlots": {},
    "subcompSerNums": {},
    "portCount": 3,
    "switchedBootstrapPortCount": 2,
    "managementPortCount": 1,
    "dataLinkPortCount": 0,
    "emmcFlashDevices": {},
    "cardSlots": {},
    "internalPortCount": 0,
    "powerSupplySlots": {},
    "fanTraySlots": {},
    "systemInformation": {
        "name": "cEOSLab",
        "description": "cEOSLab",
        "mfgDate": "",
        "hardwareRev": "",
        "hwEpoch": "",
        "serialNum": ""
    },
    "unconnectedPortCount": 0,
    "switchedPortCount": 0,
    "switchedFortyGOnlyPortCount": 0
}
```

and with this tiny `scrapligo` program you can easily retrieve all the data from this output:

```go
package main

import (
 "encoding/json"
 "fmt"

 "github.com/scrapli/scrapligo/driver/base"
 "github.com/scrapli/scrapligo/driver/core"
 "github.com/scrapli/scrapligo/transport"
)

func main() {
 d, _ := core.NewCoreDriver(
  "clab-scrapli-ceos",
  "arista_eos",
  base.WithAuthStrictKey(false),
  base.WithAuthUsername("admin"),
  base.WithAuthPassword("admin"),
  base.WithTransportType(transport.StandardTransportName),
 )

 d.Open()
 // send show command and ask to output it as JSON
 r, _ := d.SendCommand("show inventory | json")

 // imagine, that the structure that this output can be parsed into is unknown to us
 // thus we will use a map of empty interfaces to dynamically query data after
 var jOut map[string]interface{}
 json.Unmarshal(r.RawResult, &jOut)

 fmt.Println("number of management ports:", jOut["managementPortCount"])

 d.Close()
}
```

that produces the following output:

```
❯ go run main_arista.go
number of management ports: 1
```

That approach is a decent alternative to a missing programmatic interface and sometimes is the best option. But, as it usually happens, it is not universal. Many Network OS'es can not emit JSON for any given command, if at all. That means we need to resort to the parsing of the unstructured data ourselves.

## good old parsing

And we back to square 1, where we usually get after some reality check. That is where we need to parse the unstructured output ourselves and get the blob of text we receive from a device to be transformed to some data structure which we can use in a program.

Of course, we can simply use Regular Expressions or even brute characters matching a loop, but when dealing with lengthy outputs (usually a product of a `show` command), we often resort to a framework that can simplify the parsing.

For quite a long time the [TextFSM](https://code.google.com/archive/p/textfsm/wikis/TextFSMHowto.wiki#:~:text=TextFSM%20is%20a%20Python%20module,for%20any%20such%20textual%20output.) python library was the answer to that particular task and since then a huge amount of textfsm templates were written to parse all sorts of outputs from various devices.

Being a Go person myself I was wondering if TextFSM exists in Go, since once we have scrapli in Go, having a parsing library in Go was the key piece missing.

Fortunately, some bright mind already ported TextFSM to Go - [go-textfsm](https://github.com/sirikothe/gotextfsm) - and Carl [integrated](https://github.com/scrapli/scrapligo/pull/28) it into scrapligo the same day I notified him that go-textfsm exists.

Let's have a look how it is used within scrapligo. For that exercise we will take a `show system information` output from Nokia SR OS and use a textfsm template to create a structured data out of it.

> the original textFSM templates might need to be touched by you, since Go regexp differs from Python RE in some parts.

To parse the output we will get from the Nokia SR OS device I will create a file with the textfsm template for this output under `sysinfo.textfsm` file name. Here is the template body:

```
# System
Value SysName (\S+)
Value SysType (.*)
Value Version (\S+)
Value SysContact (.*)
Value SysLocation (.*)
Value SysCoordinates (.*)
Value SysAtv (\S+)
Value SysUpTime (.*)
Value ConfigurationModeCfg (.*)
Value ConfigurationModeOper (.*)


Start
  ^System Information -> ReadData

ReadData
  ^System Name\s*:\s*${SysName}
  ^System Type\s*:\s*${SysType}
  ^System Version\s*:\s*${Version}
  ^System Contacts+:\s+${SysContact}
  ^System Location\s*:\s*${SysLocation}
  ^System Coordinates\s*:\s*${SysCoordinates}
  ^System Active Slot\s*:\s*${SysAtv}
  ^System Up Time\s*:\s*${SysUpTime}
```

Now when the template is there, we can write the following scrapligo + gotextfsm program:

```go
package main

import (
 "fmt"

 "github.com/scrapli/scrapligo/driver/base"
 "github.com/scrapli/scrapligo/driver/core"
 "github.com/scrapli/scrapligo/transport"
)

func main() {
 d, _ := core.NewCoreDriver(
  "clab-scrapli-sros",
  "arista_eos",
  base.WithAuthStrictKey(false),
  base.WithAuthUsername("admin"),
  base.WithAuthPassword("admin"),
  base.WithTransportType(transport.StandardTransportName),
 )

 d.Open()

 r, _ := d.SendCommand("show system information")

 parsedOut, _ := r.TextFsmParse("private/sysinfo.textfsm")

 fmt.Printf("Version: %s\nUptime: %s",
  parsedOut[0]["Version"], parsedOut[0]["SysUpTime"])

 d.Close()
}
```

Output:

```
❯ go run main_fsm.go
Version: B-20.10.R3
Uptime: 8 days, 03:07:43.25 (hr:min:sec)
```

Easy-peasy! All thanks to the textFSM integration that scrapligo recently added!

## PS

Regardless which network/vendor/consulancy firm you employed with, you won't be able to avoid CLI parsing activities at all times. The legacy gear is out there, with no other management interface but SSH/SNMP.

Before scrapligo it was quite tedious (I'd claim not worth it even) to automate network activities over SSH. Now the module packs almost everything you need to efficiently get going and write some nice automation programs or CLI tools.
