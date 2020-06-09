#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp_cluster.techtestappvpc.py
    :platform: Unix
    :synopsis:
        Create a new VPC for the TechTestApp through the AWS CDK in Python.
        Creates a public and an isolated subnet in each AZ, the former for
        the Fargate cluster, the latter for RDS

.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

import toml
from aws_cdk import \
    (
        core,
        aws_ec2 as ec2,
    )


class TTAVPC(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, cluster_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = self.get_newvpc()

    def get_newvpc(self) -> ec2.Vpc:
        """
        Create a new VPC with public and isolated (i.e. private without NAT GW) subnets.
        Public will have an IGW attached. Private subnets only get a RTN to talk between
        themselves and to the public subnets (but not "through" them of course).

        :return: VPC object
        """
        return ec2.Vpc(self, 'VPC',
                       subnet_configuration=[
                           ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.ISOLATED,
                               name='DB',
                               cidr_mask=21
                           ),
                           ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name='Fargate',
                               cidr_mask=21
                           )
                       ],
                       )

