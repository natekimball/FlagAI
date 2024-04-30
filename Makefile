run:
	python manage.py runserver

shell:
	python manage.py shell

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

test:
	python manage.py test

start:
	sudo service postgresql start

stop:
	sudo service postgresql stop

pg-shell:
	sudo -U psql

.PHONY: run, shell, migrations, migrate, start, stop, pg-shell
