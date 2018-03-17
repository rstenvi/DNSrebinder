FROM python:2

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install iptables -y

ENTRYPOINT [ "python", "./DNSRebinder.py" ]
CMD ["--help"]


