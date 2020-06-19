#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp_cluster.techtestappeks.py
    :platform: Unix
    :synopsis:
        Create an AWS EKS Cluster stack for the TechTestApp through the AWS CDK in Python.

.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

import toml
from aws_cdk import \
    (
        core,
        aws_ec2 as ec2,
        aws_iam as iam,
        aws_eks as eks,
        aws_ecr as ecr,
        aws_ecs_patterns as ecs_patterns,
    )


class TTAEKS(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, vpc, cluster_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.make_eks(vpc=vpc, clusterconfig=cluster_config)

    def make_eks(self, *, vpc, clusterconfig):
        """
        Create an EKS cluster in public subnets within VPC

        :param vpc: The VPC
        :param clusterconfig: Config dict for configuration of RDS and Fargate clusters
        """
        cluster_admin = iam.Role(self, 'AdminRole', assumed_by=iam.AccountRootPrincipal())
        cluster = eks.Cluster(self, "EKSCluster",
                              vpc=vpc,
                              vpc_subnets=[ec2.SubnetType.PUBLIC],
                              masters_role=cluster_admin,
                              output_cluster_name=True
                              )

        repo = ecr.Repository.from_repository_name(self, "repo", repository_name=clusterconfig['ecrreponame'])
        '''
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
                                                                   'VTT_DBPASSWORD': ecs.Secret.from_secrets_manager(sec)
                                                               }
                                                           ),
                                                           public_load_balancer=True,
                                                           assign_public_ip=True)
        '''
        return cluster

