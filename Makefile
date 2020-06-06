
PIPELINENAME=techtestapp-pipeline
AWSDIR=$(HOME)/.aws
AWSPROFILE=centauridau-mike

.PHONY: pipeline

pipeline:
	cd awscdk/pipeline && docker build -t $(PIPELINENAME) . && docker run --rm -e AWS_PROFILE=$(AWSPROFILE) -v $(AWSDIR):/root/.aws $(PIPELINENAME)