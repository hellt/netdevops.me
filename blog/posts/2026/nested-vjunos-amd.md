---
date: 2026-11-22
comments: true
tags:
  - containerlab
  - juniper
  - virtualization
---

# Making nested vJunos-switch fast on AMD

Booting a vJunos-switch should not leave enough time to make coffee, drink it, and start questioning your life choices. Yet this is roughly where I was with one of my nested labs: **15 minutes and 24 seconds** from starting the container to a healthy Junos node.

After three small patches to the Junos startup script, the same node became healthy in **3 minutes and 44 seconds**. A repeat run took **3 minutes and 28 seconds**. No hardware was upgraded in the process. In fact, the biggest improvement came from giving Junos *fewer* vCPUs.

The credit for the important discoveries goes to Piet Braat and his excellent post [Defying the 'Impossible': Getting Nested vJunos-switch Running on AMD Epyc](https://www.linkedin.com/pulse/defying-impossible-getting-nested-vjunos-switch-running-piet-braat-i9d4e/). Piet ignored the usual "nested vJunos will never work" advice, dug into the guest, and documented the CPU-counting bug and the QEMU debugger setup. My part was to reproduce his findings with [Boxen](https://boxen.containerlab.dev/), time each change, and package the result so that I would not have to hand-edit disks again.

This post has the full journey, including a change that did not help and an extra vCPU that made things worse.

<!-- more -->

## Wait, how many hypervisors?

vJunos-switch is not just one VM. The outer Linux VM runs the dataplane and starts another QEMU process for the Junos control plane. Boxen then packages and starts that outer VM in a container.

My lab host is itself a cloud VM, which makes the whole arrangement look like this:

| Layer | What runs there | vCPUs |
| --- | --- | ---: |
| L0/L1 | Physical host and Nebius KVM hypervisor | Not exposed |
| L2 | Cloud VM running Docker and Boxen | 16 |
| L3 | Outer vJunos-switch VM started by Boxen | 4 |
| L4 | Nested Junos control-plane VM | 5 before the fix, 1 after it |

Turtles, hypervisors, all the way down.

Here is the CPU that the cloud VM exposed to me:

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

The generic `AMD EPYC-Genoa Processor` name is what QEMU exposes to the guest, so it does not identify a particular retail EPYC SKU.

## The first AMD problem: SVM

The original outer Linux VM checked only for Intel VMX:

```bash
CPU_FLAG=$(cat /proc/cpuinfo | grep -ci "vmx")
```

On an AMD machine this check failed, and `/home/pfe/junos/start-junos.sh` helpfully shut everything down. Boxen already patched it to accept both Intel and AMD virtualization flags:

```bash
CPU_FLAG=$(cat /proc/cpuinfo | grep -Eci "vmx|svm")
```

That patch came from the earlier [MarcsTech vJunos-switch AMD workaround](https://marcstech.blog/archives/juniper-vjunos-switch-amd-cpu-containerlab/). It got me past the shutdown, but the boot was still painfully slow.

Piet's article had two more leads: a mysterious `-S` QEMU flag and a monitor process that attached `strace` to the nested VM. Time to measure instead of guessing.

## A paused CPU that was not the main problem

The inner QEMU command started like this:

```bash
/usr/bin/qemu-system-x86_64 \
 -S \
 -daemonize \
 -name vcp-vmx1 \
 ...
```

QEMU's documentation describes `-S` as:

> Do not start CPU at startup (you must type 'c' in the monitor).

In other words, start paused and wait for a debugger. Not exactly what I need for a regular lab node.

I built a new image with only the ` -S \` line removed. I also checked the complete script diff to make sure that I had not accidentally included another experiment. The node booted fine, but the timing was a little underwhelming:

| Image | Launch to healthy |
| --- | ---: |
| Original | 924 seconds — 15m24s |
| `-S` removed | 943 seconds — 15m43s |

Nineteen seconds *slower*. That is run-to-run noise, not a regression worth chasing, but certainly not the breakthrough I was hoping for.

## Next suspect: the strace monitor

Right after starting the nested VM, `start-junos.sh` launched `qemu_monitor.sh`. The monitor found the QEMU PID and attached `strace` to it:

```bash
/usr/bin/strace -e none -e exit_group -p "$PID"
```

For the next run I removed both `-S` and the line that started `qemu_monitor.sh`.

One subtlety: deleting only the `strace` command is a bad idea. The rest of the monitor script would continue, decide that QEMU had exited, and shut down the outer VM. Debugger removal needs a tiny bit of precision.

This combination produced the first useful improvement:

| Image | Junos vCPUs | Launch to healthy | Change from original |
| --- | ---: | ---: | ---: |
| Original | 5 | 924 seconds | — |
| `-S` removed | 5 | 943 seconds | +2.1% |
| `-S` and strace monitor removed | 5 | 782 seconds — 13m02s | −15.4% |

Two minutes saved is nice. Thirteen minutes is still far too long, though. The article had one more clue, and it turned out to be the big one.

## Four vCPUs walk in, eight processors come out

The startup script decides how many vCPUs the nested Junos VM gets with this bit of shell:

```bash
totalcpu=$(cat < /proc/cpuinfo | grep -csi "processor")

if [ "$totalcpu" -le 3 ]; then
   VCPCPU=1
else
   VCPCPU=$((totalcpu-3))
fi
```

Three CPUs are reserved for the dataplane, and the rest go to Junos. With a four-vCPU outer VM, Junos should therefore get one.

Except `grep -i "processor"` does not only match the actual processor entries on my AMD guest. It also matches the model name:

```text
processor : 0
model name : AMD EPYC-Genoa Processor
```

Every real vCPU was counted twice. Four outer vCPUs became eight matches, and the script then calculated `8 - 3 = 5` vCPUs for Junos.

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

Now the model name stays a model name, `totalcpu` is four, and Junos gets the intended single vCPU.

## All the numbers

I timed every run from container launch until Boxen wrote `0 running` to `/health`. This is deliberately the full user-visible wait: both VM layers boot, Junos reaches its CLI, Boxen applies the runtime configuration, and the configuration commit finishes.

Each test used a fresh container with the same 5120 MiB of memory and network settings. Only one test VM ran at a time. The outer VM had four vCPUs unless the table says otherwise.

| Variant | Outer vCPUs | Junos vCPUs | Junos prompt | Launch to healthy | After prompt |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 4 | 5 | 819s | **924s — 15m24s** | 105s |
| `-S` removed | 4 | 5 | 835s | **943s — 15m43s** | 108s |
| `-S` and strace monitor removed | 4 | 5 | 707s | **782s — 13m02s** | 75s |
| CPU-count fix only | 4 | 1 | 306s | **329s — 5m29s** | 23s |
| All three fixes | 4 | 1 | 205s | **224s — 3m44s** | 19s |
| All three fixes, repeat | 4 | 1 | 189s | **208s — 3m28s** | 19s |
| All three fixes with `QEMU_SMP=5` | 5 | 2 | 236s | **246s — 4m06s** | 10s |

The CPU-count-only row was a deliberate ablation test: `-S` and the strace monitor were still enabled. That one-character CPU fix accounted for most of the total improvement by itself. Removing `-S` and the monitor then cut another 105 seconds from the first CPU-fix run.

The two complete-fix runs at four outer vCPUs differed by 16 seconds. These were sequential tests on one shared host, not a statistically rigorous benchmark, so I would not read anything into a few seconds either way. The difference between 924 and roughly 216 seconds is thankfully a little harder to explain away as noise.

## Is five outer vCPUs better than four?

Once the boot got faster, the natural next question was whether one more outer vCPU would make it faster still. More cores fixes everything, right?

With the corrected counting logic, five outer vCPUs produce **two** Junos vCPUs:

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

Manual `virt-edit` sessions are good for an experiment and bad for repeatability. Both the `juniper_vjunos-switch` and `juniper_vjunos-router` Boxen profiles now patch `start-junos.sh` while packaging the image. They:

1. accept Intel VMX or AMD SVM;
2. count only lines beginning with `processor`;
3. remove the nested QEMU `-S` option;
4. stop launching the `qemu_monitor.sh` strace monitor.

Every substitution is idempotent. Applying the packaging command to an unpatched image fixes everything; applying it to an already patched image changes nothing.

The router profile also switched from a `guestfish` command with a hardcoded `/dev/sda2` mount to the same partition-agnostic `virt-edit` form used by the switch profile. Both platforms patch the same guest script. Only vJunos-switch was benchmarked here, so I am not claiming an independently measured router improvement.

The changes are in [Boxen PR #103](https://github.com/carlmontanari/boxen/pull/103). I extracted the patch script from the committed YAML and ran it against the original disk to verify that it produced exactly the benchmarked script. `make fmt`, `make lint`, `make test`, and the strict docs build all pass as well.

## Final kudos

The appealing answer to a slow VM is always more CPU, more memory, or a bigger host. Here the answer was four small packaging patches, one of which *reduced* the nested VM from five vCPUs to one.

And the reason I knew where to look was [Piet Braat's original post](https://www.linkedin.com/pulse/defying-impossible-getting-nested-vjunos-switch-running-piet-braat-i9d4e/). His write-up turned a vague "nested vJunos is impossibly slow on AMD" problem into concrete, testable fixes. Big kudos to him for doing the investigation and sharing it instead of keeping the working setup to himself.

My vJunos-switch is now usable for iterative labs on this AMD host: four outer vCPUs, one Junos vCPU, no paused start, no debugger, and about eleven and a half minutes back every time a node boots.
