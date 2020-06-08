
# Edit this one as needed to profile with roles/policies/permissions to deploy stacks
# See the README files for what all is used here
AWSPROFILE=centauridau-mike

# Should not have to edit anything below here, unless you don't like the naming conventions
PIPELINENAME=techtestapp-pipeline
CLUSTERNAME=techtestapp-cluster
AWSDIR=$(HOME)/.aws

.PHONY: all build pipeline cluster

all:
	echo "Options to run make with are:"
	echo "pipeline | cluster | delpipeline | delcluster | build"

build:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) .
	cd awscdk/cluster && docker build -t $(CLUSTERNAME) .

pipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)

cluster: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(CLUSTERNAME)

delpipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME) destroy --force

delcluster: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(CLUSTERNAME) destroy --force

