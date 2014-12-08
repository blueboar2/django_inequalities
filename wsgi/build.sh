PGPASSWORD="inequality" psql -h "127.0.0.1" -U 'inequality' < ./rename_permissions.sql
/etc/init.d/apache2 restart
