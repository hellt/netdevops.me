---
date: 2021-02-23T06:00:00Z
comment_id: furyio
keywords:
  - fury.io
  - apt
  - yum
  - goreleaser
tags:
  - fury.io
  - apt
  - yum
  - goreleaser

title: Building and publishing deb/rpm packages with goreleaser and fury.io
---

I am a huge fan of a [goreleaser](https://goreleaser.com/) tool that enables users to build Go projects and package/publish build artifacts in a fully automated and highly customizable way. We've have been using goreleaser with all our recent projects and we couldn't be any happier since then.

But once the artifacts are built and published, the next important step is to make them easily installable. Especially if you provide deb/rpm packages which are built with [NFPM integration](https://goreleaser.com/customization/nfpm/).

The "challenge" with deb/rpm packages comes to light when project owners want to add those packages to Apt/Yum repositories. Goreleaser doesn't provide any integrations with 3rd party repositories nor there are Apt/Yum repositories which are free and provide an API to upload artifacts. Or are there?

## Gemfury aka Fury.io
Actually there is at least one - the [gemfury.io](https://fury.io) project that does just that (and even more).

![fury](https://gitlab.com/rdodin/pics/-/wikis/uploads/f329ec478f16c4b2c0dce0108a51be75/image.png)

> Gemfury is a private package repository to help you easily reuse code without worrying about its hosting or deployment. It integrates directly with existing package management tools that you already use.

Among other repositories, Fury provides a Yum/Apt repo for pre-built deb/rpm packages. It is free for public packages, which makes it a good choice for OSS projects. It also sports a hefty number of options to upload artifacts, from a simple `curl` to a push via its own CLI tool.

![upload](https://gitlab.com/rdodin/pics/-/wikis/uploads/9d85417c6db94401967e1a4e7d342354/image.png)

Just register within the service and generate a [push token](https://gemfury.com/help/tokens/#push-tokens-to-upload-packages), and you are good to go leveraging Goreleaser to push your artifacts to Fury.

## Using Goreleaser with Fury
#### Step 1: Adding Fury' token
Once you have a Fury' push token, it is a matter of a few lines of code on the Goreleaser side.

I am using Goreleaser' Github action to build and publish artifacts, therefore I added push token to repo's secrets and added it as another environment variable of a goreleaser action:

```yaml
# github action workflow file
---
name: Release
on:
  push:
    tags:
      - v*
jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Set up Go
        uses: actions/setup-go@v2
        with:
          go-version: 1.15
      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v2
        with:
          version: v0.155.0
          args: release --rm-dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          FURY_TOKEN: ${{ secrets.FURYPUSHTOKEN }}
```

This will make our `FURYPUSHTOKEN` secret value to be available inside the Goreleaser' Env vars under the `FURY_TOKEN` name.

#### Step 2: Add ID for NFPM builds
In the `nfpm` section of your `.goreleaser.yml` file add `id` field. This identification string will be used in Step 3 to scope which artifacts will be pushed to Fury. Since Fury will be used exclusively for dep/rpm artifacts, by using the `id` related to them we will skip artifacts which are generated in the `build` section of goreleaser (aka archives).

```yaml
# .goreleaser.yml file
<SNIP>
nfpms:
  - id: packages # here we say that artifacts built with nfpm will be identified with `packages` string.
    file_name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
<SNIP>
```

#### Step 3: Add custom publisher
Now we need to tell Goreleaser to actually push those deb/rpm files it produced to a Fury repo. This is easily done with the [custom publishers](https://goreleaser.com/customization/publishers/) feature.

```yaml
publishers:
  - name: fury.io
    # by specifying `packages` id here goreleaser will only use this publisher
    # with artifacts identified by this id
    ids:
      - packages
    dir: "{{ dir .ArtifactPath }}"
    cmd: curl -F package=@{{ .ArtifactName }} https://{{ .Env.FURY_TOKEN }}@push.fury.io/netdevops/
```

Look how easy it is. Now on every goreleaser' build, artifacts from nfpm will be concurrently uploaded to Fury and immediately available to the users of those Apt/Yum repositories. Do note, that by default pushed artifacts have a private scope, so don't forget to visit Fury' account dashboard and make them public.

Did I say that Goreleaser is a great tool? I bet I did, so consider supporting it if you have a chance.


> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>