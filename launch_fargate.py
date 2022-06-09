import json
import os
import boto3

ECSCluster = os.environ["ECS_CLUSTER"]
ECSSecGroup = os.environ["ECS_SEC_GROUP"]
ECSSubnet = os.environ["ECS_SUBNET"]
ECSTaskArn = os.environ["ECS_TASK_ARN"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
output_bucket = os.getenv("FEED_BUCKET_NAME")
output_folder_path = os.getenv("S3_OUTPUT_FOLDER_PATH")

def test(event, context):
    body = {
        "message": {"ECSCluster":ECSCluster
                    ,"CONTAINER_NAME":CONTAINER_NAME
                    ,"output_bucket":output_bucket
                    ,"output_folder_path":output_folder_path},
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response



def launch_fargate(event, context):
    client = boto3.client("ecs")

    run_task_response = client.run_task(
        cluster=ECSCluster,
        taskDefinition=ECSTaskArn,
        count=1,
        launchType="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": CONTAINER_NAME,
                    # We override the command so that we can pass some arguments
                    # e.g. for running different spiders.
                    "command": [
                        "python",
                        "main.py",
                        json.dumps(event),
                    ]
                }
            ],
        },
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [
                    # ECS_TASK_VPC_SUBNET_1,
                    # ECS_TASK_VPC_SUBNET_2
                    ECSSubnet
                ],
                "securityGroups": [
                    ECSSecGroup,
                ],
                "assignPublicIp": "ENABLED"
            },
        },
    )
    return json.dumps(run_task_response, default=str)