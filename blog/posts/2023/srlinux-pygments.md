---
date: 2023-01-08
comments: true
tags:
  - srlinux
  - pygments
---

# Creating a syntax highlighter for SR Linux CLI snippets

How to write a custom syntax highligher for your favorite Network OS CLI and integrate it the doc engine?

=== "Raw text CLI snippet"
    ```
    --{ * candidate shared default }--[ network-instance black ]--
    A:leaf1# info static-routes
            static-routes {
                route 192.168.18.0/24 {
                    admin-state enable
                    metric 1
                    preference 5
                    next-hop-group static-ipv4-grp
                }
                route 2001:1::192:168:18:0/64 {
                    admin-state enable
                    metric 1
                    preference 6
                    next-hop-group static-ipv6-grp
                }
            }
    ```
=== "With `srl` syntax applied"
    ```srl
    --{ * candidate shared default }--[ network-instance black ]--
    A:leaf1# info static-routes
            static-routes {
                route 192.168.18.0/24 {
                    admin-state enable
                    metric 1
                    preference 5
                    next-hop-group static-ipv4-grp
                }
                route 2001:1::192:168:18:0/64 {
                    admin-state enable
                    metric 1
                    preference 6
                    next-hop-group static-ipv6-grp
                }
            }
    ```

Read in my post [**"SR Linux Syntax Highlighting with Pygments"**](https://learn.srlinux.dev/blog/2023/sr-linux-syntax-highlighting-with-pygments/) at learn.srlinux.dev portal.
