#!/usr/bin/env python3

import toml
from aws_cdk import core
from techtestapp_pipeline.techtestapppipeline import TTAPipeline

pipeline_config = TTAPipeline.get_pipeline_config()

app = core.App()

TTAPipeline(app, 'PipelineApp',
            env=core.Environment(region=pipeline_config['region'], account=pipeline_config['accountid']),
            pipeline_config=pipeline_config)

app.synth()
