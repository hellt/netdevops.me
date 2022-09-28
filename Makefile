# insiders version/tag https://github.com/srl-labs/mkdocs-material-insiders/pkgs/container/mkdocs-material-insiders
# make sure to also change the mkdocs version in actions' cicd.yml and force-build.yml files
MKDOCS_INS_VER = 8.5.3-insiders-4.24.0

.PHONY: docs
docs:
	docker run -v $$(pwd):/docs --entrypoint mkdocs squidfunk/mkdocs-material:$(MKDOCS_INS_VER) build --clean --strict

# serve the site locally using mkdocs-material insiders container
.PHONY: serve
serve:
	docker run -it --rm -p 8002:8000 -v $$(pwd):/docs ghcr.io/hellt/mkdocs-material-insiders:$(MKDOCS_INS_VER)

.PHONY: htmltest
htmltest:
	docker run --rm -v $$(pwd):/docs --entrypoint mkdocs ghcr.io/hellt/mkdocs-material-insiders:$(MKDOCS_INS_VER) build --clean --strict
	docker run --rm -v $$(pwd):/test wjdp/htmltest --conf ./site/htmltest-w-github.yml
	rm -rf ./site
