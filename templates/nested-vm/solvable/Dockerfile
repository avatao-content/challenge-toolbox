FROM avatao/lesp:ubuntu-14.04

USER root

COPY ./solvable/ /

RUN chmod 664 /var/www/*.* \
	&& touch -t 201606031125 /var/log/nginx/error.log \
	&& touch -t 201606031125 /var/log/nginx/access.log \
	&& touch -t 201606031125 /var/log/nginx \
	&& touch -t 201606031151 /var/log/auth.log \
	&& touch -t 201606031112 /var/www/uploads/prxy.php \
	&& touch -t 201606031112 /var/www/uploads \
	&& touch -t 201606031108 /var/www/uploads/image.jpg \
	&& touch -t 201606031150 /var/www/css/c100.php \
	&& touch -t 201606031150 /var/www/css \
	&& touch -t 201606030000 /var/www/db.php \
	&& touch -t 201606030000 /var/www/index.html \
	&& touch -t 201606030000 /var/www/ok.html \
	&& touch -t 201606030000 /var/www/products.php \
	&& touch -t 201606030000 /var/www/upload.php \
	&& touch -t 201606030000 /var/www/css/bootstrap.min.css \
	&& mkdir /var/log/php5-fpm \
	&& chown -R www-data:www-data /db /var/log/nginx /var/log/php5-fpm /var/cache/nginx /var/www \
	&& chown -R user:user /home/user \
	&& chown syslog /var/log/auth.log \
	&& chmod 777 /var/log \
	&& chown root /var/www/css/c100.php



VOLUME ["/home/user", "/var/log", "/var/run/php-fpm", "/var/lib/php5", "/var/cache/nginx", "/etc/nginx", "/run", "/tmp"]

EXPOSE 2222

WORKDIR /home/user/

USER user

CMD ["/usr/sbin/sshd", "-Df", "/etc/ssh/sshd_config_user"]

