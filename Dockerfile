FROM python:3.8
WORKDIR /usr/src/app
RUN python -m pip install "poetry==1.1.4"
ENTRYPOINT [ "poetry" ]
