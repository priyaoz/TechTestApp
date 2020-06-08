#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp-cluster.techtestappcluster.py
    :platform: Unix
    :synopsis:
        Create an AWS Fargate Cluster and RDS stack for the TechTestApp through the AWS CDK in Python.

        Shows the power of AWS CDK patterns - what's already fewer lines of imperative code
        becomes even less!

.. moduleauthor:: Michael Hoffmann <michaelh@centaur.id.au>

"""

import toml
from aws_cdk import \
    (
        core,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_ecr as ecr,
        aws_rds as rds,
        aws_ecs_patterns as ecs_patterns
    )


class TTACluster(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, cluster_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = self.get_newvpc()

        db = self.get_newdb(vpc=vpc)

        cluster = self.make_cluster(vpc=vpc, db=db, ecrreponame="techtestapp_ecr")

        # TODO: proper access control for limited subnets
        # self.allow_cluster_to_db(db=db, cluster=cluster)
        db.connections.allow_default_port_from_any_ipv4('access for Fargate cluster')

    def get_newvpc(self) -> ec2.Vpc:
        """
        Create a new VPC with public and isolated (i.e. private without NAT GW) subnets.
        Public will have an IGW attached. Private subnets only get a RTN to talk between
        themselves and to the public subnets (but not "through" them of course).

        :return: VPC object
        """
        return ec2.Vpc(self, "ClusterVPC",
                       subnet_configuration=[
                           ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.ISOLATED,
                               name="DB",
                               cidr_mask=21
                           ),
                           ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name="Fargate",
                               cidr_mask=21
                           )
                       ],
                       )

    def get_newdb(self, *, vpc) -> rds.DatabaseCluster:
        """
        Create an Aurora RDS cluster in private subnets of the VPC.

        :param vpc: VPC object
        :return: RDS Cluster object
        """
        db = rds.DatabaseCluster(self, 'TTARDS',
                                 # this will automatically create an auto-rotating PW in SecretsManager
                                 master_user=rds.Login(username='postgres'),
                                 engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
                                 engine_version='10.7',
                                 default_database_name='app',
                                 removal_policy=core.RemovalPolicy.DESTROY,
                                 # Probably want this in production or such
                                 # removal_policy=core.RemovalPolicy.RETAIN,
                                 instance_props=rds.InstanceProps(vpc=vpc, vpc_subnets=ec2.SubnetType.PRIVATE,
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

    def make_cluster(self, *, vpc, db, ecrreponame):
        """
        Create an ECS Fargate cluster in public subnets within VPC running the specified container.

        :param vpc: The VPC
        :param db: RDS DB object (to grab secret DB from securely)
        :param ecrreponame: name of ECR repo image
        """
        cluster = ecs.Cluster(self, "TTACluster", vpc=vpc)

        repo = ecr.Repository.from_repository_name(self, "repo", repository_name=ecrreponame)
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "TTAFargateService",
                                                           cluster=cluster,  # Required
                                                           cpu=512,  # Default is 256
                                                           desired_count=2,  # Default is 1
                                                           # this is a mandatory option with Fargate
                                                           memory_limit_mib=2048,
                                                           task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                               image=ecs.EcrImage.from_ecr_repository(repo),
                                                               container_port=3000,
                                                               environment={
                                                                   'VTT_DBUSER': 'postgres',
                                                                   'VTT_DBNAME': 'app',
                                                                   # Aurora listens on 3306 (mysql!) even when set to postgresql by default
                                                                   'VTT_DBHOST': db.cluster_endpoint.hostname,
                                                                   'VTT_DBPORT': '3306',
                                                                   # 'VTT_DBHOST': 'merlot',
                                                                   # 'VTT_DBPORT': '5432',
                                                                   'VTT_LISTENHOST': '0.0.0.0',
                                                                   'VTT_LISTENPORT': '3000',
                                                               },
                                                               # TODO: determine object to inject here without exposing PW
                                                               # secrets={
                                                               #     'VTT_DBPASSWORD': db.secret.something.something.
                                                               # }
                                                           ),
                                                           public_load_balancer=True,
                                                           assign_public_ip=True)  # Default is False
        return cluster

    @staticmethod
    def allow_cluster_to_db(*, db, cluster):
        """
        Set access SGs for RDS cluster to allow Fargate cluster containers to connect.

        :param db: RDS DB object
        :param cluster: ECS Fargate cluster
        """
        # doesn't contain the SGs of the Fargate cluster for some reason, check doco more closely
        for sg in cluster.connections.security_groups:
            db.connections.allow_default_port_from(sg, 'access for Fargate cluster')

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
