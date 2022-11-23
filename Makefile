MAJOR?=0
MINOR?=1

VERSION=$(MAJOR).$(MINOR)

APP_NAME = "redis-proxy"

# Docker files
DOCKER_PATH = "docker"
APP_DOCKERFILE = "${DOCKER_PATH}/app.Dockerfile"
COMPOSE_FILE = "${DOCKER_PATH}/integration_test_compose.yaml"

# silent target
all:
	@echo "specify a target, eg:  make test"

# docker target - for dev purposes
.PHONY: build-app-image
build-app-image:
	@echo "+ $@"
	@docker build -t ${APP_NAME}:${VERSION} -f ./${APP_DOCKERFILE} .
	@docker tag ${APP_NAME}:${VERSION} ${APP_NAME}:latest
	@echo "Done"
	@docker images --format '{{.Repository}}:{{.Tag}}\t\t Built: {{.CreatedSince}}\t\tSize: {{.Size}}' | grep ${APP_NAME}:${VERSION}

# build the docker images for compose
.PHONY: build
build:
	@echo "+ $@"
	@docker-compose -f ${COMPOSE_FILE} build

# run the test container, will start redis + app
.PHONY: run-test
run-test:
	@echo "+ $@"
	@docker-compose -f ${COMPOSE_FILE} run test

# shut down the compose containers
.PHONY: down
down:
	@echo "+ $@"
	@docker-compose -f ${COMPOSE_FILE} down


# complete test target
.PHONY: test
test: build run-test down


