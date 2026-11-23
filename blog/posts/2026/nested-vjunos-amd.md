---
date: 2026-11-22
comments: true
tags:
  - containerlab
  - juniper
  - virtualization
  - boxen
---

# Making vJunos run faster in virtual machines with AMD CPU

Booting a vJunos-switch (or vJunos-router) should **not** leave enough time to make coffee, drink it, and start questioning your life choices. Yet this is roughly where it was in Containerlab-land should you have an AMD CPU: **15 minutes and 24 seconds** from starting the container to a healthy Junos node.  
This was bad, but not too bad, considering that HPE/Juniper gurus would claim that:

1. vJunos-switch/router deployment in VMs is not supported.
2. vJunos-switch/router deployment supports only Intel VT-x virtualization.

While it is quite common to see VM-images not running on ARM architecture, seeing them disqualified on the merit of running in the VMs or on Intel VT-X vs AMD SVM is weird. And as you'll see in this post, there are no technical reasons to support these claims.

In [Nebius cloud](console.nebius.com) I have general compute nodes powered by AMD EPYC Genoa chips and I had a need to run some Junos, so it was in my best interest to make it work.  
After three small patches to the Junos startup script, the same network node became healthy on the same hardware in **3 minutes and 44 seconds**, and the biggest improvement came from giving Junos *fewer* vCPUs.

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

Turtles, hypervisors, all the way down. However, the nested virtualization in and of itself is not a hard blocker if your CPU is modern and powerful enough. I have the EPYC Genoa one, which is not the most modern fly on the block, but a decent one.

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

vJunos HW requirements page will outright [say](https://networkingdocs.hpe.com/documentation/us/en/software/vjunos-router/vjunos-router-kvm/topics/vjunos-router-kvm-hw-requirements.html): _vJunos-router is not supported on EVE-NG or any other deployments that launch vJunos from within a VM due to the constraints of deeply nested virtualization._  
A self-imposed limitation, which turns out to be an overly precaution one as well. It is hard to imagine lab systems (not to mention public clouds), that will offer bare metal compute for labs and simulations.

Anyways, the nested virt was not the roadblock for vJunos in my[^1] env - it was something else.

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

The reason that Juniper started this VM in a paused mode is because they attached an `strace` monitor to the control plane VM and then started it. A debugger?  
Right after starting the nested VM, `start-junos.sh` launched `qemu_monitor.sh`. The monitor found the QEMU PID and attached `strace` to it:

```bash
/usr/bin/strace -e none -e exit_group -p "$PID"
```

How important it is for a regular lab node?.. Let's find out. I built a new image with the both `-S` arg and the line that started `qemu_monitor.sh` removed.

> One subtlety: deleting only the `strace` command is a bad idea. The rest of the monitor script would continue, decide that QEMU had exited, and shut down the outer VM. Debugger removal needs a tiny bit of precision.

This combination produced the first useful improvement:

| Image |  Launch to healthy | Change from original |
| --- |  ---: | ---: |
| Original  | 924 seconds | — |
| `-S` and strace monitor removed  | 782 seconds — 13m02s | −15.4% |

Two minutes saved is nice. Thirteen minutes is still far too long, though. The article had one more clue, and it turned out to be the big one.

## Four vCPUs walk in, eight processors come out

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

## All the numbers

I timed every run from container launch until Boxen wrote `0 running` to `/health`. This is deliberately the full user-visible wait: both VM layers boot, Junos reaches its CLI, Boxen applies the runtime configuration, and the configuration commit finishes.

* Each test used a fresh container with the same 5120 MiB of memory and network settings.
* Only one test VM ran at a time.
* The outer VM had four vCPUs unless the table says otherwise.

| Variant | Outer vCPUs | Inner VM (VCP) vCPUs | Junos prompt | Launch to healthy | After prompt |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 4 | 5 | 819s | **924s — 15m24s** | 105s |
| `-S` and strace monitor removed | 4 | 5 | 707s | **782s — 13m02s** | 75s |
| CPU-count fix only | 4 | 1 | 306s | **329s — 5m29s** | 23s |
| All fixes | 4 | 1 | 205s | **224s — 3m44s** | 19s |
| All fixes, repeat | 4 | 1 | 189s | **208s — 3m28s** | 19s |
| All fixes with `QEMU_SMP=5` | 5 | 2 | 236s | **246s — 4m06s** | 10s |

The CPU-count-only row was a deliberate ablation test: `-S` and the strace monitor were still enabled. That one-character CPU fix accounted for most of the total improvement by itself. Removing `-S` and the monitor then cut another 105 seconds from the first CPU-fix run.

The two complete-fix runs at four outer vCPUs differed by 16 seconds. These were sequential tests on one shared host, not a statistically rigorous benchmark, so I would not read anything into a few seconds either way. The difference between 924 and roughly 216 seconds is thankfully a little harder to explain away as noise.

## Is five outer vCPUs better than four?

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

This run took 246 seconds. The two four-vCPU runs took 224 and 208 seconds. On average, keeping the outer VM at four vCPUs was **30 seconds faster**.

This also matches Piet's observation that multiple vCPUs in a deeply nested Junos guest can introduce timing problems. Giving Junos two vCPUs was worse than giving it one. The existing Boxen default of `cpuCores: 4` for the outer VM therefore stayed exactly as it was.

## Making the fix stick

Manual `virt-edit` sessions are good for an experiment and bad for repeatability. Both the `juniper_vjunos-switch` and `juniper_vjunos-router` [Boxen profiles](https://github.com/carlmontanari/boxen/tree/main/assets/profiles) now patch `start-junos.sh` while packaging the image. They:

1. accept Intel VMX or AMD SVM;
2. count only lines beginning with `processor`;
3. remove the nested QEMU `-S` option and stop launching the `qemu_monitor.sh` strace monitor.


The changes were made in [Boxen PR #103](https://github.com/carlmontanari/boxen/pull/103).

## Final kudos

The appealing answer to a slow VM is always more CPU, more memory, or a bigger host. Here the answer was four small packaging patches, one of which *reduced* the nested VM from five vCPUs to one.

And the reason I knew where to look was [Piet Braat's original post](https://www.linkedin.com/pulse/defying-impossible-getting-nested-vjunos-switch-running-piet-braat-i9d4e/). His write-up turned a vague "nested vJunos is impossibly slow on AMD" problem into concrete, testable fixes. Big kudos to him for doing the investigation and sharing it instead of keeping the working setup to himself.

[Boxen's](https://boxen.containerlab.dev) vJunos-switch and vJunos-router profiles are now available for everyone to use with Containerlab and C9s.

[^1]: And for many vJunos users in Containerlab discord either.
