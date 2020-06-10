# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

There are a plethora of choice for CI/CD, ranking from on-prem to SaaS. I don't have a CircleCI or TravisCI subscription
and neither did I want to spin up a Jenkins or Bamboo server.

## Decision

Using AWS own CodePipeline/CodeBuild suite for  CI/CD.

## Consequences

Creation of that pipeline is the only manual deployment step marring the "look, ma, no hands!" automatism.

