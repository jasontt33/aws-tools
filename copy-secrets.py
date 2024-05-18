import boto3
import json

# Create a Secrets Manager client
client = boto3.client('secretsmanager')

# Function to get a secret
def get_secret(secret_name):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        # Check if the secret is a string or binary
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            # For binary secret, decode it
            return base64.b64decode(get_secret_value_response['SecretBinary'])
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        return None

# Function to create or update a secret
def create_or_update_secret(secret_name, secret_value):
    try:
        response = client.create_secret(Name=secret_name, SecretString=secret_value)
        print(f"Secret {secret_name} created successfully.")
    except client.exceptions.ResourceExistsException:
        try:
            # If secret already exists, update it
            response = client.update_secret(SecretId=secret_name, SecretString=secret_value)
            print(f"Secret {secret_name} updated successfully.")
        except Exception as e:
            print(f"Error updating secret {secret_name}: {e}")

# Main execution
source_secret_name = 'dev/feedback-app'
destination_secret_name = 'staging/feedback-app'

# Get the secret from the source
source_secret_value = get_secret(source_secret_name)

if source_secret_value:
    # Create or update the destination secret
    create_or_update_secret(destination_secret_name, source_secret_value)

