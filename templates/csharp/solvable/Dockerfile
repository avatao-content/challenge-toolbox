FROM avatao/webide:ubuntu-14.04

USER root

COPY ./solvable/ /

# Usage of setup.py
# python3 /opt/setup.py <WORKING DIRECTORY> <FILE TO OPEN IN WEBIDE>
RUN chown -R user:user /home/user/solvable \
	&& python3 /opt/setup.py /home/user/solvable /home/user/solvable/Program.cs \
	&& chmod 444 /var/www/codiad/data/projects.php

VOLUME ["/home/user/solvable"]
VOLUME ["/tmp", "/var/log", "/var/lib/php5"]
VOLUME ["/var/www/codiad/data", "/var/www/codiad/plugins", "/var/www/codiad/themes", "/var/www/codiad/workspace"]
VOLUME ["/var/run/php-fpm", "/var/cache/nginx", "/run"]

USER user

CMD ["supervisord", "-c", "/etc/supervisor/nginx-php.conf"]
