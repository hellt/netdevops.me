---
date: 2021-02-01T06:00:00Z
comment_id: git-remove-big-files
keywords:
- git
tags:
- git

title: Remove binaries and big files from git repo
---
You slice and dice your files in a git repo like a pro and accidentally commit a binary file. It happened to you as well, don't pretend it didn't.  
Sooner or later you recognizes this file shouldn't be there, it is clogging your git repo for no reason. OK, you delete the file and commit. But the repo size doesn't get any smaller. Hm...
<!--more-->

Indeed, next time you do `git clone` you are wondering why your repo is still megabytes in size, while it has just some source code files?

The thing is, by just deleting the file from your working tree and committing this action you don't make things any better. This large file still sits somewhere in `.git` directory waiting for you to rewind the history back and get it. The problem though is that you want this file gone for good.

### 0 TLDR
All the tags, branches are preserved with this procedure, although I do not guarantee that the workflow will work in your case. Do a backup always.

```bash
# clone a repo with --mirror flag and change into it
git clone --mirror <repo-url>

# launch cleanup process
git filter-repo --strip-blobs-bigger-than 3M

# run GC
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# update the more
git push
```

### 1 Show me big files
To see if your repo holds those monster files you can leverage some git commands, but I found [this self-contained python script](https://gist.github.com/malcolmgreaves/39e33e9b161916cb92ae0fdcfea91d64) quite a good fit for the purpose:

```bash
❯ ./lf.py -c 20
Finding the 20 largest objects…
Finding object paths…

All sizes in kB. The pack column is the compressed size of the object inside the pack file.

size   pack  hash                                      path
6769   6761  82d233ab6ff841f16bd17c2b5a6906ccdd8af8e5  rpm/tool-1.0.0.x86_64.rpm
13439  6723  dbd32fc21381cf1e4cb0ba964f53aff1ebcc8547  bin/tool
12437  6223  967237f169780b8660a771c6f478de1d93822157  bin/tool
12413  6211  dfd93506fa17401cc996223337b8372bf921887e  bin/tool
11776  5917  f35577a72a2493b00c6e0520d1454d9fdaedb886  bin/tool
5646   5638  66cc7eb29577bb84aaa682dd1eb694fde1d9e399  rpm/tool-1.0.0.x86_64.rpm
5944   4073  360106b01776e4e7419ab414878d582747d7c945  bin/tool-test
5333   3899  53ef404d20a09db9040696eeb5df5bebf10ecf52  bin/tool
4985   3569  1d81eafd70736f568526b7e5221478b5b3e67c6d  bin/tool
4111   3224  acfd2077e642272c2ab09cbfaf435b4fc91ac012  bin/tool
4018   3205  f331cec6b0e599dfbef7361c947a14beea7ce4c2  bin/tool
3849   3111  8bb4fdaeccecf1ef0a91fc780c243cb89109597a  bin/tool
655    456   393dadfa6f5957f60a42287ed2c6e7ddcd5688cc  bin/tool
```

Nice and easy we get 20 largest files which I have no intention to keep and they make the size of the repo to be in 70MB range with compression. No good.

### 2 Removing large files
#### 2.1 Beware of consequences
Now to the fun part, lets remove those files, making our repo fit again!

One problem, though, it's not that easy. First of all, this operation is very intrusive. As Git stores the commits in a graph fashion, you can't change some commit in the middle, without rewriting the commits after it.

So be prepared, that all the commits will eventually have new hashes. Evaluate the consequences and implications of it.

#### 2.2 Procedure
If you start searching, you will find many workflows, dating back to early 2000s and git 1.x. I tried them and I regret.
Eventually I found the working combination that I tested on two of my repos and they worked flawlessly.

##### 2.2.1 Make a backup
Do a backup of your original repo

##### 2.2.2 Clone a mirror
Now clone the repo with a `--mirror` option. That step is very important. You will have your repo cloned under `<repo-name>.git` directory, but you won't see actual files, instead you will have the git database of this repo.

##### 2.2.3 Install git-filter-repo
The actual tool that does the job is called [git-filter-repo](https://github.com/newren/git-filter-repo). It is a successor to *git-filter-branch* and *BFG Repo Cleaner*.

There is the [Install](https://github.com/newren/git-filter-repo/blob/main/INSTALL.md) document, but it is written somehow complex. The easy way to install for me was copying the [raw script](https://github.com/newren/git-filter-repo/blob/main/git-filter-repo) and copying it under the directory that `git --exec-path` command outputs.

##### 2.2.4 Run the cleanup
Then you can read about the options this script supports, for me I chose the easiest path possible -- delete every file that is bigger than X Megabytes. So I entered the directory that appeared after I did `git clone --mirror` and executed the following command:

```
git filter-repo --strip-blobs-bigger-than 3M
```

For my no-so-big repo with 500 commits, it finished in under a second. It removed all the files bigger than 3Megs and re-wrote all the commits that were affected by that change.

##### 2.2.5 Garbage collect
We are not done yet. Although the files were removed for good, we still need to tell git to run a garbage collection procedure to forget about those missing files:

```
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

##### 2.2.6 Update the remote
Now the final part. We are ready to update the remote with our new git history. Interesting enough it is done with a simple

```
git push
```

no `force` is needed ¯\_(ツ)_/¯


> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>