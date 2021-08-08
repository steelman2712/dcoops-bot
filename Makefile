start-webapp: 
	docker-compose -f docker-compose.yml up --build webapp

lint: 
	 black --exclude 'venv/*|alembic/*' . &&  flake8 --ignore=E501,E402 --exclude=venv/,alembic/