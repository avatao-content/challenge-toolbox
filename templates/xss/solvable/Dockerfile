FROM avatao/lesp:ubuntu-14.04

USER root

RUN rm -fr /var/www/html

COPY ./solvable /

RUN chmod 664 /var/www/*.* \
	&& chown -R www-data:www-data /var/www /db \
	&& chown www-data /var/cache/nginx

VOLUME ["/db"]

USER www-data
