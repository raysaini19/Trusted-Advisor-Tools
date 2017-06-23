import datetime
import collections
import boto3

cloudtrail = boto3.client('cloudtrail')


def lambda_handler(event, context):
    account_id = event['account_id']
    time_discovered = event['time_discovered']
    username = event['username']
    deleted_key = event['deleted_key']
    exposed_location = event['exposed_location']
    endtime = datetime.datetime.now()
    interval = datetime.timedelta(hours=24)
    starttime = endtime - interval
    print('Retrieving events...')
    events = get_events(username, starttime, endtime)
    print('Summarizing events...')
    event_names, resource_names, resource_types = get_events_summaries(events)
    return {
        "account_id": account_id,
        "time_discovered": time_discovered,
        "username": username,
        "deleted_key": deleted_key,
        "exposed_location": exposed_location,
        "event_names": event_names,
        "resource_names": resource_names,
        "resource_types": resource_types
    }


def get_events(username, starttime, endtime):
    try:
        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': username
                },
            ],
            StartTime=starttime,
            EndTime=endtime,
            MaxResults=50
        )
    except Exception as e:
        print(e)
        print('Unable to retrieve CloudTrail events for user "{}"'.format(username))
        raise(e)
    return response


def get_events_summaries(events):
    event_name_counter = collections.Counter()
    resource_name_counter = collections.Counter()
    resource_type_counter = collections.Counter()
    for event in events['Events']:
        resources = event.get("Resources")
        event_name_counter.update([event.get('EventName')])
        if resources is not None:
            resource_name_counter.update([resource.get("ResourceName") for resource in resources])
            resource_type_counter.update([resource.get("ResourceType") for resource in resources])
    return event_name_counter.most_common(10), resource_name_counter.most_common(10), resource_type_counter.most_common(10)
