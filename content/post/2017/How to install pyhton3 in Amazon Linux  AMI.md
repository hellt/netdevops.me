---
date: 2017-08-20T12:00:00Z
comment_id: py3-aws
keywords:
- AWS
- python
tags:
- AWS
- python

title: How to install python3 in Amazon Linux AMI

---

While [Amazon Linux AMI](https://aws.amazon.com/amazon-linux-ami/) has `yum` as a package manager, it is not that all compatible with any RHEL or CentOS distributive. A lot of changes that AWS team brought into this image made it a separate distro, so no eyebrows should be given when battle-tested procedure to install python3 will fail on Amazon Linux. (Yeah, python3 does not come included yet in Amazon Linux)

<!--more-->

Fortunately it is very easy to fetch (while not the latest release) python3:

```bash
# list available packages that have python3 in their name
yum list | grep python3

# install python3+pip, plus optionally packages to your taste
sudo yum install python35 python35-devel python35-pip python35-setuptools python35-virtualenv

# update pip3. optionally set a symbolic link to pip3
sudo pip-3.5 install --upgrade pip
```

And that is it!