---
date: 2020-07-03
comments: true
keywords:
- netconf
tags:
- netconf

title: NETCONF subtree filtering by example
---
If you pick a random NetEng and ask them if they love NETCONF they would likely say "Nah". The ~~hate-hate~~ love-hate kind of relationship with NETCONF mostly roots in its XML layer that one can't swap out. But if we set the XML-related challenges aside, it will become clear that NETCONF is a very well designed management interface with lots of capabilities.  

In this topic we will touch on the NETCONF's subtree filtering capabilities.
<!--more-->

NETCONF's [RFC 6241](https://www.rfcreader.com/#rfc6241) defines two methods for filtering contents on the server (router) side:

- [Subtree filtering](https://www.rfcreader.com/#rfc6241_line867) - mandatory for a NETCONF-enabled device to support
- [XPATH filtering](https://www.rfcreader.com/#rfc6241_line3008) - an optional capability

Subtree filtering is powered by the following components:

- Namespace Selection
- Attribute Match Expressions
- Containment Nodes
- Selection Nodes
- Content Match Nodes

They are very well explained in the RFC, so I won't bother with copy-pasting the definition and the rules these filtering components follow. Instead we will focus on the practical examples and put Selection and Content Match nodes to work in different scenarios.

### 1 Selection nodes

Selection node allow us to get a node and all its nested elements. Our simple examples will revolve around interactions with local users configuration on a Nokia SR OS which is modelled with the following YANG model:

```text
module: nokia-conf
  +--rw configure
     +--rw system
     |  +--rw security
     |  |  +--rw user-params
     |  |     +--rw local-user
     |  |        +--rw user* [user-name]
     |  |           +--rw user-name     types-sros:named-item
     |  |           +--rw password      types-sros:hashed-leaf
     |  |           +--rw access
     |  |           |  +--rw console?   boolean
     |  |           |  +--rw ftp?       boolean
     |  |           |  +--rw snmp?      boolean
     |  |           |  +--rw netconf?   boolean
     |  |           |  +--rw grpc?      boolean
     |  |           |  +--rw li?        boolean
     |  |           +--rw console
                       +--rw member*    ->../aaa/local-profiles…
```

If we want to filter all the configuration information related to the local users we could use Selection node `<local-user/>` in our get-config RPC:

```xml
<get-config>
    <source>
    <running />
    </source>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user/>  <!-- selection node -->
                    </user-params>
                </security>
            </system>
        </configure>
    </filter>
</get-config>
```

> Hint #1: [Nokia-yangtree](https://netdevops.me/nokia-yang-tree/) is a beautiful way to explore Nokia YANG models.  
> Hint #2: I recommend [netconf-console](https://netdevops.me/2020/netconf-console-in-a-docker-container/) to talk NETCONF to your routers.

If we translate this get-operation command to plain English it would sound like: _Dear router, can you please return everything you have under `local-user` node in the running configuration datastore?_  
And that is what router replies back:

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:f00ec433-17b3-4bcb-9d83-c3557794e56e">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <password>$2y$10$Ro5MzyBZ18eVve/aTIYt..fSBbyJar11QGcQbixrVPfxLcpXeZ4eu</password>
                                <access>
                                    <console>true</console>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                                <console>
                                    <member>administrative</member>
                                </console>
                            </user>
                            <user>
                                <user-name>roman</user-name>
                                <password>$2y$10$xkqn46jNHBUJWit446j2o.Yu3E9zWOg44yRGjRK2YjRZE4p5xFjmG</password>
                                <access>
                                    <console>true</console>
                                </access>
                                <console>
                                    <member>default</member>
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

The answer satisfies the request we specified. Router dumps everything it has under `local-users`.

#### 1.1 Multiple selection nodes

But what is we don't want to get back all that information about the local users and just interested in the account names and their access methods? That is as well the work for Selection nodes. But instead of referencing a container or a list with the Selection node, we will pinpoint the nodes of interest - `user-name` and `access`:

```xml
<get-config>
    <source>
    <running />
    </source>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name />
                                <access />
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </filter>
</get-config>
```

Pay attention that it doesn't matter what type of node we are referencing with a Selection node. It can be a container, a list, a leaf. If a selected node happens to have nested elements they will be returned as well.

In the example above we reference the `user-name`  leaf and the `access` container, as a result we receive back a concrete data stored as the `user-name` node and everything that exists under the `access` container:

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:4c646ef4-601b-465e-ba35-f90953527a73">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <access>
                                    <console>true</console>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                            </user>
                            <user>
                                <user-name>roman</user-name>
                                <access>
                                    <console>true</console>
                                </access>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </data>
</rpc-reply>
```

#### 1.2 Selection nodes in different containment nodes

It is totally fine to have the Selection nodes under different containment nodes. That allows you to filter the information from different nodes in a single request.

What if we wanted not only to see which users are configured on a box, but also to see how many login attempts each of them made? Thats a perfect example how Selection nodes from different containment nodes play well together.

```xml
<get>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name />  <!-- selection node in context A -->
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
        <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <attempted-logins />  <!-- selection node in context B -->
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </state>
    </filter>
</get>
```

Here we used Selection nodes even in two different YANG datastores and getting both configuration and state data in a single reply:

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:c622d500-b780-4765-a71e-8f6b354beff4">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                            </user>
                            <user>
                                <user-name>roman</user-name>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
        <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <attempted-logins>74</attempted-logins>
                            </user>
                            <user>
                                <user-name>roman</user-name>
                                <attempted-logins>0</attempted-logins>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </state>
    </data>
</rpc-reply>
```

### 2 Content Match nodes

In many cases it is needed to filter not only on the node itself (what Selection node does), but also on the value of the referenced leaf. That is a work for [Content Match nodes](https://www.rfcreader.com/#rfc6241_line1017).

Using our local users examples that translates to a need to filter the information of a single user only. Let's get the configuration of the `admin` user only by using the Content Match node semantics:

```xml
<get-config>
    <source>
    <running />
    </source>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>  <!-- Content Match node -->
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </filter>
</get-config>
```

Content Match nodes filtering is only applicable to the leafs, in our example that was `user-name` which we set to `admin`. As a result, we got back the configuration related to the `admin` user only:

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:5c1da160-69e1-466a-97c0-541f3add8f2d">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <password>$2y$10$Ro5MzyBZ18eVve/aTIYt..fSBbyJar11QGcQbixrVPfxLcpXeZ4eu</password>
                                <access>
                                    <console>true</console>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                                <console>
                                    <member>administrative</member>
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

#### 2.1 Multiple Content Match nodes

By adding multiple Content Match nodes in your filter request you add an implicit `AND` operand between them. Lets say we want to list the configured users who both have access to netconf and grpc. We can craft such a filter request by using two Content Match nodes expressions:

```xml
<get-config>
    <source>
    <running />
    </source>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <access>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </filter>
</get-config>
```

In the end we get our single user - `admin` - who has access to the subsystems we put in a filter, cool!

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:33d1666e-de58-4414-8c4d-374bd73d8ef2">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <access>
                                    <console>true</console>
                                    <netconf>true</netconf>
                                    <grpc>true</grpc>
                                </access>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </data>
</rpc-reply>
```

### 3 Content Match and Selection nodes

Another interesting filtering technique is combining Selection and Content Match nodes. Quite often you want to filter on the content, but at the same time limit the amount of data that router replies back. That might be very expensive for a router to return every sibling when only Content Match node is used, therefore its a good practice to craft a filter that will contain only the needed information.

Talking our local users database me might want to know if `admin` user has access to `netconf` subsystem and we don't care at all about any other configuration that user has. Thats a perfect candidate for a combination of Content Match and Selection nodes:

```xml
<get-config>
    <source>
    <running />
    </source>
    <filter>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>  <!-- content match -->
                                <access>
                                    <netconf/>                 <!-- selection -->
                                </access>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </filter>
</get-config>
```

And look at what a concise and clear response we got back. It has only the information we cared about.

```xml
<rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:02b36787-e805-4370-ac7b-b569a14d2e64">
    <data>
        <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
            <system>
                <security>
                    <user-params>
                        <local-user>
                            <user>
                                <user-name>admin</user-name>
                                <access>
                                    <netconf>true</netconf>
                                </access>
                            </user>
                        </local-user>
                    </user-params>
                </security>
            </system>
        </configure>
    </data>
</rpc-reply>
```

In the simplified local users database example that might not seem critical, but on a real network element you might filter through hundreds of configuration elements while only cared about a single one. Then it makes all the sense to combine Content Match nodes with Selection nodes to minimize the payload sizes and computation times.

### Summary

NETCONF Subtree filtering is a powerful mechanism that is both easy to use and reason about. By using Contaiment, Selection and Content Match nodes one can easily filter anything, while maintaining efficiency and cleanliness of the filter construct.

Remember that using Selection nodes with Content Match nodes allow you to follow the beast practices and request only the information that you need, without clutter.
