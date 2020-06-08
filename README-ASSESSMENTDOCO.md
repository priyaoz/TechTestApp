
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

###### Selected Services and Tools

As stated, deployment is in AWS. To this end, a number of "native" services and tools went with it:

- Use of CodePipeline as CI/CD orchestrator
- Use of CodeBuild as build tool, both for the TechTestApp in its Docker container, but also the ECS Fargate cluster
- Use of AWS CDK as imperative infrastructure-as-code tool (see below)
- Use of ECS Fargate as compromise between the pain that "pure" ECS can be (even with CDK) while not having wanted to
go "full hog" into K8S for this assignment
- Use of RDS Aurora in PostgreSQL mode as the underlying DB cluster

###### AWS CDK

Since its first release a little over a year ago, CDK has come a long way. I've experimented with it on and off in that
time but frequently aborted those attempts, due to issues. As recently as re:Invent 2019, CDK was described to me by
a fellow attendee as a "dumpster fire". However, the tool has made massive strides and I've recently even used it for
production deployments. Similar to other imperative tools such as Troposphere/Awacs or Pulumi, CDK relieves the devops
engineer from gigantic and comples YAML or JSON templates. However, its power lies in its catalogue of Assets which
allow for the creation of entire application stacks with a few lines of Python or other supported languages.

A few lines of Python (not counting comments) literally turn into hundreds of lines of CloudFormation template. The
framework takes care of creation, updating, change sets with a single "UPSERT" style command.

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

One thing to note is that for simplicity sake, web traffic is to HTTP/80 and *not* HTTPS/443. The latter would have
required certificates and registration of the cluster LB in DNS, which I considered just a bit out of scope. 
Naturally, a "real" app would use HTTPS!

Also, one thing to point out: I left some entries such as my used account ID or account alias in place. It's a 
throw-away account, fairly locked down. Not too concerned you guys will suddenly launch Bitcoin miners in there.
Besides there's no users or groups, it's all SAML/SSO with multi-factor auth. :-P

##### Deployment

###### CodePipeline

With the use of AWS, CodePipeline seemed the logical choice. Other options would have been Github or Bitbucket 
pipelines, spin up a Bamboo or Jenkins server or subscribe to CircleCI or TravisCI. To name just a few.

We wanted this to be as stand-alone and embedded as possible.

- `CodePipeline` uses `Github` as source stage and `CodeBuild` as build stage.
- All code related to the deployment is located under the awscdk sub-directory
- Exceptions are few config files that just logically fit better under the project root: 
  - `buildspec.yml`
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
  
NOTE: I did not run these deployment with admin rights during testing, but with expanded PowerUser roles. Unfortunately it takes a
lot of reading AWS documentation to get all the permissions required when running such a variety of services. Simply
using admin access is tempting.

- Correctly set AWS profile with above role(s)
- An existing AWS VPC for the CodePipeline resources. This is the equivalent of having some CI/CD tool in place, 
otherwise it becomes a hen-and-egg problem (what was first: the resources needed to run the CI/CD tools or the CI/CD
tools to deploy the resources?)
- A personal Github token for API access by CodePipeline, which must be stored in SecretsManager in the account that
runs the deployments. Make note of the secret name (including the random 5-character suffix, for example 
`GithubToken-16wV7`) and the secret key name, for example `github-oauth-token`. Set these in `pipeline.toml`.

###### Installation

- Make sure you are on the `develop` branch (hmm, otherwise you won't even see this README...) See below for why.
- Review and edit these files:
  - `awscdk/pipeline/pipeline.toml`
  - `awscdk/cluster/cluster.toml` 
  - `Makefile`
- Verify you can run `aws` commands, i.e. connect to the AWS API via CLI with appropriate profile
- Run `make pipeline` (it will map ~/.aws into the container)
  - This will build the container that itself deploys the CodePipeline stack
  - This is so everything is as self-contained as possible and there's no nasty dependency surprises
  - Watch the CDK->Cloudformation deployment 
  - At the end there should be a CodePipeline project with Github source and CodeBuild build stages which trigger
  on push to the `develop` branch.
  
  NOTE: CodePipeline with Github as source is not able to trigger on multiple branches, unless a number of wonky
  work-arounds get used. CodeCommit would have been able to.
  
  - The pipeline will build two containers: the TechTestApp one, as provided by Servian, and the cluster builder
  container
  - Both are stored in ECR


