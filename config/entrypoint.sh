#!/bin/bash

echo "fastcgi_param DB_HOST \"$DB_HOST\";" >> /etc/nginx/conf.d/db.vars
echo "fastcgi_param DB_NAME \"$DB_NAME\";" >> /etc/nginx/conf.d/db.vars
echo "fastcgi_param DB_USER \"$DB_USER\";" >> /etc/nginx/conf.d/db.vars
echo "fastcgi_param DB_PASS \"$DB_PASS\";" >> /etc/nginx/conf.d/db.vars

/etc/init.d/fcgiwrap start && nginx -g 'daemon off;'