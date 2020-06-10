
# temporarily attach an IGW and routes to the DB subnets, just to init that damn DB

vpc=$(aws ec2 describe-vpcs --filter 'Name=cidr,Values=10.0.0.0/16' --query 'Vpcs[0].VpcId' --output text)
igw=$(aws ec2 describe-internet-gateways --filters 'Name=tag:aws:cloudformation:stack-name,Values=TTAVPC' --query 'InternetGateways[].InternetGatewayId' --output text)

rtb1=$(aws ec2 describe-route-tables --filter "Name=vpc-id,Values=vpc-057facb00bc339b20" 'Name=tag:Name,Values=TTAVPC/VPC/DBSubnet1' --query 'RouteTables[].RouteTableId' --output text)
rtb2=$(aws ec2 describe-route-tables --filter "Name=vpc-id,Values=vpc-057facb00bc339b20" 'Name=tag:Name,Values=TTAVPC/VPC/DBSubnet2' --query 'RouteTables[].RouteTableId' --output text)
rtb3=$(aws ec2 describe-route-tables --filter "Name=vpc-id,Values=vpc-057facb00bc339b20" 'Name=tag:Name,Values=TTAVPC/VPC/DBSubnet3' --query 'RouteTables[].RouteTableId' --output text)

aws ec2 create-route --route-table-id "${rtb1}" --destination-cidr-block '0.0.0.0/0' --gateway-id "${igw}"
aws ec2 create-route --route-table-id "${rtb2}" --destination-cidr-block '0.0.0.0/0' --gateway-id "${igw}"
aws ec2 create-route --route-table-id "${rtb3}" --destination-cidr-block '0.0.0.0/0' --gateway-id "${igw}"

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

# aws ec2 delete-route --route-table-id "${rtb21}" --destination-cidr-block '0.0.0.0/0'
# aws ec2 delete-route --route-table-id "${rtb22}" --destination-cidr-block '0.0.0.0/0'
# aws ec2 delete-route --route-table-id "${rtb23}" --destination-cidr-block '0.0.0.0/0'

exit 0
