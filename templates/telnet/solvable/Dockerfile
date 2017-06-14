FROM avatao/ubuntu:14.04

COPY ./solvable/ /

WORKDIR /home/user/

RUN chown -R user: /home/user

USER user

EXPOSE 8888

CMD socat TCP4-LISTEN:8888,fork,rcvbuf=1,reuseaddr EXEC:"python ./encr.py",stderr
