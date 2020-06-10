# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

I wanted to make sure that I had a proper redundant database and within AWS that means RDS. RDS Aurora is cheaper than
RDS, is server-less, MySQL and PostgreSQL compatible and offers great multi-AZ capabilities out of the box.

## Decision

RDS Aurora is chosen as database cluster.

## Consequences

The way RDS stores its DB credentials in SecretsManager is incompatible with Fargate, requiring a horrible kludge
script/app that securely extracts the password and stores it in a SecretsManager entry that Fargate *can* access.
