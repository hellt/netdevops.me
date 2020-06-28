---
date: 2018-11-23T12:00:00Z
comment_id: ftp-saturation
keywords:
- FTP
- vsftpd
tags:
- vsftpd
- FTP

title: Saturating the network with FTP

---

While working on the [Ipanema Wan Opt VNF](https://www.infovista.com/products/ipanema-sdwan) integration with [Nuage Networks](http://www.nuagenetworks.net/enterprise/software-defined-wan/) I stumbled upon an interesting case which required to max out the network with FTP traffic. The tricky point there was to create the FTP connection which won't be limited by the disk IO performance. Especially, considering that the disks were kind of slow in the setup I had.

It turns out, you can use the in-memory devices in the FTP communication path `/dev/zero -> /dev/null`, ruling out the slowliness that could have been added by the disks. Lets figure out how to do that!

<!--more-->

Software-wise my setup consisted of a single FTP server `vsftpd` and the FTP client `ftp` all running on Centos7-based VMs. These VMs were equipped with a network namespace `ns-data` which host the datapath interface `eth1`.

## /dev/zero -> /dev/null
I found this ["ftp to dev null to test bandwidth"](https://fordodone.com/2013/11/13/ftp-to-dev-null-to-test-bandwidth/) blog post explaining how to use `/dev/zero` as a source file and `/dev/null` as a destination within a running FTP session.

The example there (executed on the FTP client side) demonstrates the following technique:

```bash
#!/bin/bash
/usr/bin/ftp -n <IP address of machine> <<END
verbose on
user <username> <password>
bin
put "|dd if=/dev/zero bs=32k" /dev/null
bye
END
```
So this example did not work for me right out of the box so let me augment it with the few findings I came across while trying to make this one work.

## vsftpd configuration
The `put "|dd if=/dev/zero bs=32k" /dev/null` command is the transfer operation from the client to the server. On the server side the data that comes from the client is saved in `/dev/null` device.

First thing to check there is that your FTP server configuration allows a client to use the `dev/null` device as the destination. I used the `vsftpd` as a server, so the config that worked for me (using the local user authentication) is as follows:

```bash
# cat /etc/vsftpd/vsftpd.conf
anonymous_enable=NO
local_enable=YES
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
anon_world_readable_only=YES
connect_from_port_20=YES
hide_ids=YES
pasv_min_port=40000
pasv_max_port=60000
local_umask=022
dirmessage_enable=YES
xferlog_enable=YES
xferlog_std_format=YES
listen=YES
xferlog_enable=YES
ls_recurse_enable=NO
ascii_download_enable=NO
async_abor_enable=YES
one_process_model=NO
idle_session_timeout=120
data_connection_timeout=300
accept_timeout=60
connect_timeout=60
pam_service_name=vsftpd
tcp_wrappers=YES
```

This enables me to authenticate using the local user credentials on the server and write the data to the `/dev/null` device.

## 500 OOPS: ftruncate
Once I found the workable vsftpd config, I run the script and received `500 OOPS: ftruncate` error from the server. This problem, as it seems, only affects RHEL-based distros, and as explained [here](https://access.redhat.com/solutions/776843) the workaround is to use `append` command instead of a `put`.

This brings me to the final version of the script I used:

```bash
# cat ./ftp.sh
#!/bin/bash
ip netns exec ns-data /usr/bin/ftp -n 192.168.99.101 <<END
verbose on
user myuser mypassword
bin
append "|dd if=/dev/zero bs=32k" /dev/null
bye
END
```

And the result I got on the 10Mbps uplinks:
```bash
$ sudo bash ftp.sh
Verbose mode on.
331 Please specify the password.
230 Login successful.
200 Switching to Binary mode.
local: |dd if=/dev/zero bs=32k remote: /dev/null
227 Entering Passive Mode (192,168,99,101,222,205).
150 Ok to send data.
^C277+0 records in
276+0 records out
9043968 bytes (9.0 MB) copied, 7.06165 s, 1.3 MB/s

send aborted
waiting for remote to finish abort
226 Transfer complete.
8986624 bytes sent in 7.03 secs (1278.00 Kbytes/sec)
221 Goodbye.
```
And this saturates my uplinks completely.

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>