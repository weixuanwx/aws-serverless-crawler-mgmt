# AWS Serverless Crawler
- With thousands of crawlers, management of them could quickly become unwieldy. Adding server management on top of that doesn't help.
- Our crawlers are longer running with timed sleep in between to avoid spamming the site. Therefore, deploying them on a CaaS such as AWS Fargate which charges by computation and memory consumption can be more cost effective than a FAAS like AWS Lambda which charges by the time the code executes.
- Also, any crawlers longer than 15 minutes would be not feasible on AWS Lambda as that is the hard cap limit functions in AWS Lambda at this current point of writing.
- This project uses a AWS Lambda function call to conveniently trigger a AWS Fargate task which crawls files and save them in a AWS S3 bucket

# Setup

## Create a AWS account if you don't already have one

## Serverless framework setup
Serverless Framework makes it easier for us to get the stack up on AWS via our CLI

Install `serverless` CLI using npm:
`npm install -g serverless`

Install plugin to install libraries from requirements.txt
`sls plugin install --name serverless-python-requirements`

Install plugin for cloudformation variables
`sls plugin install --name serverless-cloudformation-sub-variables`


## Add IAM user for serverless framework
- Go to AWS IAM page
- Click on **Users** and then **Add users**.
  - Enter the name. Assign the name clearly e.g. "serverless-admin"
  - Check the **Programmatic access** checkbox.
  - Click **Next** to move to Permissions page
  - Click on **Attach existing policies directly**. 
  - Search for and select **AdministratorAccess** then click **Next: Review**.
  - Click on **Create user**.
- View and copy the **API Key** & **Secret** down. Add them to your aws credentials.
- Repeat the same with another non-admin user, named e.g. "serverless-<PROFILENAME>-agent"
  - but instead of attaching AdministratorAccess, attach this [json](https://gist.github.com/ServerlessBot/7618156b8671840a539f405dea2704c8)
  - Add the following additional policies:
    - s3:* for the s3 resources or your specific s3 bucket
    - logs:PutRetentionPolicy
    - ecr:CreateRepository on FargateECSRepo
    - s3:PutBucketVersioning
    - ecr:PutLifecyclePolicy
    - ec2:AssociateRouteTable
    - ec2:CreateRoute



## Defining ECS Fargate setup using Cloud Formation template
Within fargate-template.yml
- Create a Cloud Formation (CF) template to define the Fargate task
- Reference the variables in the CF template in serverless.yml
	- Resources for variables are defined in the "resources" section in serverless.yml

## Defining s3 bucket
Within s3-template.yml
- Define your s3 bucket resource
- To be reference by 'serverless.yml'

## Defining AWS Lambda Setup
Within serverless.yml
- Define environmental variables and iam roles for the lambda function (variables referenced from fargate-template.yml)
- Define the AWS Lambda functions under the section 'functions'


## Docker Setup
The Docker image container will be built, tagged and pushed to the AWS Elastic Container Registry for AWS Fargate to run.

### Install Docker
Standard installations will do: https://docs.docker.com/desktop/

### Building, retagging and pushing the Docker Container
replace the parameters in the `Makefile`
```
STACKNAME_BASE="YOUR_STACK_NAME_IN_ECS"
REGION="YOUR_PREFERRED_AWS_REGION"
PROFILE="YOUR_AWS_PROFILE_NAME"
IMAGE_NAME="YOUR_DOCKER_ACCT_NAME/aws_fargate_crawler"
```

- `make build`
- `aws ecr get-login-password --region <REGION> --profile <PROFILE> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com`
- `make retag`

### Checking Docker container locally
_Only if you have run `sls deploy` before_
`docker run -it <IMAGE_NAME> sh`

```
docker-compose run \
	-e S3_OUTPUT_BUCKET='<Your S3 Bucket name>' \
    -e S3_OUTPUT_FOLDER_PATH='<Your S3 Bucket folder path>' \
	-e AWS_ACCESS_KEY_ID='<Your key for ease of testing locally only>' \
	-e AWS_SECRET_ACCESS_KEY='<Your key for ease of testing locally only>' \
	crawl
```

### Clean up
`docker-compose down`


## Deploying both AWS Lambda and Fargate
Within serverless.yml
- Add the necessary 'package' (include your files here), 'resources' (include other templates in here) and 'plugins' (includer serverless framework plugins here)
- Add Python and docker requirements in 'custom'
- `sls deploy --verbose`

## Invoking the example Workday Crawler function
- Workday is a Applicant Tracking System. This crawler automatically reads into the public jobs that companies are advertising via Workday.
- It can be used for various company's job posting sites under Workday.
- `sls invoke -f fargateCrawler --log --data '{"crawler_function": "workday", "company_name": "<FOLDER_IN_S3>", "prefixlink": "<INDIVIDUAL_PREFIX_LINK>", "linkWquery": "<PAGINATION_LINK>", "crawlLimit": <PAGINATION_LIMIT>}'`

## Putting the Crawler on Schedule
This section within the serverless.yml will put your function call on AWS Lambda's version of CRON
```
cronHandler:
  handler: launch_fargate.launch_fargate
  description: "Cron for individual crawling process"
  timeout: 30 # optional, in seconds, default is 6
  events:
    - schedule: 
        rate: cron(03 1 ? 1-12 1-7 *) # example
        enabled: true
        input:
          crawler_function: "workday"
          company_name: "<FOLDER_IN_S3>"
          prefixlink: "<INDIVIDUAL_PREFIX_LINK>"
          linkWquery: "<PAGINATION_LINK>"
          crawlLimit: <PAGINATION_LIMIT>
```


# References:
- https://blog.vikfand.com/posts/scrapy-fargate-sls-guide/
