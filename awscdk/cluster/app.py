#!/usr/bin/env python3

import toml
from aws_cdk import core
from techtestapp_cluster.techtestappcluster import TTACluster

cluster_config = TTACluster.get_cluster_config()

app = core.App()

TTACluster(app, 'TTACluster',
           env=core.Environment(region=cluster_config['region'], account=cluster_config['accountid']),
           cluster_config=cluster_config)

app.synth()
