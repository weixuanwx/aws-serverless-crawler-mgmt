import json
import sys
import os

import logging
import boto3


from crawlers.workday_crawler import crawl_workday

#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up S3 connection resource
s3 = boto3.resource("s3")

output_bucket = os.getenv("FEED_BUCKET_NAME")
output_folder_path = os.getenv("S3_OUTPUT_FOLDER_PATH")



def crawl(event):
    crawl_function_dispatch = {
						    'workday': crawl_workday
                            }

    totaljobs, res = crawl_function_dispatch[event['crawler_function']](event, s3, output_bucket, output_folder_path)

    print("Total {} jobs from {}: {}".format(totaljobs, event['company_name'], event['crawler_function']))


print("EXECUTING...")

print("S3_OUTPUT_BUCKET = {}".format(output_bucket))
print("S3_OUTPUT_FOLDER_PATH = {}".format(output_folder_path))
print("boto3 s3 response check = {}".format(s3.meta.client.head_bucket(Bucket=output_bucket)))

if __name__ == "__main__":
    try:
        event = json.loads(sys.argv[1])
    except IndexError:
        event = {}
    crawl(event)