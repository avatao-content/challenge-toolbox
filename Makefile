IMAGE  := eu.gcr.io/avatao-challengestore/challenge-toolbox
DOCKER := /usr/bin/docker
BFLAGS += $(if $(findstring B,$(MAKEFLAGS)),--no-cache)

build:
	$(DOCKER) build $(BFLAGS) -t $(IMAGE) .

push pull rmi history inspect:
	$(DOCKER) $@ $(IMAGE)

.PHONY: build push pull rmi history inspect
