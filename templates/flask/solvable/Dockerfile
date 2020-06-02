FROM avatao/debian:buster
MAINTAINER Turcsanyi Gergo <gergo.turcsanyi@avatao.com>

COPY ./solvable/ /

EXPOSE 8888

USER user

CMD ["python3", "/home/user/server.py"]
