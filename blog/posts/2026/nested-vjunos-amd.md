---
date: 2026-11-22
comments: true
tags:
  - containerlab
  - juniper
  - virtualization
  - boxen
---

# Making vJunos boot faster in virtual machines with AMD CPU

Booting a vJunos-switch (or vJunos-router) should **not** leave enough time to make coffee, drink it, and start questioning your life choices. Yet this is roughly where it was in Containerlab-land should you have an AMD CPU: **15 minutes and 24 seconds** from starting the container to a healthy Junos node.  
This was bad, but not too bad, considering that HPE/Juniper official stance is:

1. vJunos-switch/router deployment in VMs is not supported.
2. vJunos-switch/router deployment supports only Intel VT-x virtualization.

While it is quite common to see VM-images not running on ARM architecture, seeing them disqualified on the merit of running in the VMs or on Intel VT-X vs AMD SVM is weird. And as you'll see in this post, there are no technical reasons to support these claims.

In [Nebius cloud](https://nebius.com/compute) I have general compute nodes powered by AMD EPYC Genoa chips and thus seeing slow Junos boot was hitting me personally :)

After three small patches to the Junos startup script, the same Junos vSwitch became healthy on the same hardware in about **5-6 minutes**, and the biggest improvement came from giving Junos *fewer* vCPUs.

> The credit goes to Piet Braat for the important discoveries he had in his [Defying the 'Impossible': Getting Nested vJunos-switch Running on AMD Epyc](https://www.linkedin.com/pulse/defying-impossible-getting-nested-vjunos-switch-running-piet-braat-i9d4e/) blog. Piet ignored the usual "vJunos on ARM CPUs is not supported", dug into the guest, and documented his findings.  
> My part was to revalidate his findings with [Boxen](https://boxen.containerlab.dev/), time each change, and package the result so that others won't have to questions their life choices.

<!-- more -->

## Wait, how nested?

Frankly, all that funky business with vJunos comes from the sad fact that vJunos is not just one VM. The outer Linux VM runs the dataplane and starts another QEMU process for the Junos control plane VM. This world did not need the hidden nested virtualization, but it got it anyways...

My lab host is itself a cloud VM, which makes the whole arrangement look like this:

| Layer | What runs there | vCPUs |
| --- | --- | ---: |
| L0/L1 | Physical host and Nebius KVM hypervisor | Not exposed |
| L2 | Cloud VM running Docker, Containerlab and Boxen | 16 |
| L3 | Outer vJunos-switch VM started by Boxen | 4 |
| L4 | Nested Junos control-plane VM | 5 before the fix, 1 after it |

Turtles, hypervisors, all the way down. However, the nested virtualization in and of itself is not a hard blocker if your CPU is modern and powerful enough. I have the EPYC Genoa one, which is not the most fancy chip on the block, but a decent one, that had no problem in chugging the nested VMs.

///details | CPU spec of the cloud VM:

| Property | Value |
| --- | --- |
| Exposed CPU model | AMD EPYC-Genoa Processor |
| CPU family / model / stepping | 25 / 17 / 0 |
| Topology | 1 socket, 8 cores, 2 threads per core |
| Frequency | 2396.398 MHz |
| L1d / L1i cache | 256 KiB each |
| L2 / L3 cache | 8 MiB / 32 MiB |
| Virtualization | AMD-V, `svm`, and `npt` |
| Nested AMD virtualization | `kvm_amd nested=1` |
| TSC capabilities | `constant_tsc`, `nonstop_tsc`, `tsc_known_freq` |
| Hypervisor | KVM |
///

vJunos HW requirements page will outright [says](https://networkingdocs.hpe.com/documentation/us/en/software/vjunos-router/vjunos-router-kvm/topics/vjunos-router-kvm-hw-requirements.html): _vJunos-router is not supported on EVE-NG or any other deployments that launch vJunos from within a VM due to the constraints of deeply nested virtualization._  
A limitation, which turns out to be not that hard to overcome. It is hard to imagine lab systems (not to mention public clouds), that will offer bare metal compute for labs and simulations.

Anyways, the nested virt alone was not the roadblock for vJunos in my[^1] env - it was something else.

## The first AMD problem: SVM

If you download the vJunos-switch or vJunos-router and try running it on your fancy AMD processor, you'll see the VM shutting down pretty soon due to a missing `vmx` cpu capability. The `vmx` cpu capability is hardware-assisted virtualization for Intel processors, and the AMD processors have the like-to-like capability encoded like `svm`.  
Naturally, an AMD processor won't ever have `vmx` capability in the output of `/proc/cpuinfo`, yet, this is what the vJunos startup script only cares about: 

```bash
CPU_FLAG=$(cat /proc/cpuinfo | grep -ci "vmx")
```

On an AMD machine this check failed, and `/home/pfe/junos/start-junos.sh` helpfully shut everything down. Boxen already patched it to accept both Intel and AMD virtualization flags:

```bash
CPU_FLAG=$(cat /proc/cpuinfo | grep -Eci "vmx|svm")
```

That patch came from the earlier [MarcsTech vJunos-switch AMD workaround](https://marcstech.blog/archives/juniper-vjunos-switch-amd-cpu-containerlab/). It got us past the shutdown, but the boot was still painfully slow. Fifteen bloody minutes...

## Attached strace monitor?

Piet's article had two more leads: a mysterious `-S` QEMU flag and a monitor process that attached `strace` to the nested VCP control plane VM. Time to measure instead of guessing.

The inner QEMU command that starts the Junos control plane VM goes like this:

```bash
/usr/bin/qemu-system-x86_64 \
 -S \
 -daemonize \
 -name vcp-vmx1 \
 ...
```

QEMU's documentation describes `-S` as:

> Do not start CPU at startup (you must type 'c' in the monitor).

The reason that Juniper started this VM in a paused mode is because they attached an `strace` monitor to the control plane VM and then started it. Right after starting the nested VM, `start-junos.sh` launched `qemu_monitor.sh`. The monitor found the QEMU PID and attached `strace` to it:

```bash
/usr/bin/strace -e none -e exit_group -p "$PID"
```

How important is it for a regular lab node?.. Let's find out. I built a new image with the both `-S` arg and the line that started `qemu_monitor.sh` removed.


This combination produced the first useful improvement:

| Image |  Launch to healthy | Change from original |
| --- |  ---: | ---: |
| Original  | 924 seconds | — |
| `-S` and strace monitor removed  | 782 seconds — 13m02s | −15.4% |

Two minutes saved is nice. Thirteen minutes is still far too long, though. The article had one more clue, and it turned out to be the big one.

## Four vCPUs in, eight processors out

The vJunos startup script decides how many vCPUs the nested Junos VM gets with this bit of shell:

```bash
totalcpu=$(cat < /proc/cpuinfo | grep -csi "processor")

if [ "$totalcpu" -le 3 ]; then
   VCPCPU=1
else
   VCPCPU=$((totalcpu-3))
fi
```

Three CPUs are reserved for the dataplane VM, and the rest go to Junos VCP Control plane VM. With a four-vCPU allocated to the outer vJunos VM, its inner VCP VM should therefore get 4-3=**one vCPU**.

Except `grep -i "processor"` does not only match the actual processor entries on an AMD guest. It also matches the model name:

```text
processor : 0
model name : AMD EPYC-Genoa Processor
```

Every real vCPU was counted twice. Four outer vCPUs became eight matches, and the script then calculated `8 - 3 = 5` vCPUs for Junos VCP VM.

The serial console showed the whole comedy in three lines:

```text
smpboot: Total of 4 processors activated
VCPMEM in MB: 1886, VCPCPU: 5
FreeBSD/SMP: Multiprocessor System Detected: 5 CPUs
```

So the inner QEMU was scheduling five Junos vCPU threads on an outer VM with four vCPUs, while the dataplane also wanted CPU time. Brilliant.

Piet's fix is one character long — anchor the match to the beginning of the line:

```diff
-totalcpu=$(cat < /proc/cpuinfo | grep -csi "processor")
+totalcpu=$(cat < /proc/cpuinfo | grep -csi "^processor")
```

Now the model name stays a model name, `totalcpu` is four, and Junos VCP VM gets the intended single vCPU when the outer VM has four vCPU provided to it. And this change made the world...

## Taking care of the inner VCP VM

Packaging ends by shutting Junos down so that Boxen can save the disk. The profile used `request system halt`. Junos did halt, but halting FreeBSD does not stop the nested QEMU process. It keeps running, holding the Junos disk — a qcow2 file opened with `cache=writeback` — with writes it has not flushed yet. Boxen then kills the outer VM, and whatever was still in flight is gone, causing weird FS check issues when I attempted to run it.

Packaging step now runs `request system power-off` instead. The nested QEMU exits and flushes its disk on the way out, and Boxen waits another 30 seconds so that the outer VM's filesystem writes that out too, before the outer VM is stopped. No more panics.

## Splitting consoles

The Junos console is the outer VM's `ttyS0`, and the outer VM's kernel and init write to the same port. While Junos boots, the dataplane comes up in the outer VM: it binds every data NIC to `igb_uio` and starts DPDK, and all of that chatter lands on the serial port, interleaved with the Junos output. Since Boxen relies on reading the console and seeing messages that gate the next steps, the garbled console output makes the whole boot process unpredictable.

```text
c[  339.891118] igb_uio 0000:02:0a.0: mapping 1K dma=0xbbba2000 host=ffff8800bbba2000
[  339.895156] igb_uio 0000:02:0a.0: unmapping 1K dma=0xbbba2000 host=ffff8800bbba2000
ommit complete
```

That `c` + `ommit complete` is Junos telling us `commit complete`, just mixed up with other concurrent console writes.

To overcome this, Boxen patches the console handling and now sends the output of the dataplane launch script and of the PFE manager (`mpcsd.py`) to log files under `/var/log` in the outer VM, and drops the outer kernel's console log level to emergencies only (`echo 1 > /proc/sys/kernel/printk`) right before the dataplane starts. The outer VM's boot messages and the `VCPCPU` line still show up on the console, so it stays useful for debugging.

## The numbers

### How I timed it

With these fixes in place, the image built from the vendor `vJunos-switch-26.2R1.7.qcow2` was put to a test in a two-node Containerlab (0.83.0) topology, with the vJunos-switch `ge-0/0/0` cabled to a multitool container:

```yaml
name: vjunos-amd-ping

topology:
  nodes:
    vswitch1:
      kind: juniper_vjunosswitch
      image: boxen-juniper_vjunos-switch:26.2R1.7
      startup-config: vswitch1.cfg
    multitool:
      kind: linux
      image: ghcr.io/srl-labs/network-multitool:latest
      exec:
        - ip addr add 192.0.2.2/30 dev eth1

  links:
    - endpoints: ["vswitch1:ge-0/0/0", "multitool:eth1"]
```

`vswitch1.cfg` puts `192.0.2.1/30` on `ge-0/0/0`, so the healthy mark now also includes loading and committing a startup configuration on top of the runtime one.

A small script ran three back-to-back rounds, and each round did this:

1. `containerlab destroy --cleanup` followed by `containerlab deploy`, so every run started with a fresh container and a fresh disk overlay.
2. Took the container's `State.StartedAt` from `docker inspect` as time zero.
3. Polled `docker exec vswitch1 cat /health` every second until it read `0 running`. Boxen writes `1 booting` when the container starts and flips it once the runtime and startup-config steps are done.
4. Ran `ping -c1 -W1 192.0.2.1` from multitool in a loop until the first reply came back, then 5 more pings to check for loss.

These are the milestones and the console markers they come from:

| Milestone | Marker |
| --- | --- |
| Junos VM launched | `VCPMEM in MB: 1886, VCPCPU: 1`, printed by `start-junos.sh` right before it starts the nested QEMU |
| Junos kernel | `Copyright (c) 1992-2024 The FreeBSD Project.` |
| Login prompt | `FreeBSD/amd64 (boxen-vjunos) (ttyu0)`, the banner above `login:` |
| Startup config | Boxen starts loading the startup configuration, right after the runtime configuration commit |
| Healthy | `/health` reads `0 running` |
| First ping | First echo reply received by multitool |

All times are seconds since the container started, with one-second resolution.

### The vJunos-switch 26.2R1.7 numbers

| Run | Junos VM launched | Junos kernel | Login prompt | Startup config | Healthy | First ping |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 109s | 138s | 310s | 341s | **355s — 5m55s** | 355s |
| 2 | 106s | 135s | 320s | 354s | **364s — 6m04s** | 365s |
| 3 | 111s | 140s | 319s | 333s | **353s — 5m53s** | 360s |

All three runs went healthy in **about six minutes** (357 seconds on average), with the default four outer vCPUs and one Junos VCP vCPU. Traffic flowed within seven seconds of the health flip, and none of the runs exhibited ping loss.

The six minutes were spent like this:

* **~110s** for the outer Linux VM to boot and launch the Junos VM;
* **~30s** from there to the Junos kernel;
* **172–185s** from the Junos kernel to its login prompt — the biggest single chunk;
* **34–45s** for Boxen to log in, apply and commit the runtime configuration, then load and commit the startup configuration.

## Is five vCPUs better than four?

Once the boot got faster, the natural next question was whether one more outer vCPU would make it faster still. More cores fixes everything, right?

With the corrected counting logic, five outer vCPUs produce **two** Junos VCP vCPUs:

```text
5 correctly counted outer vCPUs
5 - 3 = 2 nested Junos vCPUs
```

I ran the exact same fully patched image with `QEMU_SMP=5`. The console confirmed that the allocations were what I expected:

```text
smpboot: Total of 5 processors activated
VCPMEM in MB: 1886, VCPCPU: 2
FreeBSD/SMP: Multiprocessor System Detected: 2 CPUs
```

This run took **30s more**, than the 2vcpu-based VCP VM...

This also matches Piet's observation that multiple vCPUs in a deeply nested Junos guest can introduce timing problems. Giving Junos two vCPUs was worse than giving it one. The existing Boxen default of `cpuCores: 4` for the outer VM therefore stayed exactly as it was.

## Making the fix stick

Manual `virt-edit` sessions are good for an experiment and bad for repeatability. The premise of Boxen is to make the packaging a process that is grounded in code and repeatable. Both the `juniper_vjunos-switch` and `juniper_vjunos-router` profiles in [Boxen 0.5.0](https://github.com/carlmontanari/boxen/tree/main/assets/profiles) now patch the outer VM's startup scripts. They:

1. accept Intel VMX or AMD SVM;
2. count only lines beginning with `processor`;
3. remove the nested QEMU `-S` option and stop launching the `qemu_monitor.sh` strace monitor;
4. keep the dataplane and the outer kernel off the shared Junos console;
5. power Junos off instead of halting it at the end of packaging;
6. stop sending an empty line into the password prompt.

The changes were made in [Boxen PR #103](https://github.com/carlmontanari/boxen/pull/103).

## Kudos

The appealing answer to a slow VM is always more CPU, more memory, or a bigger host. Here the answer was four small packaging patches, one of which *reduced* the nested VM from five vCPUs to one.

And the reason I knew where to look was [Piet Braat's original post](https://www.linkedin.com/pulse/defying-impossible-getting-nested-vjunos-switch-running-piet-braat-i9d4e/). His write-up turned a vague "nested vJunos is impossibly slow on AMD" problem into concrete, testable fixes. Big kudos to him for doing the investigation and sharing it instead of keeping the working setup to himself.

[Boxen v0.5.0](https://boxen.containerlab.dev) vJunos-switch and vJunos-router profiles are now available for everyone to use with Containerlab and C9s.

[^1]: And for many vJunos users in Containerlab discord either.
