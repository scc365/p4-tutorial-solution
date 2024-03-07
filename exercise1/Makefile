mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
curr_dir := $(patsubst %/,%,$(dir $(mkfile_path)))
PYTHONPATH := ../util/lib/

P4RT_SH_IMG := p4lang/p4runtime-sh:latest
P4C_IMG := opennetworking/p4c:stable
STRATUM_BMV2_IMG := opennetworking/ngsdn-tutorial:stratum_bmv2

P4RT_SH_SHA := sha256:6ae50afb5bde620acb9473ce6cd7b990ff6cc63fe4113cf5584c8e38fe42176c
P4C_SHA := sha256:8f9d27a6edf446c3801db621359fec5de993ebdebc6844d8b1292e369be5dfea
STRATUM_BMV2_SHA := sha256:f31faa5e83abbb2d9cf39d28b3578f6e113225641337ec7d16d867b0667524ef

NGSDN_TOPO_PY := topo.py

default:
	$(error Please specify a make target (see README.md))

_docker_pull_all:
	docker pull ${P4RT_SH_IMG}@${P4RT_SH_SHA}
	docker tag ${P4RT_SH_IMG}@${P4RT_SH_SHA} ${P4RT_SH_IMG}
	docker pull ${P4C_IMG}@${P4C_SHA}
	docker tag ${P4C_IMG}@${P4C_SHA} ${P4C_IMG}
	docker pull ${STRATUM_BMV2_IMG}@${STRATUM_BMV2_SHA}
	docker tag ${STRATUM_BMV2_IMG}@${STRATUM_BMV2_SHA} ${STRATUM_BMV2_IMG}

deps: _docker_pull_all

_start:
	$(info *** Starting Mininet (${NGSDN_TOPO_PY})... )
	@NGSDN_TOPO_PY=${NGSDN_TOPO_PY} docker-compose -f docker-compose.yml up -d
	sleep 10
	PYTHONPATH=${PYTHONPATH} python3 ../util/simple_controller.py -a localhost:50001 -d 1 -p /tmp/s1.txt -c mininet/s1-runtime.json
	PYTHONPATH=${PYTHONPATH} python3 ../util/simple_controller.py -a localhost:50002 -d 1 -p /tmp/s2.txt -c mininet/s2-runtime.json
	PYTHONPATH=${PYTHONPATH} python3 ../util/simple_controller.py -a localhost:50003 -d 1 -p /tmp/s3.txt -c mininet/s3-runtime.json
	PYTHONPATH=${PYTHONPATH} python3 ../util/simple_controller.py -a localhost:50004 -d 1 -p /tmp/s4.txt -c mininet/s4-runtime.json

start: NGSDN_TOPO_PY := topo.py
start: _start

stop:
	$(info *** Stopping ONOS and Mininet...)
	@NGSDN_TOPO_PY=foo docker-compose -f docker-compose.yml down -t0

restart: reset start

mn-cli:
	$(info *** Attaching to Mininet CLI...)
	$(info *** To detach press Ctrl-D (Mininet will keep running))
	-@docker attach --detach-keys "ctrl-d" $(shell docker-compose ps -q mininet) || echo "*** Detached from Mininet CLI"

mn-log:
	docker logs -f mininet

install:
	pip3  install grpcio grpcio-tools

p4-build: p4src/main.p4
	$(info *** Building P4 program...)
	@mkdir -p p4src/build
	docker run --rm -v ${curr_dir}:/workdir -w /workdir ${P4C_IMG} \
		p4c-bm2-ss --arch v1model -o p4src/build/bmv2.json \
		--p4runtime-files p4src/build/p4info.txt --Wdisable=unsupported \
		p4src/main.p4
	@echo "*** P4 program compiled successfully! Output files are in p4src/build"

proto-build:
	python3 -m grpc_tools.protoc --proto_path=../proto/ ../proto/p4/v1/p4data.proto \
		../proto/p4/config/v1/p4info.proto ../proto/p4/config/v1/p4types.proto \
		../proto/google/rpc/status.proto ../proto/google/rpc/code.proto \
		../proto/p4/tmp/p4config.proto ../proto/p4/server/v1/config.proto \
		../proto/p4/v1/p4runtime.proto --python_out=../util/lib/ --grpc_python_out=../util/lib/

clean:
	rm -r ./tmp/
