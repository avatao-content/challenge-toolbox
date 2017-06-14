FROM avatao/controller:ubuntu-14.04

USER root
RUN apt-get -qy update \ 
	&& apt-get install -qy libfontconfig

COPY ./controller /

RUN chown -R user:user /opt

VOLUME ["/opt"]

USER user
