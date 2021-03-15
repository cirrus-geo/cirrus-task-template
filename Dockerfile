# use any appropriate base docker image
FROM developmentseed/geolambda:2.1.0-python

ENV \
    HOME=/home/cirrus/task

WORKDIR ${HOME}

COPY requirements.txt ./

RUN \
    pip install -r requirements.txt;

ADD . ${HOME}

# Add task to $PATH so AWS Batch can run
COPY task.py /usr/local/bin
