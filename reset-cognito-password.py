import boto3
from botocore.exceptions import ClientError

def reset_cognito_user_password(user_pool_id, username, new_password, region='us-east-1'):
    # Create a Cognito Identity Provider client
    client = boto3.client('cognito-idp', region_name=region)

    try:
        # Reset the user's password and require them to change it on next login
        response = client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=new_password,
            Permanent=False
        )
        print("Password has been reset successfully. User must update password on next login.")
        return response
    except ClientError as error:
        print(f"An error occurred: {error}")
        raise error

# Example usage
if __name__ == "__main__":
    USER_POOL_ID = "us-east-1_8ACJAA1gX"
    USERNAME = "roger@example.com"
    NEW_PASSWORD = "ChangeMe123!@#"
    REGION = "us-east-1"  # e.g., 'us-east-1'
    reset_cognito_user_password(USER_POOL_ID, USERNAME, NEW_PASSWORD, REGION)
