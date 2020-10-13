FROM jfloff/alpine-python:3.8-slim

# Copy required files
COPY requirements.txt /requirements.txt
COPY service/ /service

# install requirements
RUN /entrypoint.sh -P requirements.txt

CMD ["python", "-u", "-m" , "service"]
