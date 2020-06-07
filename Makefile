
PIPELINENAME=techtestapp-pipeline
CLUSTERNAME=techtestapp-cluster
AWSDIR=$(HOME)/.aws
AWSPROFILE=centauridau-mike

.PHONY: all pipeline cluster

all:
	echo "Choose either make pipeline or make cluster"

pipeline:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) . && docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)

cluster:
	cd awscdk/cluster && docker build -t $(CLUSTERNAME) . && docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(CLUSTERNAME)
