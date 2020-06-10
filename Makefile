
# Edit these as needed to profile with roles/policies/permissions to deploy stacks and the right AWS credentials
# See the README files for what all is used here
# Also don't forget to edit 'awscdk/pipeline/attach_policies.sh` to see if you need permission for CodeBuild!

AWSPROFILE=centauridau-mike
AWSDIR=$(HOME)/.aws

# Should not have to edit anything below here, unless you don't like the naming conventions

PIPELINENAME=techtestapp-pipeline

.PHONY: all build pipeline delpipeline

all:
	echo "Options to run make with are:"
	echo "pipeline | delpipeline | build"

build:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) .

pipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)
	sh awscdk/pipeline/attach_policies.sh

delpipeline: build
	docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME) destroy --force

