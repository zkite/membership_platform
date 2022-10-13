FROM python:3.9-alpine

ENV APP_DIR /application
WORKDIR ${APP_DIR}

COPY ./application ${APP_DIR}
COPY ./requirements.txt ${APP_DIR}/requirements.txt

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    pip install --upgrade pip setuptools && \
    pip install -r ${APP_DIR}/requirements.txt

CMD ["gunicorn", "-b :5000", "wsgi:app", "--reload"]
