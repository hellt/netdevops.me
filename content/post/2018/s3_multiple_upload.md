---
date: 2018-03-25T12:00:00Z
comment_id: s3-multiupload
keywords:
- AWS
tags:
- AWS

title: Uploading multiple files to AWS S3 in parallel

---

Have you ever tried to upload thousands of small/medium files to the AWS S3? If you had, you might also noticed ridiculously slow upload speeds when the upload was triggered through the AWS Management Console. Recently I tried to upload 4k html files and was immediately discouraged by the progress reported by the AWS Console upload manager. It was something close to the 0.5% per 10s. Clearly, the choke point was the network (as usual, brothers!).

Comer here, Google, we need to find a better way to handle this kind of an upload.

<!--more-->

To set a context, take a look at the file size distribution I had (thanks to this [awk magic](https://superuser.com/questions/565443/generate-distribution-of-file-sizes-from-the-command-prompt)):

```
  Size, KB   Num of files
       256   2
       512   2
      1024   8
      2048 1699
      4096 1680
      8192 579
     16384 323
     32768 138
     65536  34
    131072   6
    262144   1
   1048576   1
   2097152   1
   4194304   1
```

My thought was that maybe there is a way to upload a tar.gz archive and unpack it in an S3 bucket, unfortunately this is not supported by the S3. The remaining options were ([as per this SO thread](https://stackoverflow.com/questions/28291466/how-to-extract-files-from-a-zip-archive-in-s3)):

> 1. You could mount the S3 bucket as a local filesystem using s3fs and FUSE (see article and github site). This still requires the files to be downloaded and uploaded, but it hides these operations away behind a filesystem interface.

> 2. If your main concern is to avoid downloading data out of AWS to your local machine, then of course you could download the data onto a remote EC2 instance and do the work there, with or without s3fs. This keeps the data within Amazon data centers.

> 3. You may be able to perform remote operations on the files, without downloading them onto your local machine, using AWS Lambda.

Hands down, these three methods could give you the best speeds, since you could upload tar archive and do the heavy lifting on the AWS side. But none of them were quite appealing to me considering the one-time upload I needed to handle. I hoped to find kind of a parallel way of the multiple uploads with a CLI approach.

So what I found boiled down to the following CLI-based workflows:

1. `aws s3 rsync` command
2. `aws cp` command with `xargs` to act on multiple files
3. `aws cp` command with `parallel` to act on multiple files

TL;DR: First option won the competition (# of cores matters), but lets have a look at the numbers. I created 100 files 4096B each and an empty test bucket to do the tests:

```bash
# create 100 files size of 4096 bytes each
seq -w 1 100 | xargs -n1 -I% sh -c 'dd if=/dev/urandom of=file.% bs=1 count=4096'
```

```bash
$ find . -type f -print0 | xargs -0 ls -l | awk '{size[int(log($5)/log(2))]++}END{for (i in size) printf("%10d %3d\n", 2^i, size[i])}' | sort -n

      4096 100
```

### 1. AWS Management Console
As a normal human being I selected all these 100 files in the file dialog of the AWS Management Console and waited for **5 minutes** to upload 100 of them. Horrible.

> The rest of the tests were run on an old 2012 MacBook Air with 4vCPUs.

### 2. aws s3 sync
A `aws s3 sync` command is cool when you only want to upload the missing files or make the remote part in sync with a local one. In case when a bucket is empty a sequential upload will happen, but will it be fast enough?

```bash
time aws s3 sync . s3://test-ntdvps

real	0m10.124s
user	0m1.470s
sys	0m0.273s
```

10 seconds! Not bad at all!

### 3. aws s3 cp with xargs

```
ls -1 | time xargs -I % aws s3 cp % s3://test-ntdvps
294.05 real        68.76 user         9.27 sys
```

5 mins! As bad as the AWS Management Console way!

### 4. aws s3 cp with parallel

`parallel` is a [GNU tool to run parallel shell commands](https://www.gnu.org/software/parallel/parallel_tutorial.html).

```
# parallel with 60 workers
ls -1 | time parallel -j60 -I % aws s3 cp % s3://test-ntdvps --profile rdodin-cnpi
39.32 real       108.41 user        14.46 sys
```

~40 seconds, better than `xargs` and worse than `aws s3 sync`. With an increasing number of the files `aws s3 sync` starts to win more, and the reason is probably because `aws s3 sync` uses one tcp connection, while `aws s3 cp` opens a new connection for an each file transfer operation.

### 5. What if I had some more CPU cores?
You can increase the number of the workers, and if you have a solid amount of threads available you might win the upload competition:

```
# 48 Xeon vCPUs, same 100 files 4KB each

aws s3 sync: 6.5 seconds
aws s3 cp with parallel and 128 jobs: 4.5 seconds

# now 1000 files 4KB each
aws s3 sync: 40 seconds
aws s3 cp with parallel and 252 jobs: 21.5 seconds
``` 

So you see that the `aws s3 cp` with `parallel` might come handy if you have enough of vCPUs to handle that many parallel workers. But if you are sending your files from a regular notebook/PC the `aws s3 sync` command will usually be of a better choice.

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>