import json
import boto3
import base64
from botocore.exceptions import ClientError


class TransferPw:
    """
    Kludge class to grab the actual PW from the RDS secrets attachment format and pack it into another
    'pure' SecretsManager secret.
    This is because Fargate right now, as per the AWS docs cannot deal with secrets with multiple
    elements (represented as JSON, e.h. {'username': 'mike', 'password': 'pw'}.
    So we need to grab that pw and then create a new simple one that we can get the ARN for an inject
    into the stack.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_client(region_name='ap-southeast-2'):
        """
        Create a boto3 client.

        :param region_name: Regon name
        :return: Boto3 client
        """
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        return client

    @staticmethod
    def get_secret(client, secret_name):
        """
        Taken straight from AWS documentation and sample code.
        Modified to return *only* the password as string

        Original comment in this code sample:
        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.
        :param client: Boto3 client
        :param secret_name: SecretsManager name or ARN
        :return: Password as string
        """

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                # always uses this in RDS JSON structure for SecretsAttachment
                jsecret = json.loads(secret)
                return jsecret['password']
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret
        return None

    @staticmethod
    def set_secret(client, secretname, secretvalue):
        """
        Create a new SecretsManager item or update an existing one.
        Will hold nothing but the password, so Fargate is happy.

        :param client: Boto3 client
        :param secretname: Name of the item in SecretsManager (this is NOT the ARN)
        :param secretvalue: PW as string
        :return: ARN of SecretsManager item
        """
        try:
            response = client.create_secret(
                Name=secretname,
                # hard-wiring this as we're only using it here
                Description='grabbed from RDS for Fargate',
                SecretString=secretvalue,
            )
        # should probably narrow down the exception but trying to get this to work
        except Exception as e:
            response = client.update_secret(
                SecretId=secretname,
                SecretString=secretvalue,
            )
        return response['ARN']

    def transfer_pw(self, *, region, rdssecret, newsecret):
        """
        Take from one and push to the other.
        :param region: Region name
        :param rdssecret: Name or ARN of the SecretsManager RDS item
        :param newsecret: Name for the new SecretsManager item holding only the password
        :return: ARN of new item
        """
        client = self.get_client(region)
        # this isn't perfect, but Python is pretty good with cleaning up after itself internally
        # without the risk of exposing passwords in memory
        newarn = self.set_secret(client,  newsecret, self.get_secret(client, rdssecret))
        return newarn

