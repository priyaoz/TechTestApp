# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Relates to:

ADR-0015

## Context

Merged branch should probably not be left hanging about, lest tragedy strikes with mis-places merge attempts.
However, one point of the assessment as passed on by Chris Karanja, was to demonstrate understanding of Git
and good branching models.

I use a  "modified" Gitflow (AKA, the simplified Atlassian model), as I have for years and quite like it.

It's `release`, `master`, `develop`, `feature/name`, `bug/name`, `hotfix/name`. Features and bugs go to `develop`, `hotfix`
generally to `master`. `release` holds tagged releases out of `master`.

Once the assessor  has seen that I understand git, branching and DVSC, they should best just be deleted.

## Decision

Leave a couple of old branch about as "evidence".

## Consequences

If somebody tries to merge those, it will not end well.

DO NOT MERGE THEM! 

