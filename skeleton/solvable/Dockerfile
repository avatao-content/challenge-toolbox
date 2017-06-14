FROM avatao/ubuntu:14.04

COPY ./solvable/ /

WORKDIR /home/user/

RUN chown -R user: /home/user

USER user
EXPOSE 8888

CMD ["/home/user/vmmigration"]
