FROM python:3.6-alpine

ENV AWS_PROFILE=default

RUN \
    echo "start" && \
    apk add --update nodejs npm && \
    npm install -g aws-cdk && \
    pip install --upgrade aws-cdk.core && \
    echo "CDK installed"

COPY ./ .

RUN \
    pip install -r requirements.txt && \
    echo "CDK stack dependencies installed"


VOLUME "/root/.aws"
ENTRYPOINT ["cdk"]
CMD ["deploy", "--strict", "--require-approval=never"]

