#!/usr/bin/env python3

import toml
from aws_cdk import core
from techtestapp_pipeline.techtestapppipeline import TTAPipeline

# Servian are TOML fans it seems...
pipeline_config = toml.load('pipeline.toml')['codepipeline']

# Could just grab the dict members directly to pass in, but this way something goes wrong early
region = pipeline_config['region']
account_basename = pipeline_config['accountname']
account_id = pipeline_config['account']
smname = pipeline_config['githubtokenname']
smkey = pipeline_config['githubtokenkey']
owner = pipeline_config['repoowner']
repo = pipeline_config['reponame']
branch = pipeline_config['buildbranch']

role_arn = f'arn:aws:iam::{account_id}:role/CentaurDev'
smarn = f'arn:aws:secretsmanager:{region}:{account_id}:secret:{smname}'

app = core.App()

TTAPipeline(app, 'TTAPipeline', env=core.Environment(region=region, account=account_id), rolearn=role_arn,
            githubtokenarn=smarn, githubtokenkey=smkey, githubrepoowner=owner, githubrepo=repo, buildbranch=branch)

app.synth()
