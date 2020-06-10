source ./vpcdata.sh

pcx=$(aws ec2 create-vpc-peering-connection --vpc-id ${vpc1} --peer-vpc-id ${vpc2} --query 'VpcPeeringConnection.VpcPeeringConnectionId' --output text)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id ${pcx}

aws ec2 create-route --route-table-id ${rtb1} --destination-cidr-block ${cidr2} --vpc-peering-connection-id ${pcx}
aws ec2 create-route --route-table-id ${rtb21} --destination-cidr-block ${cidr1} --vpc-peering-connection-id ${pcx}
aws ec2 create-route --route-table-id ${rtb22} --destination-cidr-block ${cidr1} --vpc-peering-connection-id ${pcx}
aws ec2 create-route --route-table-id ${rtb23} --destination-cidr-block ${cidr1} --vpc-peering-connection-id ${pcx}

dbep=$(aws rds describe-db-cluster-endpoints --query 'DBClusterEndpoints[?EndpointType==`WRITER`].Endpoint' --output text)
docker run \
	-e VTT_PASSWORD=$(aws secretsmanager get-secret-value --secret-id VTT_PW --query 'SecretString' --output text) \
	-e VTT_DBHOST=${dbep} \
	-e VTT_DBUSER=postgres \
	-e VTT_DBNAME=app \
	-e VTT_DBPORT=3306 \
	-e VTT_LISTENHOST=0.0.0.0 \
	-e VTT_LISTENPORT=3000 \
	102460195799.dkr.ecr.ap-southeast-2.amazonaws.com/techtestapp_ecr:latest updatedb -s

# aws ec2 delete-route --route-table-id ${rtb1} --destination-cidr-block ${cidr2}
# aws ec2 delete-route --route-table-id ${rtb21} --destination-cidr-block ${cidr1}
# aws ec2 delete-route --route-table-id ${rtb22} --destination-cidr-block ${cidr1}
# aws ec2 delete-route --route-table-id ${rtb23} --destination-cidr-block ${cidr1}

# aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id ${pcx}

exit 0
