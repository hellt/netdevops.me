---
date: 2020-01-28T06:00:00Z
comment_id: netconf-console-docker
keywords:
- netconf
- docker
tags:
- Netconf
- Docker

title: NETCONF console in a docker container
---
Its an engineers core ability to decompose a complex task in a set of a smaller, easy to understand and perform sub-tasks. Be it a feature-rich program that is decomposed to classes, functions and APIs or a huge business operation captured in steps in a *Methods Of Procedure* document.

In a network automation field where the configuration protocols such as NETCONF or gRPC are emerging, it is always needed to have a quick way to validate an *RPC* or *Notification* feature before implementing this in a code or a workflow.

This blog post is about a handy tool called [`netconf-console`](https://pypi.org/project/netconf-console/) which allows you to interface with your network device using NETCONF quick and easy. And, of course, I packed it in a smallish container so you can enjoy it hassle-free on every docker-enabled host.
<!--more-->

[`netconf-console`](https://pypi.org/project/netconf-console/) is a tool from Tail-f that basically gives you a NETCONF client for your console. That is exactly the packaging that I appreciate to have when I need to play with NETCONF. Cold-starting a python project with `ncclient` is much slower and you need ensure that you have all the RPCs coded, meh. With the console client you have almost anything you need to start tinkering with NETCONF enabled device.

```
# netconf-console --host=example.com --db candidate --lock --edit-config=fragment1.xml \
--rpc=commit-confirmed.xml --unlock --sleep 5 --rpc=confirm.xml
```

Moreover, you can have an interactive NETCONF console to your device:

```
# netconf-console --host=example.com -i
netconf> lock
netconf> edit-config fragment1.xml --db candidate
netconf> rpc commit-confirmed.xml
netconf> unlock
netconf> get-config
netconf> rpc confirm.xml
```

## Containerize
I've been spoiled by Rust/Go tools that are self-contained, dependency-free and almost platform-agnostic. To achieve the same level of hassle-free for python tool I practice containerization.

So I decided to put `netconf-console` in a whale protected cage by building a multi-stage docker image. Even though there are [some](https://hub.docker.com/search?q=netconf%20console&type=image) images for the netconf-console, they are all outdated, based on an old version of the tool and use python2 under the hood. Its 2020 here, so I wanted to create a fresh, small image based off of the recent netconf-console code and running with python3.

So here it is, a multi-stage build [Dockerfile](https://github.com/hellt/netconf-console-docker/blob/master/Dockerfile) that builds `netconf-console` in Alpine linux with python3.7.  
The result of this build can be found at the relevant [docker hub page](https://hub.docker.com/repository/docker/hellt/netconf-console).

### Tags
The docker image will be tagged in accordance with the relase verion numbers of the `netconf-console`; at the time of this writing, the latest version is `2.2.0`, hence you will find the image with the corresponding tag. Also, the `latest` tag will point to the most recent version.

## Installation
As with any other docker image, all it takes is to make a pull:

```
docker pull hellt/netconf-console
```

## Usage examples
The entry point of the docker image is the netconf-console itself, therefore you can run it almost in the same way as you'd do with a standalone installation - by providing the arguments to the callable.
```bash
# verify that the tool is properly working,
docker run --rm -it hellt/netconf-console --help

usage: netconf-console [-h] [-s [{plain,noaaa} [{plain,noaaa} ...]]] [--db DB]
                       [--timeout TIMEOUT]
                       [--with-defaults {explicit,trim,report-all,report-all-tagged}]
                       [--with-inactive] [-x XPATH]
                       [-t {test-then-set,set,test-only}]
                       [-o {merge,replace,create}]
                       [--del-operation {remove,delete}] [-v VERSION]
                       [-u USERNAME] [-p [PASSWORD]] [--host HOST]
                       [-r REPLY_TIMEOUT] [--port PORT]
                       [--privKeyFile PRIVKEYFILE] [--raw [RAW]] [--tcp]
                       [-N [NS [NS ...]]] [--debug] [--hello] [--get [GET]]
                       [--get-config [GET_CONFIG]] [--kill-session SESSION_ID]
                       [--discard-changes] [--lock] [--unlock]
                       [--commit [{confirmed}]] [--validate [VALIDATE]]
                       [--copy-running-to-startup]
                       [--copy-config [COPY_CONFIG]]
                       [--edit-config [EDIT_CONFIG [EDIT_CONFIG ...]]]
                       [--set [SET [SET ...]]]
                       [--delete [DELETE [DELETE ...]]]
                       [--create [CREATE [CREATE ...]]]
                       [--get-schema GET_SCHEMA]
                       [--create-subscription [CREATE_SUBSCRIPTION]]
                       [--rpc [RPC]] [--sleep SLEEP] [-e EXPR] [--dry]
                       [--interactive]
                       [filename]
```

The interactive console mode, of course, also works:

```bash
docker run -it --rm hellt/netconf-console --host=10.1.0.11 --port=830 -u admin -p admin -i
netconf> hello
<?xml version='1.0' encoding='UTF-8'?>
<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:capabilities>
    <nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:base:1.1</nc:capability>
<<SNIPPED>>
```

Now a more real-life example would be to throw a NETCONF RPC to the target device:

```xml
$ cat test.xml
<rpc message-id="113" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get>
    <filter>
      <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
        <system>
          <security>
            <user-params>
              <local-user>
		            <user/>
	            </local-user>
            </user-params>
          </security>
        </system>
      </state>
    </filter>
  </get>
</rpc>
```
```xml
$ docker run -it --rm -v $(pwd):/rpcs hellt/netconf-console --host=10.1.0.11 --port=830 -u admin -p admin /rpcs/test.xml
<?xml version='1.0' encoding='UTF-8'?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="113">
    <data>
        <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <attempted-logins>13</attempted-logins>
                                <failed-logins>0</failed-logins>
                                <locked-out>false</locked-out>
                                <password-changed-time>2020-01-24T23:27:33.0Z</password-changed-time>
                            </user>
                            <user>
                                <user-name>grpc</user-name>
                                <attempted-logins>0</attempted-logins>
                                <failed-logins>0</failed-logins>
                                <locked-out>false</locked-out>
                                <password-changed-time>2020-01-24T23:27:35.0Z</password-changed-time>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </state>
    </data>
</rpc-reply>
```

And you can create pretty complex ad-hoc RPCs with locking the datastore, commiting and discarding the changes effortlessly.