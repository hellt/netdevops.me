---
date: 2017-07-25
comments: true
tags:
- git

title: How to count lines of code in a git repo?

---



Nothing bad in knowing how many lines of code or text out there in your repo. You don't even need your VCS to convey this analytics. All you need is `git`, `grep` and `wc`.

```bash
# count lines in .py and .robot files in /nuage-cats dir of the repo
$ git ls-files nuage-cats/ | grep -E ".*(py|robot)" | xargs wc -l
       0 nuage-cats/robot_lib/__init__.py
     817 nuage-cats/robot_lib/lib/NuageQoS.py
     409 nuage-cats/robot_lib/lib/NuageVCIN.py
    1841 nuage-cats/robot_lib/lib/NuageVNS.py
    2964 nuage-cats/robot_lib/lib/NuageVSD.py
    # OMITTED
      26 nuage-cats/test_suites/0910_fail_bridges_kvm_vms/0910_fail_bridges_kvm_vms.robot
   13636 total
```
