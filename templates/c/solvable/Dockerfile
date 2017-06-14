FROM avatao/webide-c:ubuntu-14.04

COPY ./solvable/ /

RUN  chown -R user: /solvable/app \
	&& ln -s /solvable/app /home/user/app \
	&& chmod 600 /solvable/server.py \
	&& chmod 600 /solvable/tests/* \
	&& chmod 700 /solvable/tests \
	&& python3 /opt/setup.py /solvable/app /solvable/app/app.c

WORKDIR /solvable/app

VOLUME ["/solvable"]
VOLUME ["/var/www/codiad/data", "/var/www/codiad/plugins", "/var/www/codiad/themes", "/var/www/codiad/workspace"]
