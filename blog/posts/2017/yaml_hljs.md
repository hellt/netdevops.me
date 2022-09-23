---
date: 2017-11-24
comments: true
keywords:
- highlightjs
- yaml
- hugo
tags:
- highlightjs
- hugo

title: How to add YAML highlight in Highlight.js?

---


Haters gonna hate YAML, thats for sure. I am on the other hand in love with YAML; when one have to manually write/append config files I find YAML easier than JSON (and you have comments too).
{{< image classes="fig-33 fancybox" src="https://ih1.redbubble.net/image.441447001.5086/ra,relaxed_fit,x2000,e5d6c5:f62bbf65ee,front-c,295,163,750,1000-bg,f8f8f8.u2.jpg">}}

Ansible, various static-site-generators and quite a lot of opensource tools use YAML syntax for the configuration purposes.  
But still, YAML syntax highlighting is not a part of the Common languages shipped with [highlight.js](https://highlightjs.org/download/) compiled package.

[Hugo](https://netdevops.me/2017/setting-up-a-hugo-blog-with-gitlab-and-cloudflare/) also uses the hljs to colorize code snippets, but it uses the default pack of languages that lacks YAML support.

Look at this greyish snippet, looks ugly.

```plain
---
- name: Prepare linux virt host
  gather_facts: no
  hosts: localhost
  tasks:
    - name: Include packages/services to install/set
      include_vars: main.yml
```

Luckily, we can add _custom_ languages using [Cloudflare CDN collection](https://cdnjs.com) of pre-built packages.

To do so, add [this config portion](https://gitlab.com/rdodin/netdevops.me/commit/d26866ee4b21f7ad8a590e466f92354487ace6ed) to your Hugo' `config.toml`:

```ini
# double check, that you have 
# syntaxHighlighter = "highlight.js" in your config.toml

# note, [[params.customJS]] is nested under [params] section
  [[params.customJS]]
      src = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/languages/yaml.min.js"
      integrity = "sha256-tvm0lHsuUZcOfj/0C9xJTU4OQx5KpUgxUcAXLX5kvwA="
      crossorigin = "anonymous"
      async = true
      defer = true
```

And now our YAML looks a bit better:

```yaml
---
- name: Prepare linux virt host
  gather_facts: no
  hosts: localhost
  tasks:
    - name: Include packages/services to install/set
      include_vars: main.yml
```

I changed the `style-*-.min.css` property to highlight string portions in green, instead of dark blue. A proper way would be to use a custom HLjs theme, but building it in Tranquilpeak theme [is kinda tedious](https://github.com/kakawait/hugo-tranquilpeak-theme/blob/master/docs/user.md#change-code-coloration-highlightjs-theme), so I picked up a shortcut changing the [compiled css](https://gitlab.com/rdodin/netdevops.me/blob/master/themes/hugo-tranquilpeak-theme/static/css/style-jsjn0006wyhpyzivf6yceb31gvpjatbcs3qzjvlumobfnugccvobqwxnnaj8.min.css) instead:

```bash
# change the color code for this class
# in my case I changed to #a5c261
.codeblock .string,figure.highlight .string{color:#a5c261}
```

> Thanks to [Tranquilpeack for Hugo](https://github.com/kakawait/hugo-tranquilpeak-theme) theme maintainer, who [shared](https://github.com/kakawait/hugo-tranquilpeak-theme/issues/186#issuecomment-346593802) with me this option for custom highlighting  
<br/>

> **PS.** Since the method to load custom JS described in this article [has a bug](https://github.com/kakawait/hugo-tranquilpeak-theme/issues/186#issuecomment-348104753) when it comes to Chrome browser, I changed the way Hugo loads custom JS as suggested in the referenced issue.
