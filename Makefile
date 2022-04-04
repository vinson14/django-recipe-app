test:
	docker-compose run app sh -c "python manage.py test"

test-lint:
	docker-compose run app sh -c "python manage.py test && flake8"

migrate-core:
	docker-compose run app sh -c "python manage.py makemigrations core"