VENV_DIR = softeng_venv
REQ_FILE = requirements.txt
SSL_DIRS = back-end/rest_api/ssl back-end/portal-back-end/ssl
API_DIR = back-end/rest_api
PORTAL_DIR = back-end/portal-back-end
DATABASE_DIR = back-end/rest_api/database

.PHONY: all init_venv install_reqs generate_ssl create_env create_db

all: init_venv install_reqs generate_ssl create_env

scratch : init_venv install_reqs generate_ssl create_env create_db

init_venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python -m venv $(VENV_DIR); \
	fi

install_reqs: init_venv
	$(VENV_DIR)/Scripts/pip install -r $(REQ_FILE)

generate_ssl:
	@if [ ! -d "back-end/rest_api/ssl" ]; then \
		mkdir -p back-end/rest_api/ssl; \
	fi; \
	if [ ! -d "back-end/portal-back-end/ssl" ]; then \
		mkdir -p back-end/portal-back-end/ssl; \
	fi; \
	openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "//CN=localhost"; \
	openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt; \
	cp server.* back-end/rest_api/ssl; \
	cp server.* back-end/portal-back-end/ssl;

create_env:
	@if [ ! -f $(DATABASE_DIR)/.env ]; then \
		echo "Enter DB_PASSWORD_LOCAL (the password for the root user of the local database):"; \
		read DBPW; \
		echo "DB_PASSWORD_LOCAL=$$DBPW" > back-end/rest_api/database/.env; \
	fi

create_db:
	@echo "Running database creation script..."
	mysql -uroot -p$(DB_PASSWORD_LOCAL) < $(DATABASE_DIR)/db_create.sql

run_api:
	$(VENV_DIR)/Scripts/python $(API_DIR)/app.py
run_portal: 
	$(VENV_DIR)/Scripts/python $(PORTAL_DIR)/webapp.py 
activate_venv:
	powershell -NoExit -ExecutionPolicy Bypass -Command ". .\$(VENV_DIR)\Scripts\Activate.ps1"
