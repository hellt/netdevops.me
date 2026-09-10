UV ?= uv
DEV_ADDR ?= 127.0.0.1:8002
DEPLOY_REMOTE ?= origin
DEPLOY_BRANCH ?= gh-pages
DEPLOY_NAME ?= github-actions[bot]
DEPLOY_EMAIL ?= 41898282+github-actions[bot]@users.noreply.github.com
HTMLTEST_VERSION := 0.17.0

.DEFAULT_GOAL := build-docs
.PHONY: install-docs lock-docs build-docs serve-docs test-docs deploy-docs htmltest htmltest-internal check-docs docs serve serve-full

install-docs:
	$(UV) sync --locked

lock-docs:
	$(UV) lock

build-docs: install-docs
	$(UV) run --locked python scripts/docs.py build

serve-docs: install-docs
	$(UV) run --locked python scripts/docs.py serve --address $(DEV_ADDR)

check-docs: test-docs htmltest-internal

test-docs: build-docs
	$(UV) run --locked python -m unittest discover -s tests -v

# Keep the existing branch-based GitHub Pages deployment and custom domain.
deploy-docs: check-docs
	GIT_COMMITTER_NAME="$(DEPLOY_NAME)" GIT_COMMITTER_EMAIL="$(DEPLOY_EMAIL)" $(UV) run --locked ghp-import -n -p -f -r $(DEPLOY_REMOTE) -b $(DEPLOY_BRANCH) site

# Native Go binary; no container action or remote shell installer.
bin/htmltest:
	GOBIN=$(CURDIR)/bin go install github.com/wjdp/htmltest@v$(HTMLTEST_VERSION)

htmltest: build-docs bin/htmltest
	bin/htmltest --conf blog/htmltest.yml

htmltest-internal: build-docs bin/htmltest
	bin/htmltest --conf blog/htmltest.yml --skip-external

docs: build-docs
serve serve-full: serve-docs
