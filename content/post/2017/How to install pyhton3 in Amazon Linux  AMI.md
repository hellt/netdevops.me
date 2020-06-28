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

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>