import json
import boto3
import os
from uuid import uuid4

session = boto3.Session(profile_name='serverless_dev_user', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ItemsTable')

def create_item(event, context):
    body = json.loads(event['body'])
    item_id = str(uuid4())
    item = {
        'id': item_id,
        'name': body.get('name'),
        'description': body.get('description')
    }
    table.put_item(Item=item)
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Item created", "item": item})
    }

def get_items(event, context):
    response = table.scan()
    items = response.get('Items', [])
    return {
        "statusCode": 200,
        "body": json.dumps(items)
    }

def get_item(event, context):
    item_id = event['pathParameters']['id']
    response = table.get_item(Key={'id': item_id})
    item = response.get('Item')

    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}

    return {"statusCode": 200, "body": json.dumps(item)}

def update_item(event, context):
    item_id = event['pathParameters']['id']
    body = json.loads(event['body'])

    response = table.update_item(
        Key={'id': item_id},
        UpdateExpression='SET #n = :name, #d = :description',
        ExpressionAttributeNames={
            '#n': 'name',
            '#d': 'description'
        },
        ExpressionAttributeValues={
            ':name': body.get('name'),
            ':description': body.get('description')
        },
        ReturnValues="ALL_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Item updated", "item": response['Attributes']})
    }

def delete_item(event, context):
    item_id = event['pathParameters']['id']
    table.delete_item(Key={'id': item_id})

    return {"statusCode": 200, "body": json.dumps({"message": "Item deleted"})}
