---
date: 2017-10-29
comment_id: wait-ssh-paramiko
keywords:
- paramiko
- python
tags:
- paramiko
- python

title: Waiting for SSH service to be ready with Paramiko

---

Today I faced a task which required first to establish an SSH tunnel in a background process and later use this tunnel for SSH connection. What seemed like a child's play first actually had some fun inside.

A problem were hidden right between the moment you spawned `ssh` process in the background and the next moment you tried to use this tunnel. In other words, it takes literally no time to spawn a process in the background, but without checking that tunnel is ready, you will quite likely receive an error, since your next instructions will be executed immediately after.

Consequently, I needed a way to ensure that the SSH service is ready before I try to consume it.

<p align=center>
<img src="https://gitlab.com/rdodin/netdevops.me/uploads/584a84f21b9736016c5c2b140f5fab58/image.png"/>
</p>


<!--more-->

But how do you check if there is a server behind some `host:port` and that this server is of SSH nature? In Ansible we could leverage `wait_for` module that can poke a socket and see if OpenSSH banner is there. But in my case Python & [Paramiko](http://www.paramiko.org/) was all I had.

It turned out that with Paramiko it is possible to achieve the goal with most straightforward and probably least elegant code:

{{< gist hellt 6e5b657de8e504b60b56db252e1204e6 >}}

I found it sufficient to setup a timer-driven _while loop_ where Paramiko tries to open a connection without credentials. In order to detect if socket is opened I catch different type of exceptions that Paramiko emits:

* if there is nothing listening on a particular socket, then Paramiko emits `paramiko.ssh_exception.NoValidConnectionsError`
* if the socket is open, but the responding service is not SSH, then Paramiko emits `paramiko.ssh_exception.SSHException` with a particular message _Error reading SSH protocol banner_
* if the socket is open and SSH service responding on the remote part - **we are good to go**! This time still `paramiko.ssh_exception.SSHException` is emitted, but the error message would be _No authentication methods provided_.

And that quite does the trick:

<p align=center>
<img src="https://gitlab.com/rdodin/netdevops.me/uploads/744680ad94fe0d7fc6cbb3aaf475b400/wait_ssh.gif"/>
</p>

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>