FROM alpine
RUN apk add --no-cache python3 bash && pip3 install docker
ENV ShR_SERVERS="192.168.66.100 192.168.66.101 192.168.66.102 192.168.66.103 192.168.66.104 192.168.66.105 192.168.66.106 192.168.66.107"
ENV ShR_IMAGE="ubuntu"
COPY main.py /
CMD python3 /main.py