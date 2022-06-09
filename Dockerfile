FROM python:3.7

WORKDIR /usr/src/app

COPY main.py ./
ADD crawlers/ ./crawlers/
COPY requirements.txt ./

RUN pip install boto3 --quiet
RUN pip install -r requirements.txt --quiet

CMD ["python3", "./main.py"]