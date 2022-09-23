---
date: 2020-02-01
comment_id: netconf-xml-skeleton
keywords:
- netconf
- docker
- yang
tags:
- Netconf
- Docker
- YANG

title: Getting XML data sample for a given leaf in a YANG model
---
We can praise YANG as long as we want, but for an end user YANG is useful as the tooling around it and the applications leveraging it. Ask yourself, as a user of any kind of NETCONF/YANG application what was the last time you looked at a `*.yang` file content and found something that was needed to consume that application?  
In a user role I personally never look at a YANG source, though, I look at the tree or HTML representation of YANG all the time; Thats is the YANG human interface for me.

And even in these human friendly formats you can't find all the answers; for example, looking at the YANG tree, how do you get the XML data sample of a given leaf? Thats what we will discover in this post.
<!--more-->

# Problem statement

Getting the XML data sample of a given leaf? What is this, why might I need it?

Lets work through a real-life example that should make a perfect point. Suppose you need to get a list of configured users from a given network element (NE). You would normally do this by leveraging `<get-config>` operation, but in order to get only the users portion of the configuration, you would need to augment your request with a filter.

NETCONF defaults to [subtree filtering](http://www.rfcreader.com/#rfc6241_line869) when it comes to filters.

```xml
<!-- subtree filter example from RFC6241 -->
<rpc message-id="101"
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get-config>
    <source>
      <running/>
    </source>
    <filter type="subtree">
      <top xmlns="http://example.com/schema/1.2/config">
        <users/>
      </top>
    </filter>
  </get-config>
</rpc>
```

Now the question comes: how do one know how to craft the subtree filter XML data for a given NE? If you will send the above XML envelope to any NE you will receive an error, because the subtree filter provided is not how the users are modelled in the underlying YANG model.

Yes, it boils down to an underlying model used by a given NE; you would need to consult with this model and derive the right nodes to get to the configuration block in question.

Actually, that post is a feedback to the question that popped up in my twitter recently:

<center>{{<tweet 1223087371299753984>}}</center>

# Solving the problem with PYANG

Rafael asked a very practical question that every NETCONF user encounters; ours example follows the same question by asking **how do I know which XML data to use in my subtree filter to get users config, are there aby tools for that?**

It didn't take Rafael long to come up with a solution to his own question, which he explained in the same thread:

<center>{{<tweet 1223221183753134080>}}</center>

As you can see, he leveraged [PYANG](https://github.com/mbj4668/pyang) and solved the problem with a grain of `sed` salt. The steps he took can be categorized with 4 major steps:

1. Generated HTML view of a YANG model (jstree output format)
2. Copy the path of a node in question
3. Remove the prefix from that path
4. Generate XML skeleton data for that cleaned path

Lets solve our example question following this method and using Nokia SR OS router running 19.10.r2.

First, lets enjoy the generated HTML views of Nokia SR OS models provided in the [nokia-yangtree repo](https://github.com/hellt/nokia-yangtree/tree/sros_19.10.r6), no need to generate anything yourself, we value your time and here we got you covered.  
Few clicks away and you drill down to the `user` list of the configuration model. Thats where our configured local users live.

![users_yang](https://gitlab.com/rdodin/pics/-/wikis/uploads/4e657129cac96662d75c2e5908cf0275/image.png)

To our grief, PYANG cant digest the path that it produces in its Path column of the HTML view, therefore we need to sanitize it and remove the path prefix (`conf` in our case) from it:

```bash
# path in the HTML: /conf:configure/conf:system/conf:security/conf:user-params/conf:local-user/conf:user
/configure/system/security/user-params/local-user/user
```

> **SR OS PRO TIP that makes competition angry**  
> You can get the model path right out from the box when you navigate to the context of interest

```text
*(ex)[]
A:admin@R1# configure system security user-params local-user user del

*(ex)[configure system security user-params local-user user "del"]
A:admin@R1# pwc model-path
Present Working Context:
/nokia-conf:configure/system/security/user-params/local-user/user=del
```

> Now all you need is to copy that path and remove the user key.

Having the model path without the context we can generate the XML data using the [`sample-xml-skeleton`](https://manned.org/pyang/195e05d7#head15) output of PYANG.

For that step I leverage the open YANG models of SR OS that you can download from the [7x50_YANG_MODELS](https://github.com/nokia/7x50_YangModels) repo and the [PYANG tool in a container](https://github.com/hellt/pyang-docker):

```xml
$ docker run --rm -v $(pwd):/yang hellt/pyang pyang -f sample-xml-skeleton --sample-xml-skeleton-path "/configure/system/security/user-params/local-user/user" nokia-conf-combined.yang
<?xml version='1.0' encoding='UTF-8'?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
    <system>
      <security>
        <user-params>
          <local-user>
            <user>
              <user-name/>
              <home-directory/>
              <password/>
              <cli-engine>
                <!-- # entries: 0..2 -->
              </cli-engine>
<!-- <<SNIP>> -->
            </user>
          </local-user>
        </user-params>
      </security>
    </system>
  </configure>
</data>
```

Pretty neat, right? You have the path to the node you specified as well as all the enclosed containers, lists and leafs so you can filter on them.

In our case we can cut everything that sits under the `<user>` node and get the portion of XML data that is ready to be filled in a subtree filter:

```xml
<!-- this data is ready to be pasted in a subtree template -->
  <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
    <system>
      <security>
        <user-params>
          <local-user>
            <user>
            </user>
          </local-user>
        </user-params>
      </security>
    </system>
  </configure>
</data>
```

This is a `get-config` template XML envelope:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="getBGPNBRstate" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <get>
        <filter>
        </filter>
    </get>
</rpc>
```

Just paste it in the `get-config` XML envelope like this and save it in a `get-users.xml` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="getBGPNBRstate" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <get>
        <filter>
          <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
              <security>
                <user-params>
                  <local-user>
                    <user>
                    </user>
                  </local-user>
                </user-params>
              </security>
            </system>
          </configure>
        </filter>
    </get>
</rpc>
```

Now its ready to be tested (using [netconf-console in a docker container](https://netdevops.me/2020/netconf-console-in-a-docker-container/)):

```xml
[root@infra ~]# docker run -it --rm -v $(pwd):/rpcs hellt/netconf-console --host=10.1.0.11 --port=830 -u admin -p admin /rpcs/get-users.xml
<?xml version='1.0' encoding='UTF-8'?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="getBGPNBRstate">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <password>$2y$10$TQrZlpBDra86.qoexZUzQeBXDY1FcdDhGWdD9lLxMuFyPVSm0OGy6</password>
                                <cli-engine>md-cli</cli-engine>
                                <cli-engine>classic-cli</cli-engine>
                                <access>
                                    <console>true</console>
                                    <ftp>true</ftp>
                                    <snmp>true</snmp>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                                <console>
                                    <member>administrative</member>
                                    <member>netconf</member>
                                </console>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </data>
</rpc-reply>
```

Works!

# Automating the solution

Seeing this in action got me itching; I wanted to automate this process so it would be generic and less manual. For that reason I enriched my [Pyang-docker](https://github.com/hellt/pyang-docker) tool with a tiny shell script that will:

1. Automatically strip the path prefix from the string copied from HTML representation of a model
2. Call pyang with the right flags to generate the xml data

Now when you copy-paster your model path from the HTML you can immediately get the XML data skeleton with:

```xml
$ docker run --rm -v $(pwd):/yang hellt/pyang xmlsk.sh "/conf:configure/conf:system/conf:security/conf:user-params/conf:local-user/conf:user/conf:user-name" nokia-conf-combined.yang

<?xml version='1.0' encoding='UTF-8'?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
    <system>
      <security>
        <user-params>
          <local-user>
            <user>
              <user-name/>
            </user>
          </local-user>
        </user-params>
      </security>
    </system>
  </configure>
</data>
```
