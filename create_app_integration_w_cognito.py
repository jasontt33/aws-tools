import boto3
from botocore.exceptions import ClientError
import argparse
import sys


def get_args():
    parser = argparse.ArgumentParser(
        description='Create a new user pool client for a Cognito user pool')
    parser.add_argument('arg1', help='The ID of the user pool')
    parser.add_argument('arg2', help='The name of the new user pool client')
    parser.add_argument('arg3', help='Cognito Domain, e.g. stand_together_google')

    args = parser.parse_args()
    return args

def create_user_pool_client(user_pool_id, client_name, cognito_domain):
    """Create a new user pool client for a Cognito user pool

    :param user_pool_id: The ID of the user pool
    :param client_name: The name of the new user pool client
    :return: The ID and secret of the new user pool client
    """

    # Create a Cognito client
    cognito = boto3.client('cognito-idp')
    # Set the read and write attributes
    read_attributes = ReadAttributes=['email', 'given_name', 'family_name']
    write_attributes = WriteAttributes=['email', 'given_name', 'family_name']
    # Create the user pool client
    try:
        response = cognito.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            GenerateSecret=True,
            RefreshTokenValidity=30,
            ReadAttributes=read_attributes,
            ExplicitAuthFlows= [
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
            ],
            WriteAttributes=write_attributes)
        client_id = response['UserPoolClient']['ClientId']
        client_secret = response['UserPoolClient']['ClientSecret']
        return response, client_id, client_secret
    
    except ClientError as e:
        print(e.response['Error']['Message'])
        sys.exit(1)

def create_user_pool_domain(client_id, user_pool_id, cognito_domain):
    
    # Create a Cognito client
    cognito = boto3.client('cognito-idp')
    response = cognito.create_user_pool_domain(
        Domain=cognito_domain,
        UserPoolId=user_pool_id,
    )

    domain_name = response['DomainDescription']['Domain']
    try:
        response = cognito.update_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
            ],
            SupportedIdentityProviders=['COGNITO'],
            CallbackURLs=['http://localhost:5000/postlogin'],
            LogoutURLs=['http://localhost:5000/postlogout'],
            AllowedOAuthFlowsUserPoolClient=True,
            AllowedOAuthFlows=['implicit'],
            AllowedOAuthScopes=['openid'],
            AllowedCorsOrigins=['http://localhost:5000'],
            EnableTokenRevocation=True,
            AccessTokenValidity=3600,
            IdTokenValidity=3600,
            RefreshTokenValidity=3600,
            ReadAttributes=['email', 'given_name', 'family_name'],
            WriteAttributes=['email', 'given_name', 'family_name'],
            PreventUserExistenceErrors='ENABLED',
            SupportedUILocales=['en_US'],
            UserPoolDomain=domain_name,
        )
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
        sys.exit(1)

def main():
    """Exercise the create_user_pool_client function"""

    # Get the command line arguments
    args = get_args()
    user_pool_id = args.arg1
    client_name = args.arg2
    cognito_domain = args.arg3

    # Create the user pool client
    response, client_id, client_secret = create_user_pool_client(
        user_pool_id, client_name, cognito_domain)
    create_user_pool_domain(client_id,user_pool_id, cognito_domain)

    # Display the new user pool client
    print('ID: ' + client_id)
    print('Secret: ' + client_secret)
    print('Response: ' + str(response))

if __name__ == '__main__':
    main()