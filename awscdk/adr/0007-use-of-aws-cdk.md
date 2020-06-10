# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

AWS actively pushes the use of AWS CDK for CloudFormation as their imperative infrastructure-as-code tool.
After being labelled a "dumpster fire" as recently as re:invent 2019, it has come a long way, but still has
significant issues that require wonky work-arounds or make it necessary to go back to external support scripts.

Since its first release a little over a year ago, CDK has come a long way. I've experimented with it on and off in that
time but frequently aborted those attempts, due to issues. As recently as re:Invent 2019, CDK was described to me by
a fellow attendee as a "dumpster fire". However, the tool has made massive strides and I've recently even used it for
production deployments. Similar to other imperative tools such as Troposphere/Awacs or Pulumi, CDK relieves the devops
engineer from gigantic and comples YAML or JSON templates. However, its power lies in its catalogue of Assets which
allow for the creation of entire application stacks with a few lines of Python or other supported languages.

A few lines of Python (not counting comments) literally turn into hundreds of lines of CloudFormation template. The
framework takes care of creation, updating, change sets with a single "UPSERT" style command.

## Decision

Add environment variables overrides back
Despite issues AWS CDK is used as it works for 90%+ of what we wanted to achieve.

## Consequences

Some deployment steps had to be moved to additional helpers.

