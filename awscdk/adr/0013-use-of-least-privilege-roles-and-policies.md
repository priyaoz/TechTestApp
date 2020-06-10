# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

It would  have been easier to simply use admin rights/policies/role for the entire deployment chain. I prefer to use
only the amount of privileges required.

## Decision

Use the policies and profiles created by CDK for the stacks plus attach extra ones as required to the CodePipeline chain.

## Consequences

AWS CDK is still lacking functionality in making it easy to attach existing policies (as opposed to create full-blown 
policy statements). That led to issues when CDK tries to determine all required policies - but of course wasn't able
to "predict" what would be needed in the buildspec.yml control file.

As a result there needed to be a little separate script that finds the CDK created role (which gets very wonky
auto-generated names) and attach my policies there. These also had to be detached if the stacks was deleted, lest
deletion fails.

