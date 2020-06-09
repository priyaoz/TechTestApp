#!/usr/bin/env python3

import toml
from aws_cdk import core
from techtestapp_cluster.techtestappfargate import TTAFargate
from techtestapp_cluster.techtestapprds import TTARDS
from techtestapp_cluster.techtestappvpc import TTAVPC


def get_cluster_config(configfile='cluster.toml'):
    """
    Read pipeline config parameters from a TOML file.

    :param configfile: File name, defaults to cluster.toml
    :return: Dict of the [cluster] section
    """
    cluster_config = toml.load(configfile)['cluster']
    return cluster_config


cluster_config = get_cluster_config()

app = core.App()

assignment_vpc = TTAVPC(app, 'TTAVPC',
                        env=core.Environment(region=cluster_config['region'], account=cluster_config['accountid']),
                        cluster_config=cluster_config)
assignment_rds = TTARDS(app, 'TTARDS',
                        env=core.Environment(region=cluster_config['region'], account=cluster_config['accountid']),
                        vpc=assignment_vpc.vpc, cluster_config=cluster_config)
assignment_fargate = TTAFargate(app, 'TTAFargate',
                                env=core.Environment(region=cluster_config['region'],
                                                     account=cluster_config['accountid']),
                                dbendpoint=assignment_rds.endpoint, dbsecret=assignment_rds.secret,
                                vpc=assignment_vpc.vpc,
                                cluster_config=cluster_config)

app.synth()
