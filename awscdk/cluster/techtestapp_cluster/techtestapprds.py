#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp_cluster.techtestapprds.py
    :platform: Unix
    :synopsis:
        Create an RDS Aurora cluster stack for the TechTestApp through the AWS CDK in Python.

.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

from aws_cdk import \
    (
        core,
        aws_ec2 as ec2,
        aws_rds as rds,
    )


class TTARDS(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, cluster_config, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        db = self.get_newdb(vpc=vpc, clusterconfig=cluster_config)
        self.endpoint = db.cluster_endpoint.hostname
        self.secret = db.secret

        db.connections.allow_default_port_from_any_ipv4('access for Fargate cluster')

    def get_newdb(self, *, vpc, clusterconfig) -> rds.DatabaseCluster:
        """
        Create an Aurora RDS cluster in private subnets of the VPC.

        :param vpc: VPC object
        :param clusterconfig: Config dict for configuration of RDS and Fargate clusters
        :return: RDS Cluster object
        """
        db = rds.DatabaseCluster(self, 'RDS',
                                 # this will automatically create an auto-rotating PW in SecretsManager
                                 master_user=rds.Login(username=clusterconfig['dbuser']),
                                 engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
                                 engine_version='10.7',
                                 default_database_name=clusterconfig['dbname'],
                                 removal_policy=core.RemovalPolicy.DESTROY,
                                 # Probably want this in production or such
                                 # removal_policy=core.RemovalPolicy.RETAIN,
                                 instance_props=rds.InstanceProps(vpc=vpc, vpc_subnets=ec2.SubnetType.ISOLATED,
                                                                  instance_type=ec2.InstanceType.of(
                                                                      # aurora postgresql minimum requirements as per doco
                                                                      instance_class=ec2.InstanceClass.BURSTABLE3,
                                                                      instance_size=ec2.InstanceSize.MEDIUM)),
                                 parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                     self, "para-group-postgres",
                                     parameter_group_name="default.aurora-postgresql10"
                                 ),
                                 storage_encrypted=True
                                 )

        return db

