#!/usr/bin/env bash

# attach some needed policies to the Pipeline stack policy
# This is NOT needed everywhere and depends on the IAM roles used for stack deployment
# in your environment. Some people just use admin for build and deployment jobs...

# Find the role name by munging about with grep and awk. Wish there were wildcards :(

pipeline_role=$(aws iam list-roles --output text | grep TTAPipeline-TTACluster | awk -F'/' '{print $2}' | awk '{print $1}')


echo "Attaching required roles to the Pipeline stack CodeBuild role ${pipeline_role}"

aws iam detach-role-policy --policy-arn arn:aws:iam::102460195799:policy/baseIamUserGrants --role-name ${pipeline_role}
aws iam detach-role-policy --policy-arn arn:aws:iam::102460195799:policy/miscAllows --role-name ${pipeline_role}
aws iam detach-role-policy --policy-arn arn:aws:iam::102460195799:policy/limitedIAM --role-name ${pipeline_role}
aws iam detach-role-policy --policy-arn arn:aws:iam::aws:policy/PowerUserAccess --role-name ${pipeline_role}

echo "Displaying attached managed policies"
aws iam list-attached-role-policies --role-name ${pipeline_role}
