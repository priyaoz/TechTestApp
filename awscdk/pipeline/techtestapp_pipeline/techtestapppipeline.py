#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""

.. module:: techtestapp-pipeline.techtestapppipeline.py
    :platform: Unix
    :synopsis:
        Create an AWS CodePipeline stack through the AWS CDK in Python.

        This becomes the CI/CD pipeline to automate deployment of the TechTestApp infrastructure
        for the Servian hiring test.

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
    aws_iam as iam,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_codepipeline as cpl,
    aws_codepipeline_actions as cpactions,
    aws_ecr as ecr,
)


class TTAPipeline(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, pipeline_config, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = cpl.Pipeline(self, "TTAPipeline", pipeline_name='TTAPipeline')

        githubtokenarn = f"arn:aws:secretsmanager:{pipeline_config['region']}:{pipeline_config['accountid']}:secret:{pipeline_config['githubtokenname']}"
        source_action, source_artifact = self._get_source(owner=pipeline_config['githubrepoowner'],
                                                          repo=pipeline_config['githubreponame'],
                                                          branch=pipeline_config['buildbranch'],
                                                          secmgrarn=githubtokenarn,
                                                          secmgrkey=pipeline_config['githubtokenkey'])
        pipeline.add_stage(stage_name="TTASource", actions=[source_action])

        build_action, build_artifact = self._get_build(sourceartifact=source_artifact, pipeline_config=pipeline_config)
        pipeline.add_stage(stage_name="TTABuild", actions=[build_action])

        cbuild_action, cbuild_artifact = self._get_clusterbuild(sourceartifact=build_artifact, pipeline_config=pipeline_config)
        pipeline.add_stage(stage_name="TTACluster", actions=[cbuild_action])

    def _get_source(self, *, owner, repo, branch='master', secmgrarn, secmgrkey):
        """
        The magic to link CodePipeline up to Github.
        The access tokens must be created separately in AWS SecretsManager for security.
        At this time AWS CDK does NOT support using SecureString in Parameter Store, so
        it's US$0.40/month per secret and US$0.05 per 10,000 access

        :param owner: The Github user account name
        :param repo: The name of the repository
        :param branch: Branch name, defaults to master
        :param secmgrarn: The SecretsManager name ARN for the Github access token
        :param secmgrkey: The SecretsManager key name for the access token
        :return: Tuple of Github source action and the CDK source artifact
        """
        source_artifact = cpl.Artifact()
        source_action = cpactions.GitHubSourceAction(
            action_name="Github_Source",
            output=source_artifact,
            owner=owner,
            repo=repo,
            branch=branch,
            oauth_token=self._get_token(secmgrarn=secmgrarn, secmgrkey=secmgrkey)
        )
        return source_action, source_artifact

    def _get_build(self, *, sourceartifact, pipeline_config, buildspec='buildspec.yml'):
        """
        Create the CodeBuild environment and define what YAML file to control the actual
        build with.
        Will also create the ECR repo, as we are, after all, building and pushing out an
        app in a container.

        :param sourceartifact: Passed in from the creation of the Source stage
        :param buildspec: Name of the buildspec file, defaults by convention to buildspec.yml
        :return: Tuble of CodeBuild action and CodeBuild artifact
        """

        valid_ecrname = f"{pipeline_config['githubreponame'].lower()}_ecr"
        valid_cluster_ecrname = f"{pipeline_config['githubreponame'].lower()}_cluster_ecr"
        build_artifact = cpl.Artifact()
        build_spec = codebuild.BuildSpec.from_source_filename(buildspec)
        build_project = codebuild.PipelineProject(self, "TTABuild",
                                                  build_spec=build_spec,
                                                  environment=codebuild.BuildEnvironment(
                                                      privileged=True,
                                                      build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                                                      compute_type=codebuild.ComputeType.SMALL,
                                                  ),
                                                  environment_variables={
                                                      # This one is the actual TechTestApp container
                                                      'IMAGE_REPO_NAME': codebuild.BuildEnvironmentVariable(
                                                          value=valid_ecrname),
                                                      # and this one is the cluster creator, because we can't use CodeDeploy in CDK yet
                                                      'CLUSTER_IMAGE_REPO_NAME': codebuild.BuildEnvironmentVariable(
                                                          value=valid_cluster_ecrname),
                                                      'IMAGE_TAG': codebuild.BuildEnvironmentVariable(value='latest'),
                                                      'AWS_ACCOUNT_ID': codebuild.BuildEnvironmentVariable(
                                                          value=pipeline_config['accountid']),
                                                      'AWS_DEFAULT_REGION': codebuild.BuildEnvironmentVariable(
                                                          value=pipeline_config['region']),
                                                  }
                                                  )
        build_action = cpactions.CodeBuildAction(
            action_name="CDK_Build",
            project=build_project,
            input=sourceartifact,
            outputs=[build_artifact]
        )

        # our build needs an ECR repo to write to
        for reponame in [valid_ecrname, valid_cluster_ecrname]:
            ecrrepo = ecr.Repository(
                self, f'TTAECR{reponame}',
                repository_name=reponame,
                removal_policy=core.RemovalPolicy.DESTROY
            )
            ecrrepo.grant_pull_push(build_project)
            ecrrepo.grant(build_project, 'ecr:SetRepositoryPolicy')

        return build_action, build_artifact

    def _get_clusterbuild(self, *, sourceartifact, pipeline_config, buildspec='clusterspec.yml'):
        """
        Create the CodeBuild environment and define what YAML file to control the actual
        build with.
        Will also create the ECR repo, as we are, after all, building and pushing out an
        app in a container.

        :param sourceartifact: Passed in from the creation of the Source stage
        :param buildspec: Name of the buildspec file, defaults by convention to buildspec.yml
        :return: Tuble of CodeBuild action and CodeBuild artifact
        """
        valid_cluster_ecrname = f"{pipeline_config['githubreponame'].lower()}_cluster_ecr"
        build_artifact = cpl.Artifact()
        build_spec = codebuild.BuildSpec.from_source_filename(buildspec)
        build_project = codebuild.PipelineProject(self, "TTACluster",
                                                  build_spec=build_spec,
                                                  environment=codebuild.BuildEnvironment(
                                                      privileged=True,
                                                      build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
                                                      compute_type=codebuild.ComputeType.SMALL,
                                                  ),
                                                  environment_variables={
                                                      # and this one is the cluster creator, because we can't use CodeDeploy in CDK yet
                                                      'CLUSTER_IMAGE_REPO_NAME': codebuild.BuildEnvironmentVariable(
                                                          value=valid_cluster_ecrname),
                                                      'IMAGE_TAG': codebuild.BuildEnvironmentVariable(value='latest'),
                                                      'AWS_ACCOUNT_ID': codebuild.BuildEnvironmentVariable(
                                                          value=pipeline_config['accountid']),
                                                      'AWS_DEFAULT_REGION': codebuild.BuildEnvironmentVariable(
                                                          value=pipeline_config['region']),
                                                  }
                                                  )
        build_action = cpactions.CodeBuildAction(
            action_name="CDK_Build",
            project=build_project,
            input=sourceartifact,
            outputs=[build_artifact]
        )

        return build_action, build_artifact

    @staticmethod
    def _get_deploy(*, buildartifact):
        """
        Not used yet. This should handle the actual fancy deployment of the container in
        an ECS/Fargate cluster. One thing at a time.

        NOTE: To clarify, as of writing this, ECS deploys are not yet supported in AWS CDK!

        :param buildartifact: Passed in from the creation of the Build stage
        :return: CodeDeploy action
        """
        deploy_action = cpactions.CodeDeployEcsDeployAction(
            action_name="CDK_Deploy",
            input=buildartifact)
        return deploy_action

    @staticmethod
    def _get_token(*, secmgrarn, secmgrkey):
        """
        Go to AWS SecretsManager and get the Github token as a SecretValue object.

        :param secmgrarn: SecretManager ARN of the Secret name
        :param secmgrkey: SecretManager key
        :return: SecretValue (as required by CodeBuild)
        """
        return core.SecretValue.secrets_manager(secret_id=secmgrarn, json_field=secmgrkey)

    @staticmethod
    def get_pipeline_config(configfile='pipeline.toml'):
        """
        Read pipeline config parameters from a TOML file.

        :param configfile: File name, defaults to pipeline.toml
        :return: Dict of the [codepipeline] section
        """
        # Servian are TOML fans it seems...
        pipeline_config = toml.load(configfile)['codepipeline']

        return pipeline_config
