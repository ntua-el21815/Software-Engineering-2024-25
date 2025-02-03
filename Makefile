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
	@for dir in $(SSL_DIRS); do \
		if [ ! -d "$$dir" ]; then \
			mkdir -p $$dir; \
		fi; \
		if [ ! -f "$$dir/server.crt" ] || [ ! -f "$$dir/server.key" ]; then \
			openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout $$dir/server.key -out $$dir/server.crt -subj "/C=GR/ST=Attiki/L=Athens/O=NTUA/OU=Unit/CN=localhost"; \
		fi; \
	done

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
