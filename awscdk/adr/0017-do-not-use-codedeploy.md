# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

Within the Code* tools, there's also CodeDeploy. Its support in CDK is still a bit lacking and for our purposes it
just didn't do what we wanted. It turns out that in Fargate, blue/green is the automatic option, making CodeDeploy
unnecessary.

## Decision

Use a CodeBuild project to  build and deploy TechTestApp and another CodeBuild project for the actual deployment
of the run environment.

## Consequences

Because the dependency chain for artifacts ends up slightly unusual, both builds get run at repo push. Even if/when
only the dependent code for either has changed.

Who'd have thunk how quickly you can burn through your monthly free 100 build minutes...

