FROM avatao/webide-c:ubuntu-16.04

COPY ./solvable/ /

RUN  chown -R user: /solvable/src \
    && mkdir /solvable/wd && ln -s /solvable/src/app.c /solvable/wd/app.c \
    && chmod 600 /solvable/server.py \
    && chmod 600 /solvable/test/* \
    && chmod 700 /solvable/test \
    && python3 /opt/setup.py /solvable/wd /solvable/wd/app.c \
    && chmod 444 /var/www/codiad/data/projects.php \
    && mkdir /solvable/build && cd /solvable/build \
    && cmake /solvable \
    && make

# Usage of the setup script (/opt/setup.py):
# python3 /opt/setup.py /PATH/OF/WORKING/DIRECTORY /PATH/OF/FILE/TO/OPEN/IN/WEBIDE

WORKDIR /solvable

VOLUME ["/solvable", "/var/lib/nginx", "/var/lib/php"]
VOLUME ["/var/www/codiad/data", "/var/www/codiad/plugins", "/var/www/codiad/themes", "/var/www/codiad/workspace"]
