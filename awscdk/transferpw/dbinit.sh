
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

