#!/bin/bash
set -euo pipefail

ROOTPW="${MYSQL_ROOT_PASSWORD:-root_change_me}"
export MYSQL_ROOT_PASSWORD="$ROOTPW"

mkdir -p /run/mysqld /var/log/nginx
chown -R mysql:mysql /run/mysqld /var/lib/mysql || true

if [[ ! -d /var/lib/mysql/mysql ]]; then
    echo "[*] 初始化 MariaDB 数据目录..."
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql >/dev/null
fi

echo "[*] 启动 mysqld..."
mysqld_safe --user=mysql --datadir=/var/lib/mysql &

mysql_ready() {
    mysqladmin ping -h 127.0.0.1 -uroot --silent >/dev/null 2>&1 \
        || mysqladmin ping --socket=/run/mysqld/mysqld.sock -uroot --silent >/dev/null 2>&1
}

for _ in $(seq 1 90); do
    mysql_ready && break
    sleep 1
done

if ! mysql_ready; then
    echo "[!] MySQL 未就绪"
    exit 1
fi

MARKER=/var/lib/mysql/.sqli_lab_seeded
MYSQL_ROOT=(mysql -uroot)
if [[ -f "${MARKER}" ]]; then
    MYSQL_ROOT=(mysql -uroot -p"${ROOTPW}")
fi

if [[ ! -f "${MARKER}" ]]; then
    echo "[*] 导入题库 SQL（首次启动）..."
    mysql -uroot < /docker-init/01_init.sql
    touch "${MARKER}"
    MYSQL_ROOT=(mysql -uroot -p"${ROOTPW}")
fi

if [[ -n "${DASFLAG:-}" ]]; then
    INSERT_FLAG="$DASFLAG"
    export DASFLAG=no_FLAG
elif [[ -n "${FLAG:-}" ]]; then
    INSERT_FLAG="$FLAG"
    export FLAG=no_FLAG
elif [[ -n "${GZCTF_FLAG:-}" ]]; then
    INSERT_FLAG="$GZCTF_FLAG"
    export GZCTF_FLAG=no_FLAG
else
    INSERT_FLAG="${STATIC_FLAG:-HelloCTF{sql_injection_lab}}"
fi

sql_escape() {
    printf "%s" "$1" | sed "s/'/'\\\\''/g"
}
FLAG_SQL=$(sql_escape "${INSERT_FLAG}")

echo "[*] 写入动态 Flag（flag_store）..."
for db in lv_0 lv_1 lv_2 lv_3 lv_4 lv_5 lv_6 lv_7 lv_8 lv_9 lv_10 lv_11 lv_12 lv_13; do
    "${MYSQL_ROOT[@]}" -e "UPDATE \`${db}\`.\`flag_store\` SET \`flag\`='${FLAG_SQL}' WHERE id=1 LIMIT 1;" || true
done

APP_USER="${MYSQL_APP_USER:-sqli_app}"
APP_PASS="${MYSQL_APP_PASSWORD:-sqli_app_change_me}"
export MYSQL_APP_USER="${APP_USER}"
export MYSQL_APP_PASSWORD="${APP_PASS}"
mkdir -p /root
cat > /root/.my.cnf <<EOF
[client]
host=127.0.0.1
user=${APP_USER}
password=${APP_PASS}
EOF
chmod 600 /root/.my.cnf

export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER="${APP_USER}"
export MYSQL_PASSWORD="${APP_PASS}"
export MYSQL_ADMIN_USER="${MYSQL_ADMIN_USER:-sqli_admin}"
export MYSQL_ADMIN_PASSWORD="${MYSQL_ADMIN_PASSWORD:-sqli_admin_change_me}"
export MYSQL_DATABASE=sqli_lab

cd /code
echo "[*] 启动 Gunicorn..."
gunicorn --workers 2 --threads 4 --timeout 120 -b 127.0.0.1:5000 wsgi:app &

echo "[*] 启动 ttyd..."
ttyd --writable -i 127.0.0.1 -p 7681 -b /terminal bash &

echo "[*] 启动 Nginx..."
exec nginx -g 'daemon off;'
