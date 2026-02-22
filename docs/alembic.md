# For make migrate or update data bank

```shell
alembic revision --autogenerate -m "$MSG"
alembic upgrade head
```