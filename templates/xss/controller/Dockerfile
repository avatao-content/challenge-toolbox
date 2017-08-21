FROM avatao/xss-controller:ubuntu-16.04

USER root

COPY ./controller /

RUN chown -R user:user /opt

VOLUME ["/opt"]

USER user
