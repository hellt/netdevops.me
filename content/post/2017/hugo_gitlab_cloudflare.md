---
date: 2017-08-04T12:00:00Z
gitment_id: hugo-gitlab-cloudflare
keywords:
- Hugo
- Gitlab
- Cloudflare
tags:
- Hugo
- Gitlab
- Cloudflare

title: Setting up a Hugo blog with GitLab and CloudFlare

---

[Hugo](https://gohugo.io/) gets a lot of [attention](https://www.staticgen.com/hugo) these days, it is basically snapping at the Jekyll' heels which is still the king of the hill! I don't know if Hugo' popularity coupled with **the fastest static-site-generator** statement, but for me "speed" is not the issue at all. A personal blog normally has few hundreds posts, not even close to thousands to be worried about slowness.

Then if it is not for speed then why did I choose Hugo? Because it became a solid product with a crowded community and all the common features available. _(To be honest I also got an illusion that one day I might start sharpen my Go skills through Hugo as well)_.

As you already noticed, this blog is powered by **Hugo**, is running on **GitLab pages**, with SSL certificate from **CloudFlare** and costs me **$0**. And I would like to write down the key pieces that'll probably be of help on your path to a zero-cost personal blog/cv/landing/etc.

<!--more-->
The key ingredients of a modern zero-cost blog powered by a Static Site Generator are:

1. Version Control System -- **Git**
2. Web-based version control repository -- **GitLab**/Github
4. Web server -- **GitLab Pages**/GitHub Pages
3. Static Site Generator Engine -- **Hugo**/Jekyll/Hexo/Pelican/many-others
5. SSL Certificate provider -- **Cloudflare**/LetsEncrypt _(optional)_
6. Custom domain linked to a free one from GitLab/Github _(optional)_

While Git and GitLab/GitHub are of obvious choice we better discuss the `Hugo + GitLab CI + GitLab pages + Cloudflare` mix that I chose to enable this blog.

# Hugo
Hugo installation is ridiculously easy, thanks to Golang that powers it. Download a single `hugo` binary from the [official repo](https://github.com/gohugoio/hugo/releases) and thats it. No need for virtualenvs, npms and alike, a single binary is all you need.

Once the binary is in your `$PATH` create a site skeleton with
```
hugo new site <yourBlogName>
```

For details refer to the [QuickStart guide](https://gohugo.io/getting-started/quick-start/) to get a locally running site under 5 minutes.

### Theme
Hugo community produced over 100+ themes for different needs. As to me, most of them are ugly, or as minimalistic as the blogspot. Probably the hardest thing in the whole process is to find a theme that suits you. This blog uses a [Tranquilpeak](https://themes.gohugo.io/hugo-tranquilpeak-theme/) theme.

To onboard a chosen theme follow the quickstart guide' [step 3](https://gohugo.io/getting-started/quick-start/#step-3-add-a-theme).

# GitLab
Now when you have an engine and a theme coupled together its GitLab' part to present your content to the world. GitLab has the [GitLab Pages](https://about.gitlab.com/features/pages/) service created just for what we need and highligted by being: 

* free
* SSG-agnostic
* SSL & custom domains ready 

It has more whistles than Github pages and is completely free without any limitations.

There is a [comprehensive guide](https://docs.gitlab.com/ee/user/project/pages/) about onboarding a static generated site within GitLab, I will boil it down to a few steps (you can always peer into [my repo](https://gitlab.com/rdodin/netdevops.me) for a complete code and settings):

1. Create a `.gitlab-ci.yml` file at the root of your repo with the [`pages`](https://docs.gitlab.com/ce/ci/yaml/#pages) job
    ```bash
    pages:
    # this image is slimmer than official one; based on Alpine
    image: fundor333/hugo 
    script:
        - hugo
    # send all files from public directory to the CI server
    artifacts:
        paths:
          - public
    only:
        - master  # this job will affect only the 'master' branch
    ```
    Note, that you can put the exact same content in your file, there are no custom parts here.

2. Find your `baseurl` and put it into `config.toml` of your Hugo site. A base URL depends on how did you create a GitLab project. Is it a project placed under you personal account or a under a group? All the options are outlined in the [official docs](https://docs.gitlab.com/ce/user/project/pages/getting_started_part_one.html#gitlab-pages-domain).

3. Make a commit with the contents of your blog and push the changes to the master branch `git push origin master`. That will automatically trigger the `pages` job to build your site and start serving it from https://yournamespace.gitlab.io

4. At this point you are good to go, you have TLS certificate provided by Gitlab for `*.gitlab.io` namespace, your posts will be automatically generated once you push to `master` branch and your texts are in VSC. WIN! 

You can stop here and start generate the content, but if you are up to custom domain or custom TLS certificate -> continue to read.

## Custom domain
Having your site to render by _myawesome.blog_ URL instead of _gitlab.io_ is solid. For that you just need a `A` or `CNAME` DNS record provisioned as [explained in the docs](https://docs.gitlab.com/ce/user/project/pages/getting_started_part_three.html). I chose to delegate my **netdevops.me** domain to Cloudflare, since they provide a TLS certificate for free.

## TLS (SSL) certificates
Two common free options when we talk about TLS certs are LetsEncrypt and Cloudflare certs. I am no security expert to claim that one is better than other, I chose a path that is easier, which is [Cloudflare FlexSSL](https://www.cloudflare.com/ssl/) in my case.

{{< image classes="center fancybox clear" src="https://www.cloudflare.com/img/products/ssl/flexible-ssl.svg" title="Cloudflare FlexSSL" >}}

>**Flexible SSL** encrypts traffic from Cloudflare to end users of your website, but not from Cloudflare to your origin server. This is the easiest way to enable HTTPS because it doesn’t require installing an SSL certificate on your origin. While not as secure as the other options, Flexible SSL does protect your visitors from a large class of threats including public WiFi snooping and ad injection over HTTP.

Implications are clear, FlexSSL is free but does not make secure connection end-to-end, which is fine with me.

FlexSSL configuration is as easy as going to **Crypto** pane in the Cloudflare admin panel and enabling _Flexible SSL_:
{{< image classes="center clear" src="https://lh3.googleusercontent.com/IiFaytpHlZgVdig7ZDmVdu1dqbMgzDUo9KCFNxtjXTluW7Bpv3D9lXyYonAUr0HH4MQnDLQKv5d3W-WnqD7caRxXboay6AFpQuwN-1ip_FK74mVIprp_8NqHdD486xSXksxAF-1PLjk5OdeFLFxpIlZ6PeVGE3tsZ0827O2ic1kJNF7DPAwrypBjthqIISDql8rHgiLuVqwZwf-9gmXuSlLqbYztp2w51_ZTP6_Duy4HWvTmZwJqyNy5B_bpRUMAtookE54o3XYxDUzpZrfcyLiRFgQOuGpm2W7k-5ZOlrwZgN-H9WTksUoIBVYNgwjKjm3wDRUFByk_pFJPCcQrzm_wL5stCkzr7ag-FIbne-J4XMMJv78zhzYbDlq89IGOOMyVNyWFanHBV9-jIDBmP76LgpO2-V55fvRMUSgZTn2s5Wmquly-W7_85IYUOuF8Dh4KjW3njRqXDtZuaMxns757-Kz8q854n0-JHtTeM9w8-sEs_TgDFyaXOuUwU3BeNBqhuzsJGhzQnUEJGB0uXk0FRI5qC-SdhDy-wtGGiIMSjZIJFCNl13n8BJIprf7tZPN_NPuSzk4yCBWcFxa36f_GLhLX-8GgRxSPp_-kd6Y3Ax1SxVWiRe_H8RYA6u_53crQobyNMrF_aVLTgP80ZLsyoexvkrLuPhiIEUUlePUPR9g=w982-h409-no" >}}

In that case nothing is needed to be configured in GitLab, just enjoy your TLS-enabled site.

In case you want to enable end-to-end encryption (Strict SSL) there is a thorough [guide from Gitlab](https://about.gitlab.com/2017/02/07/setting-up-gitlab-pages-with-cloudflare-certificates/) covering every step.


> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/3).