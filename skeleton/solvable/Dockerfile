FROM avatao/debian:buster

COPY ./solvable/ /

WORKDIR /home/user/

RUN chown -R user: /home/user

USER user
EXPOSE 8888

CMD ["/home/user/vmmigration"]
