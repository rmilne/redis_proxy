MAJOR?=0
MINOR?=1

VERSION=$(MAJOR).$(MINOR)

APP_NAME = "redis-proxy"

# Docker files
DOCKER_PATH = "docker"
APP_DOCKERFILE = "${DOCKER_PATH}/app.Dockerfile"
TEST_DOCKERFILE = "${DOCKER_PATH}/test.Dockerfile"
REDIS_DOCKERFILE = "${DOCKER_PATH}/redis.Dockerfile"

# silent target
all:
	@echo "specify a target"


# docker targets
.PHONY: build-app-image
build-app-image:
	@echo "+ $@"
	@docker build -t ${APP_NAME}:${VERSION} -f ./${APP_DOCKERFILE} .
	@docker tag ${APP_NAME}:${VERSION} ${APP_NAME}:latest
	@echo "Done"
	@docker images --format '{{.Repository}}:{{.Tag}}\t\t Built: {{.CreatedSince}}\t\tSize: {{.Size}}' | grep ${APP_NAME}:${VERSION}


# test targets
.PHONY: unit-test
unit-test:
	@echo "+ $@"
	@echo "TODO"


