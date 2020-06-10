# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Relates to:

ADR-0016

## Context

Normally all changes would go into `master` for deployment. We wanted to leave the Servian repo as untouched as possible,
so my changes for the assessment could be thrown away in entirety.

## Decision

Deployment trigger off pushes to `develop`

## Consequences

May cause a bit of confusion within a proper Gitflow branch model. Maybe I should have given the branch a name like
`michaelh` to make it absolutely clear why we're diverting from common practise.
