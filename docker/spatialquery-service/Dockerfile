# Parent image
FROM hubmap/api-base-image:1.2.0

LABEL description="HuBMAP SpatialQuery Service"

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# Set up the repository file for the stable version of nginx
RUN set -eux && \
    cat <<'EOF' > /etc/yum.repos.d/nginx.repo
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EOF

# Install nginx, swap in our nginx.conf, install requirements, make start.sh executable, clean up
RUN dnf install --assumeyes nginx gcc-c++ && \
    [ ! -f /etc/nginx/conf.d/default.conf ] || mv /etc/nginx/conf.d/default.conf /tmp/etc_nginx_conf.d_default.conf.ORIGINAL && \
    [ ! -f /etc/nginx/nginx.conf ] || mv /etc/nginx/nginx.conf /tmp/etc_nginx_nginx.conf.ORIGINAL && \
    mv nginx/nginx.conf /etc/nginx/nginx.conf && \
    [ ! -d nginx ] || mv nginx /tmp/nginx_from_WORKDIR && \
    [ ! -f /tmp/verify_uwsgi.sh ] || mv /tmp/verify_uwsgi.sh /tmp/verify_uwsgi.sh.ORIGINAL && \
    pip3.13 install --no-cache-dir --upgrade pip -r app/requirements.txt && \
    chmod a+x start.sh && \
    dnf clean all && \
    rm -rf /var/cache/dnf \
        /var/log/dnf \
        /var/log/yum \
        /root/.cache

# 5000 is for the uwsgi socket, 8080 for nginx
EXPOSE 5000 8080

# Set the entrypoint and make it executable
RUN mv entrypoint.sh /usr/local/bin/entrypoint.sh && \
    chmod a+x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["./start.sh"]