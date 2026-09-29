.PHONY: setup db kato geography etl etl-demography etl-labor etl-economy validate dev test
setup:
	cp .env.example .env
db:
	docker compose up -d postgres redis
kato:
	docker compose run --rm etl-worker python -m etl kato
geography:
	docker compose run --rm etl-worker python -m etl geography
etl:
	docker compose run --rm etl-worker python -m etl all
etl-demography:
	docker compose run --rm etl-worker python -m etl stat --category demography
etl-labor:
	docker compose run --rm etl-worker python -m etl stat --category labor
etl-economy:
	docker compose run --rm etl-worker python -m etl stat --category economy
validate:
	docker compose run --rm etl-worker python -m etl validate
dev:
	docker compose up --build
test:
	docker compose run --rm backend pytest && docker compose run --rm frontend npm test

