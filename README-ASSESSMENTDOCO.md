
##### Servian Assessment "Exam" Assignment

###### By: Michael Hoffmann

###### Outline

The goal was to automate deployment of the TechTestApp and its database into AWS. That cloud provider was chosen due to
familiarity (GCP would have been second choice). As I always look for learning opportunities, I wanted a chance to 
build a worthwhile AWS CDK stack.

NOTE: this document has gotten quite long. It's not merely intended as install guide or runbook, but is intended to
show my thinking, my approach and how I specifically targeted the requirements of the assessment - or where I 
deviated from them and why.

###### Overengineering

The guidelines for the assessment make mention of "don't over-engineer". As I'm German by ancestry that is not in
my genes. ;-)

Some of the following may indeed appear like way too much effort, but I'd feel comfortable using my solution as 
pattern for other applications, by simply swapping out the desired application. That implies a certain level of
abstraction, which I've aimed for.

###### ADR

See the `adr` folder under the `awscdk` directory which continue on from the "main" ADR entries but which I wanted
to keep encapsulated and separate.

###### Security

As per the assessment guidelines, I've put a fair amount of emphasis on security, specifically the confidentiality and
availability components of the C-I-A triangle.

- No credentials or passwords are embedded in the code or environment variables. 
- AWS SecretManager is used for the DB password and the Github token.
- S3 buckets and the database are encrypted at rest.
- The database is clustered across multiple AZ, as is the Fargate cluster.
- A newly created "blank" VPC is rolled out to host the app.
- The web application (in Fargate) with its ALB are hosted in public subnets. 
- The database is in private subnets with no access to or from the Internet. 

##### Deployment

###### CodePipeline

With the use of AWS, CodePipeline seemed the logical choice. Other options would have been Github or Bitbucket 
pipelines, spin up a Bamboo or Jenkins server or subscribe to CircleCI or TravisCI. To name just a few.

We wanted this to be as stand-alone and embedded as possible.

- `CodePipeline` uses `Github` as source stage and `CodeBuild` as build stage.
- All code related to the deployment is located under the awscdk sub-directory
- Exceptions are few config files that just logically fit better under the project root: 
  - `buildspec.yml`
  - `clusterspec.yml`
  - `Makefile`
  - `ecrpolicy.json`

Their use is explained below.

###### Requirements

- GNU `make` (optional if running the commands in the Makefile manually)
- Docker
- AWS accounts access with IAM roles/policies/permissions to deploy CloudFormation stacks and all required resources:
  - IAM roles and policies
  - RDS Aurora
  - ECS Fargate
  - ECR repositories
  - Code* projects
  - SecretManager secrets
  - etc
  
- Correctly set AWS profile with above role(s)
- An existing AWS VPC for the CodePipeline resources. This is the equivalent of having some CI/CD tool in place, 
otherwise it becomes a hen-and-egg problem (what was first: the resources needed to run the CI/CD tools or the CI/CD
tools to deploy the resources?)

###### Installation

- Make sure you are on the `develop` branch (hmm, otherwise you won't even see this README...) See below for why.

- Review and edit these files:
  - `Makefile`
  - `awscdk/pipeline/pipeline.toml`
  - `awscdk/cluster/cluster.toml` 
  - `awscdk/pipeline/attach_policies.sh` 
  - `awscdk/pipeline/detach_policies.sh` 
  
- Review these files to see what's going on:
  - `buildspec.yml`
  - `clusterspec.yml`
  - `ecrpolicy.json`

- Verify you can run `aws` commands, i.e. connect to the AWS API via CLI with appropriate profile
- From the project root, run `make pipeline` (it will map ~/.aws into the container)
  - This will build the container that itself deploys the CodePipeline stack
  - This is so everything is as self-contained as possible and there's no nasty dependency surprises
  - Watch the CDK->Cloudformation deployment and/or the CodeBuild logs 
  - At the end there should be a CodePipeline project with Github source and CodeBuild build stages which trigger
  on push to the `develop` branch.
  
  NOTE: CodePipeline with Github as source is not able to trigger on multiple branches, unless a number of wonky
  work-arounds get used. CodeCommit would have been able to.
  
  - The pipeline will build a TechTestApp container, as provided by Servian, and store it in ECR

###### Application Deployment

Once the pipeline is correctly generated, any push to `develop` should trigger CodePipeline to deploy the CloudFormation
stacks for the actual TechTestApp application.

There should be two CodeBuild projects, one for the TechTestApp, the other to create the application stack.

