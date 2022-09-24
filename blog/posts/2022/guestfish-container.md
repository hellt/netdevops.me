---
date: 2022-02-22
comments: true
tags:
  - guestfish
---
# Using guestfish container image

Once in a while, one still needs to get down to a VM-land and dust off some guestfish skills.

Like today I got the IPInfusion OcNOS `qcow2` image whose devs decided it is best to use VNC console by default. VNC console for a text-based terminal...

So along come guestfish commands.

<!-- more -->

It is hugely satisfying to modify the VM images using containers, so here are my two commands to modify GRUB settings.

I first check the initial grub content, then swap it with a modified one (with a serial console, right?). Clean, fast, 🧑‍🍳

```bash
# show image's file contents

DISK_IMG=/tmp/ocnos.qcow2
DISK_DIR=$(dirname ${DISK_IMG})
DISK_NAME=$(basename ${DISK_IMG})

docker run -i --rm \
  -v ${DISK_DIR}:/work/${DISK_DIR} \
  -w /work/${DISK_DIR} \
  bkahlert/libguestfs \
  guestfish \
  --ro \
  --add ${DISK_NAME} \
  --mount /dev/sda1:/ \
  cat /etc/default/grub
```

```bash
# copy-in a file

LOCAL_FPATH=/tmp/ocnos-newgrub
REMOTE_FPATH=/etc/default/grub

docker run -i --rm \
  -v ${DISK_DIR}:/work/${DISK_DIR} \
  -v ${LOCAL_FPATH}:/work${LOCAL_FPATH} \
  -w /work/${DISK_DIR} \
  bkahlert/libguestfs \
  guestfish \
  --rw \
  --add ${DISK_NAME} \
  --mount /dev/sda1:/ \
  upload /work${LOCAL_FPATH} ${REMOTE_FPATH}
```
