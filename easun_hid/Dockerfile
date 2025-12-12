FROM alpine:3.19

RUN apk add --no-cache python3 py3-pip py3-pyusb py3-requests

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
