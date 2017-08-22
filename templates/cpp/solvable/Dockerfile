FROM avatao/webide-c:ubuntu-16.04

COPY ./solvable/ /

RUN  chown -R user: /solvable/app \
	&& ln -s /solvable/app /home/user/app \
	&& chmod 600 /solvable/server.py \
	&& chmod 600 /solvable/tests/* \
	&& chmod 700 /solvable/tests \
	&& python3 /opt/setup.py /solvable/app /solvable/app/geomean.cpp \
	&& chmod 444 /var/www/codiad/data/projects.php \
	&& ln -s /solvable/app/geomean.cpp /solvable/tests/geomean.cpp \
	&& cd /solvable/tests \
	&& cmake CMakeLists.txt \
	&& make gtest gtest_main gmock gmock_main

# Usage of the setup script (/opt/setup.py):
# python3 /opt/setup.py /PATH/OF/WORKING/DIRECTORY /PATH/OF/FILE/TO/OPEN/IN/WEBIDE

WORKDIR /solvable/app

VOLUME ["/solvable", "/var/lib/nginx", "/var/lib/php"]
VOLUME ["/var/www/codiad/data", "/var/www/codiad/plugins", "/var/www/codiad/themes", "/var/www/codiad/workspace"]
