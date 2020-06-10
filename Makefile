
# Edit this one as needed to profile with roles/policies/permissions to deploy stacks
# See the README files for what all is used here
AWSPROFILE=centauridau-mike

# Should not have to edit anything below here, unless you don't like the naming conventions
PIPELINENAME=techtestapp-pipeline
clusterNAME=techtestapp-cluster
RDSNAME=techtestapp-rds
AWSDIR=$(HOME)/.aws

.PHONY: all build pipeline cluster delpipeline delcluster buildpipeline buildcluster

all:
	echo "Options to run make with are:"
	echo "pipeline | cluster | delpipeline | delcluster | build"

buildpipeline:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) .

buildcluster:
	cd awscdk/cluster && docker build -t $(CLUSTERNAME) .

build: buildpipeline buildcluster

pipeline: buildpipeline
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)

cluster: buildcluster
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(CLUSTERNAME)

delpipeline: buildpipeline
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME) destroy --force

delcluster: buildcluster
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(CLUSTERNAME) destroy --force


