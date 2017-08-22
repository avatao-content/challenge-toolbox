FROM avatao/java-controller:ubuntu-16.04
MAINTAINER Gergo Turcsanyi <gergo.turcsanyi@avatao.com>

COPY ./controller/ /

RUN cd /home/user/test \
	&& find . -type f -exec chmod 744 {} + \
	&& chown -R controller:controller /home/user/test \
	&& chown root:root /home/user/test/ProgramTest.java

VOLUME ["/home/user/test"]

USER controller
