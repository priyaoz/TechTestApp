
# Edit this one as needed to profile with roles/policies/permissions to deploy stacks
# See the README files for what all is used here
AWSPROFILE=centauridau-mike

# Should not have to edit anything below here, unless you don't like the naming conventions
PIPELINENAME=techtestapp-pipeline
FARGATENAME=techtestapp-fargate
RDSNAME=techtestapp-rds
AWSDIR=$(HOME)/.aws

.PHONY: all build pipeline cluster

all:
	echo "Options to run make with are:"
	echo "pipeline | fargate | rds | delpipeline | delfargate | delrds | build"

build:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) .
	cd awscdk/fargate && docker build -t $(FARGATENAME) .
	cd awscdk/rds && docker build -t $(RDSNAME) .

pipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)

fargate: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(FARGATENAME)

rds: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(RDSNAME)

delpipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME) destroy --force

delfargate: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(FARGATENAME) destroy --force

delrds: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(RDSNAME) destroy --force

