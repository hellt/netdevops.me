---
date: 2017-07-28
comments: true
keywords:
- Golang
- VSCode
tags:
- Golang
- VSCode

title: How to make VS Code Go extension to work in your cloud folder on different platforms?

---

I started to play with **Go** aka Golang. Yeah, leaving the comfort zone, all that buzz. And for quite some time I've been engaged with VS Code whenever/wherever I did dev activities.

VS Code has a solid Go support via its official extension:

> This extension adds rich language support for the Go language to VS Code, including:

> - Completion Lists (using gocode)
> - Signature Help (using gogetdoc or godef+godoc)
>
> - Quick Info (using gogetdoc or godef+godoc)
> - Goto Definition (using gogetdoc or godef+godoc)
> - Find References (using guru)
> - File outline (using go-outline)
>
* Workspace symbol search (using go-symbols)
- Rename (using gorename)
- Build-on-save (using go build and go test)
- Lint-on-save (using golint or gometalinter)
- Format (using goreturns or goimports or gofmt)
- Generate unit tests skeleton (using gotests)
- Add Imports (using gopkgs)
- Add/Remove Tags on struct fields (using gomodifytags)
- Semantic/Syntactic error reporting as you type (using gotype-live)

Mark that gotools in the brackets, these ones are powering all that extra functionality and got installed into your `GOPATH` once you install them via VS Code.

And here you might face an issue if you want to use Go + VS Code both on Mac and Linux using the Dropbox folder (or any other syncing service). The issue is that binaries for Mac and Linux will overwrite themselves once you decide to install the extension on your second platform. Indeed, by default VS Code will fetch the source code of the tools and build them, placing binaries in the `$GOPATH/bin`.

Lucky we, the Go Extension developers have a special setting to put extension dependencies to a different `$GOPATH`:

> #### Tools this extension depends on

> This extension uses a host of Go tools to provide the various rich features. These tools are installed in your `GOPATH` by default. If you wish to have the extension use a separate `GOPATH` for its tools, provide the desired location in the setting `go.toolsGopath`. [Read more](https://github.com/Microsoft/vscode-go/wiki/Go-tools-that-the-Go-extension-depends-on) about this and the tools at Go tools that the Go extension depends on

And thats it, open your `settings.json`, put something like

```json
"go.toolsGopath": "~/.gotools"
```

and thats it, next time you hit "install" of Go Extension dependencies, they will be stored outside your Dropbox-powered `$GOPATH` and won't interfere with each other.
