# 6. environment variables overrides config file

Date: 2020-06-10

## Status

Accepted

## Context

Normally nowadays, all HTTP would be eschewed in favour of HTTPS. However, that would have required that application
cluster to be registered via DNS (even if just a sub-domain in Route53) and the then a SSL certificate obtained. 
For this assignment that seemed like a bridge too far.

## Decision

For the demo, the ALB exposes HTTP/80

## Consequences

All the issues with unencrypted traffic...

