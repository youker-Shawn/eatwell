#!/bin/bash


# wait for migration until the db service starts
while ! nc -z db 5432 ; do
    echo "Waiting for the MySQL Server"
    sleep 3
done

# python manage.py collectstatic --noinput&&
python manage.py makemigrations &&
python manage.py migrate &&
python manage.py runserver 0.0.0.0:8000

# uwsgi --ini /var/www/html/myproject/uwsgi.ini &&
# # The tail empty command prevents the web container from exiting after executing the script
# tail -f /dev/null

# exec "$@"