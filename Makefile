# Makefile
STACKNAME_BASE="aws-serverless-crawler-mgmt-dev"
REGION="ap-southeast-1"
PROFILE="<YOUR_AWS_PROFILE>"
IMAGE_NAME="<YOUR_DOCKER_IMAGE_NAME>"

build:
	docker build --platform linux/amd64 -t $(IMAGE_NAME):latest .

retag:
	docker tag $(IMAGE_NAME):latest \
		$(shell aws cloudformation --region $(REGION) --profile $(PROFILE) describe-stacks --stack-name $(STACKNAME_BASE) --query "Stacks[0].Outputs[?OutputKey=='ECRRepo'].OutputValue" --output text):latest
	@exec $(shell aws ecr --region $(REGION) --profile $(PROFILE) get-login-password)
	docker push $(shell aws cloudformation --region $(REGION) --profile $(PROFILE) describe-stacks --stack-name $(STACKNAME_BASE) --query "Stacks[0].Outputs[?OutputKey=='ECRRepo'].OutputValue" --output text):latest
