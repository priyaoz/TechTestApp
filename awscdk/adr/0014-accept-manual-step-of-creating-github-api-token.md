# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

With Github as the source repo, CodePipeline needs access to the API via a generate token. 

## Decision

Securely store the token in SecretsManager.

## Consequences

Requires some additional configuration settings to point to the SecretsManager entry, but it works just fine.

Make note of the secret name (including the random 5-character suffix, for example 
`GithubToken-16wV7`) and the secret key name, for example `github-oauth-token`. Set these in `pipeline.toml`.
