FROM nginx:1.15
RUN apt-get clean && apt-get update && apt-get install -y \
    spawn-fcgi \
    fcgiwrap \
    libcgi-pm-perl \
    libdbi-perl \
    libutf8-all-perl \
    libdbd-mysql-perl \
    && rm -rf /var/lib/apt/lists/*
RUN sed -i 's/www-data/nginx/g' /etc/init.d/fcgiwrap
RUN chown nginx:nginx /etc/init.d/fcgiwrap
COPY ./config/conf.d/ /etc/nginx/conf.d/
COPY ./config/entrypoint.sh /

WORKDIR /var/www
COPY ./app/ ./

ENV DB_HOST=web_db
ENV DB_NAME=valg
ENV DB_USER=valg
ENV DB_PASS=secret
ENV ADMIN_UID=1234

ENTRYPOINT [ "/entrypoint.sh" ]