---
date: 2018-03-25T12:00:00Z
keywords:
- AWS
tags:
- AWS

title: Uploading multiple files to AWS S3 in parallel

---

When it comes to uploading multiple small/medium files to AWS S3 a regular user might face slow upload speeds when it is triggered through AWS Management Console. Recently I tried to upload 4k html files and was immediately discouraged by the progress reported by AWS Console upload manager. It was something close to 0.5% per 10s. Clearly, the choke point was the network (as usual, brothers!).

Comer here, Google, we need to find a better way to handle this kind of upload.

<!--more-->

To set context, take a look at file size distribution I had (thanks to this [awk magic](https://superuser.com/questions/565443/generate-distribution-of-file-sizes-from-the-command-prompt)):

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

My thought was that maybe there is a way to upload tar.gz archive and unpack it in S3 bucket, unfortunately this is not supported by S3. The remaining options were ([as per this SO thread](https://stackoverflow.com/questions/28291466/how-to-extract-files-from-a-zip-archive-in-s3)):

> 1. You could mount the S3 bucket as a local filesystem using s3fs and FUSE (see article and github site). This still requires the files to be downloaded and uploaded, but it hides these operations away behind a filesystem interface.

> 2. If your main concern is to avoid downloading data out of AWS to your local machine, then of course you could download the data onto a remote EC2 instance and do the work there, with or without s3fs. This keeps the data within Amazon data centers.

> 3. You may be able to perform remote operations on the files, without downloading them onto your local machine, using AWS Lambda.

Hands down, these three methods could give you the best speeds, since you could upload tar archive and do the heavy lifting on the AWS side. Anyway, none of them were quite appealing to me for that one-time upload I needed to handle. I hoped to find kind of a parallel way of multiple uploads with a CLI approach.

So what I found boiled down to the following CLI-based workflows:

1. `aws s3 rsync` command
2. `aws cp` command with `xargs` to act on multiple files
3. `aws cp` command with `parallel` to act on multiple files

TL;DR: First option won the competition, but lets have a look at numbers. I created 100 files 4096B each and an empty test bucket to do the tests:

```bash
# create 100 files size of 4096 bytes each
seq -w 1 100 | xargs -n1 -I% sh -c 'dd if=/dev/urandom of=file.% bs=1 count=4096'
```

```bash
$ find . -type f -print0 | xargs -0 ls -l | awk '{size[int(log($5)/log(2))]++}END{for (i in size) printf("%10d %3d\n", 2^i, size[i])}' | sort -n

      4096 100
```

### 1. AWS Management Console
As a normal human being I selected all these 100 files in the file dialog of AWS Management Console and waited for **5 minutes** to upload 100 of them. Horrible.

> The rest of the tests were run on an old 2012 MacBook Air with 4vCPUs.

### 2. aws s3 sync
`aws s3 sync` command is cool when you only want to upload the missing files or make the remote part in sync with a local one. In case when a bucket is empty a sequential upload will happen, but will it be fast enough?

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

5 mins! As bad as AWS Management Console way!

### 4. aws s3 cp with parallel

`parallel` is a [GNU tool to run parallel shell commands](https://www.gnu.org/software/parallel/parallel_tutorial.html).

```
# parallel with 60 workers
ls -1 | time parallel -j60 -I % aws s3 cp % s3://test-ntdvps --profile rdodin-cnpi
39.32 real       108.41 user        14.46 sys
```

~40 seconds, better than `xargs` and worse than `aws s3 sync`. With number of files increasing `aws s3 sync` starts to win more, and the reason is I think is that `aws s3 sync` uses one tcp connection, while `aws s3 cp` opens new connection with each files passed.

### 5. What if I had more CPU cores?
You can increase the number of the workers, and if you have a solid amount of threads available you might win the competition:

```
# 48 Xeon vCPUs, same 100 files 4KB each

aws s3 sync: 6.5 seconds
aws s3 cp with parallel and 128 jobs: 4.5 seconds

# now 1000 files 4KB each
aws s3 sync: 40 seconds
aws s3 cp with parallel and 252 jobs: 21.5 seconds
``` 

So you see that `aws s3 cp` with `parallel` might come handy if you have enough of vCPU to handle that many parallel workers. But if you are sending files from a notebook, `aws s3 sync` will usually be a better choice.

> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/6).