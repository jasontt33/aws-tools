import boto3

client = boto3.client('cloudwatch')

alarms_to_delete = []

# Get a list of all alarms with insufficient data
response = client.describe_alarms(StateValue='INSUFFICIENT_DATA')

# Add the names of the alarms to the list of alarms to delete
for alarm in response['MetricAlarms']:
    alarms_to_delete.append(alarm['AlarmName'])

# Delete all alarms in the list
for alarm_name in alarms_to_delete:
    response = client.delete_alarms(AlarmNames=[alarm_name])
    print('Deleted alarm: ' + alarm_name)

