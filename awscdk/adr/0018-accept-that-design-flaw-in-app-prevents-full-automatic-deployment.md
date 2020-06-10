# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

The TechTestApp accepts two command line options: `serve` to run the web service and `updatedb [-s]` to create
the database schema and fill it with some sample data.

However, `updatedb` actually brute-force wipes out any existing data! It's not really an "update".

Also, the fact that it has to be run as a separate step, instead of an automatic check at application start-up (with,
for example, database versioning or a table flag that indicates existing previous data), makes it near impossible to
automate this step when (as dictated by best practise) the DB subnets are isolated/private and therefore only allow
access by the Fargate cluster.

Embedding the `updatedb` step into CodeBuild results in a wiped-out DB at every pipeline run, something that would be
quite unacceptable in the "real world". And that's if CodeBuild can even get to the isolated subnets. 

There are ways to get CodeBuild to run inside a VPC such that it can connect to RDS in a private subnet, but after
slamming my head against this wall for far too long, I decided to accept the consequences.

## Decision

I left this as-is for now, after spending too much time on it. Happy to discuss.

Other decision is to learn more GoLang, so I could have "fixed" the application code.

## Consequences

I found one manual work-around was to create a quick ec2 instance in the Fargate subnet(s), with docker on it and
then run the app with `updatedb -s` from there with all the required parameters passed at runtime. Requires that
the instance gets a IAM profile or AWS credentials that allow it a) obtain the DB password from SecretsManager and b) 
get the container from ECR and run it.
