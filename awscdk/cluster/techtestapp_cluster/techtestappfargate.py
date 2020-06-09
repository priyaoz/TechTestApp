#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp_cluster.techtestappfargate.py
    :platform: Unix
    :synopsis:
        Create an AWS Fargate Cluster and RDS stack for the TechTestApp through the AWS CDK in Python.

.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

import toml
from aws_cdk import \
    (
        core,
        aws_ecs as ecs,
        aws_ecr as ecr,
        aws_ecs_patterns as ecs_patterns,
        aws_secretsmanager as sm
    )


class TTAFargate(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, vpc, dbendpoint, dbsecret, cluster_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.make_fargate(vpc=vpc, dbendpoint=dbendpoint, dbsecret=dbsecret, clusterconfig=cluster_config)

    def make_fargate(self, *, vpc, dbendpoint, dbsecret, clusterconfig):
        """
        Create an ECS Fargate cluster in public subnets within VPC running the specified container.

        :param vpc: The VPC
        :param dbsecret: The DB secret object (NOT plaintext) stored in SecretManager
        :param dbendpoint: The DB endpoint FQDN
        :param clusterconfig: Config dict for configuration of RDS and Fargate clusters
        """
        cluster = ecs.Cluster(self, "TTACluster", vpc=vpc)

        # let's test this
        secretarn = 'arn:aws:secretsmanager:ap-southeast-2:102460195799:secret:DUMMY_PASSWORD-1z45re'
        sec = sm.Secret.from_secret_arn(self, 'SEC', secretarn)
        repo = ecr.Repository.from_repository_name(self, "repo", repository_name=clusterconfig['ecrreponame'])
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "FargateService",
                                                           cluster=cluster,
                                                           cpu=clusterconfig['containercpu'],
                                                           desired_count=clusterconfig['containercount'],
                                                           # this is a mandatory option with Fargate
                                                           memory_limit_mib=clusterconfig['containermem'],
                                                           task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                               image=ecs.EcrImage.from_ecr_repository(repo),
                                                               container_port=clusterconfig['listenport'],
                                                               environment={
                                                                   'VTT_DBUSER': clusterconfig['dbuser'],
                                                                   'VTT_DBNAME': clusterconfig['dbname'],
                                                                   'VTT_DBHOST': dbendpoint,
                                                                   # Hard-wiring this because RDS Aurora listens on 3306 (mysql!) even when set to postgresql by default
                                                                   # fends off confusion and grief and anger
                                                                   'VTT_DBPORT': '3306',
                                                                   'VTT_LISTENHOST': clusterconfig['listenhost'],
                                                                   'VTT_LISTENPORT': str(clusterconfig['listenport']),
                                                               },
                                                               secrets={
                                                                   # 'VTT_DBPASSWORD': ecs.Secret.from_secrets_manager(dbsecret)
                                                                   'VTT_DBPASSWORD': ecs.Secret.from_secrets_manager(sec)
                                                               }
                                                           ),
                                                           public_load_balancer=True,
                                                           assign_public_ip=True)
        return cluster

