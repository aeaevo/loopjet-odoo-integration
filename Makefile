# Loopjet Odoo Integration - Development Makefile

.PHONY: help build up down restart logs shell clean test upgrade

# Default target
help:
	@echo "Loopjet Odoo Integration - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start services in background"
	@echo "  up-dev     - Start services in development mode"
	@echo "  down       - Stop and remove services"
	@echo "  restart    - Restart all services"
	@echo "  logs       - View logs (follow mode)"
	@echo "  logs-odoo  - View Odoo logs only"
	@echo "  shell      - Open Odoo Python shell"
	@echo "  bash       - Open bash in Odoo container"
	@echo "  psql       - Open PostgreSQL shell"
	@echo "  upgrade    - Upgrade the Loopjet module"
	@echo "  clean      - Stop and remove everything (including volumes)"
	@echo "  test       - Run tests"
	@echo "  status     - Show service status"
	@echo ""

# Build images
build:
	docker-compose build

# Start services (production mode)
up:
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "📍 Odoo: http://localhost:8069"
	@echo "📝 View logs: make logs"
	@echo ""

# Start services (development mode)
up-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ Services started in DEVELOPMENT mode!"
	@echo "📍 Odoo: http://localhost:8069"
	@echo "🔄 Auto-reload enabled"
	@echo "📝 View logs: make logs"
	@echo ""

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart
	@echo "✅ Services restarted!"

# View logs
logs:
	docker-compose logs -f

# View Odoo logs only
logs-odoo:
	docker-compose logs -f odoo

# Open Odoo shell
shell:
	@echo "Opening Odoo shell... (use 'exit()' to quit)"
	@docker-compose exec odoo odoo shell -d loopjet_test || \
		echo "❌ Error: Make sure services are running (make up) and database 'loopjet_test' exists"

# Open bash in Odoo container
bash:
	docker-compose exec odoo bash

# Open PostgreSQL shell
psql:
	docker-compose exec db psql -U odoo -d loopjet_test

# Upgrade the Loopjet module
upgrade:
	@echo "Upgrading Loopjet module..."
	@docker-compose exec odoo odoo -u loopjet_integration -d loopjet_test --stop-after-init || \
		echo "❌ Error: Make sure database 'loopjet_test' exists"
	@echo "Restarting Odoo..."
	@docker-compose restart odoo
	@echo "✅ Module upgraded!"

# Clean everything (including volumes)
clean:
	@echo "⚠️  WARNING: This will delete ALL data including the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✅ Cleaned!"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Run tests (placeholder - customize based on your test setup)
test:
	@echo "Running tests..."
	docker-compose exec odoo odoo -d loopjet_test --test-enable --stop-after-init --log-level=test

# Show service status
status:
	docker-compose ps

# Quick access URLs
urls:
	@echo "🔗 Service URLs:"
	@echo "   Odoo:       http://localhost:8069"
	@echo "   PostgreSQL: localhost:5432"
	@echo ""
	@echo "📊 Default Credentials:"
	@echo "   Database:   loopjet_test"
	@echo "   User:       admin"
	@echo "   Password:   (set during first setup)"
	@echo ""

# Initialize development environment
init:
	@echo "🚀 Initializing development environment..."
	@make build
	@make up
	@echo ""
	@echo "⏳ Waiting for services to be ready (this may take 2-3 minutes)..."
	@sleep 30
	@make status
	@echo ""
	@echo "✅ Environment ready!"
	@make urls

# Backup database
backup:
	@mkdir -p backups
	@echo "📦 Creating backup..."
	@docker-compose exec -T db pg_dump -U odoo loopjet_test > backups/loopjet_test_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

# Restore database from latest backup
restore:
	@if [ -z "$(file)" ]; then \
		echo "❌ Error: Please specify backup file: make restore file=backups/loopjet_test_XXXXXX.sql"; \
		exit 1; \
	fi
	@echo "📥 Restoring from $(file)..."
	@docker-compose exec -T db psql -U odoo loopjet_test < $(file)
	@echo "✅ Database restored!"
	@make restart

