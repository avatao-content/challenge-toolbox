FROM avatao/webide:ubuntu-16.04

USER root

RUN python3 /opt/setup.py /home/user/solvable /home/user/solvable/Program.java \
	&& chmod 444 /var/www/codiad/data/projects.php

COPY ./solvable/ /

RUN chown -R user:user /home/user/solvable

VOLUME ["/home/user/solvable"]
VOLUME ["/tmp", "/var/log", "/var/lib/php", "/var/lib/nginx"]
VOLUME ["/var/www/codiad/data", "/var/www/codiad/plugins", "/var/www/codiad/themes", "/var/www/codiad/workspace"]
VOLUME ["/var/run/php-fpm", "/var/cache/nginx", "/run"]

USER user

CMD ["supervisord", "-c", "/etc/supervisor/nginx-php.conf"]
