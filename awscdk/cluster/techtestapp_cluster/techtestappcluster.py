#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp-cluster.techtestappcluster.py
    :platform: Unix
    :synopsis:
        Create an AWS Fargate Cluster stack through the AWS CDK in Python.

        Shows the power of AWS CDK patterns - what's already fewer lines of imperative code
        becomes even less!

        It is intended to show off the advantages of using imperative (as opposed to descriptive)
        programming languages to create AWS infrastructure. Its flexibility is especially useful,
        when the alternative is to use CloudFormation macros. It also shows the ease in comparison
        to other imperative/procedural approaches such as Troposphere/Awacs, especially when leveraging the
        powerful Assets, which combine multiple CFN Resources into one call,


.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

import toml
from aws_cdk import \
    (
        core,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_ecr as ecr,
        aws_ecs_patterns as ecs_patterns
    )


class TTACluster(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, cluster_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # vpc = ec2.Vpc(self, "ClusterVpc", max_azs=3)  # default is all AZs in region
        vpc = ec2.Vpc(self, "ClusterVPC",
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              subnet_type=ec2.SubnetType.ISOLATED,
                              name="DB",
                              cidr_mask=21
                          ),
                          ec2.SubnetConfiguration(
                              subnet_type=ec2.SubnetType.PUBLIC,
                              name="Cluster",
                              cidr_mask=21
                          )
                      ],
                      )

        cluster = ecs.Cluster(self, "TTACluster", vpc=vpc)

        repo = ecr.Repository.from_repository_name(self, "repo", repository_name="techtestapp_ecr")
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "TTAFargateService",
                                                           cluster=cluster,  # Required
                                                           cpu=512,  # Default is 256
                                                           desired_count=2,  # Default is 1
                                                           task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                               image=ecs.EcrImage.from_ecr_repository(repo),
                                                               container_port=3000
                                                           ),
                                                           # memory_limit_mib=2048,  # Default is 512
                                                           public_load_balancer=True,
                                                           assign_public_ip=True)  # Default is False


    @staticmethod
    def get_cluster_config(configfile='cluster.toml'):
        """
               Read pipeline config parameters from a TOML file.

               :param configfile: File name, defaults to pipeline.toml
               :return: Dict of the [codepipeline] section
               """
        # Servian are TOML fans it seems...
        cluster_config = toml.load(configfile)['codepipeline']

        return cluster_config
