FROM jfloff/alpine-python:recent-slim

# Copy required files
COPY requirements.txt /requirements.txt
COPY service/ /service

# install requirements
RUN /entrypoint.sh -P requirements.txt

CMD ["python", "-m" , "service"]
