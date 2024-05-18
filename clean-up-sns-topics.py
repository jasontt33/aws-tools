import boto3

# Initialize the SNS client
sns = boto3.client('sns')

# Get all the SNS topics
topics = sns.list_topics()['Topics']

# Filter topics with 'testing' in the name
testing_topics = [topic for topic in topics if 'i-0' in topic['TopicArn']]
count = 0
# Delete the testing topics
for topic in testing_topics:
     print(topic)
     count+=1
     sns.delete_topic(TopicArn=topic['TopicArn'])

print(count, ' number of sns topics with testing in the name')

