from aws_cdk import (
    Duration,
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class CiCdStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, conf: dict,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_upload_policy_statement = iam.PolicyStatement(
                                    sid="WriteSourceS3",
                                    effect=iam.Effect.ALLOW,
                                    actions=[
                                        "s3:PutObject*"
                                    ],
                                    resources=[
                                        "*",
                                    ]
        )
        s3_download_policy_statement = iam.PolicyStatement(
                                    sid="ReadSourceS3",
                                    effect=iam.Effect.ALLOW,
                                    actions=[
                                        "s3:GetBucket*",
                                        "s3:GetObject*",
                                        "s3:List*"
                                    ],
                                    resources=[
                                        "*",
                                    ]
        )

        cf_policy_statement = iam.PolicyStatement(
            sid="CloudFormation",
            effect=iam.Effect.ALLOW,
            actions=[
                "cloudformation:DescribeStacks",
                "cloudformation:GetTemplate",
            ],
            resources=[
                "*",
            ]
        )
        sts_policy_statement = iam.PolicyStatement(
            sid="STS",
            effect=iam.Effect.ALLOW,
            actions=[
                "sts:AssumeRole",
                "iam:PassRole"
            ],
            resources=[
                "arn:aws:iam::" + conf['aws_account'] + ":role/cdk*",
            ]
        )

        ecr_policy_statement = iam.PolicyStatement(
            sid="ECR",
            effect=iam.Effect.ALLOW,
            actions=[
                "ecr:BatchCheckLayerAvailability",
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "ecr:CreateRepository",
                "ecr:DeleteRepository",
                "ecr:DescribeImages",
                "ecr:DescribeRepositories",
                "ecr:GetAuthorizationToken",
                "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload",
                "ecr:ListImages",
                "ecr:PutImage",
                "ecr:PutLifecyclePolicy",
                "ecr:UploadLayerPart"
            ],
            resources=[
                "*",
            ]
        )

        source_output = codepipeline.Artifact()

        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="Github_Source",
            owner=conf["environment"]["owner"],
            repo=conf["environment"]["repo"],
            output=source_output,
            connection_arn=conf["environment"]["codestar-connection"]
            action_name="SourceBE",
        )

        build_project = codebuild.PipelineProject(self, "CodeBuildAppBuild",
            project_name="BuildJavaApp",
            build_spec=codebuild.BuildSpec.from_source_filename("cicd/buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_4, privileged=True
            ),
            environment_variables={"ENVIROMENT": codebuild.BuildEnvironmentVariable(value="common")},
            timeout=Duration.minutes(20)
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output
        )

        self.codepipeline_project = codepipeline.Pipeline(self, "BuildJavaApp",
                                            pipeline_name="BuildJavaApp",
                                            stages=[codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                                                    codepipeline.StageProps(stage_name="Build", actions=[build_action])]
                                            )
        build_project.add_to_role_policy(cf_policy_statement)
        build_project.add_to_role_policy(sts_policy_statement)
        build_project.add_to_role_policy(s3_upload_policy_statement)
        build_project.add_to_role_policy(s3_download_policy_statement)
        build_project.add_to_role_policy(ecr_policy_statement)