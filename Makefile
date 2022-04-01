test:
	docker-compose run app sh -c "python manage.py test"

migrate-core:
	docker-compose run app sh -c "python manage.py makemigrations core"