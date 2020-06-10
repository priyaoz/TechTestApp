# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

As the TechTestApp can be made available as container, it was logical to gain redundancy and fail-over and blue/green 
deployment capability with one of AWS' container services. The options were pure ECS, ECS Fargate or even EKS.

## Decision

ECS Fargate is chosen as the "goldilocks" solution

## Consequences

Some ECS features are not available when using Fargate, for example for SecretsManager, which affected especially 
database password exchange from RDS to Fargate.

