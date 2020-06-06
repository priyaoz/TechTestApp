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

from aws_cdk import \
(
    core,
    aws_iam as iam,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_codepipeline as cpl,
    aws_codepipeline_actions as cpactions,
)


class TTAPipeline(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *,
                 rolearn, githubtokenarn, githubtokenkey, githubrepoowner, githubrepo,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = cpl.Pipeline(self, "TTAPipeline", pipeline_name='TTAPipeline')

        source_action, source_artifact = self.get_source(owner=githubrepoowner, repo=githubrepo,
                                                         smarn=githubtokenarn, smkey=githubtokenkey)
        pipeline.add_stage(stage_name="TTASource", actions=[source_action])

        build_action, build_artifact = self.get_build(sourceartifact=source_artifact)
        pipeline.add_stage(stage_name="TTABuild", actions=[build_action])

        # deploy_action = self.get_deploy(buildartifact=build_artifact)
        # pipeline.add_stage(stage_name="TTADeploy", actions=[deploy_action])

    def get_source(self, *, owner, repo, smarn, smkey):
        source_artifact = cpl.Artifact()
        source_action = cpactions.GitHubSourceAction(
            action_name="Github_Source",
            output=source_artifact,
            owner="Marakai",
            repo="TechTestApp",
            oauth_token=self.get_token(smarn=smarn, smkey=smkey)
        )
        return source_action, source_artifact

    def get_build(self, *, sourceartifact, buildspec='buildspec.yml'):
        build_artifact = cpl.Artifact()
        build_spec = codebuild.BuildSpec.from_source_filename(buildspec)
        build_project = codebuild.PipelineProject(self, "TTABuild", build_spec=build_spec)
        build_action = cpactions.CodeBuildAction(
            action_name="CDK_Build",
            project=build_project,
            input=sourceartifact,
            outputs=[build_artifact]
        )
        return build_action, build_artifact

    @staticmethod
    def get_deploy(*, buildartifact):
        deploy_action = cpactions.CodeDeployEcsDeployAction(
            action_name="CDK_Deploy",
            input=buildartifact)
        return deploy_action

    @staticmethod
    def get_token(*, smarn, smkey):
        return core.SecretValue.secrets_manager(secret_id=smarn, json_field=smkey)
