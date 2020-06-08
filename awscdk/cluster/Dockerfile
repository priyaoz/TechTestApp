FROM python:3.6-alpine

VOLUME "/root/.aws"
ENV AWS_PROFILE=default

RUN \
    apk add --update nodejs npm && \
    npm install -g aws-cdk && \
    pip install --upgrade aws-cdk.core && \
    echo "First RUN done"

COPY ./ .

RUN \
    pip install -r requirements.txt && \
    echo "Second RUN done"

# ENTRYPOINT ["cdk", "deploy", "--strict", "--require-approval=never"]
ENTRYPOINT ["cdk", "--asset-metadata=false", "--path-metadata=false", "synth"]
CMD [""]

