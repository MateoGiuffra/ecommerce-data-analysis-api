Para levantar la app:
*Normal:* poetry run uvicorn src.main:app --reload 
*Shortcut:* poetry run poe dev

Resumen del Flujo de Trabajo
1. Modifica tus modelos en Python.
2. Genera la migración: poetry run alembic revision --autogenerate -m "Mi cambio"
3. Aplica la migración: poetry run alembic upgrade head
4. Ejecuta tu aplicación: poetry run uvicorn src.main:app --reload

Pytest:
*Correr todos los tests:* poetry run pytest
*Solo un file:* poetry run pytest tests/routers/test_auth_router.py -q
*Solo un test:* poetry run pytest tests/routers/test_auth_router.py::test_register_existing_user_returns_conflict -q
*Una clase completa:* poetry run pytest tests/routers/test_auth_router.py::TestAuthRouter -q
*Solo un method de una clase:* poetry run pytest tests/routers/test_auth_router.py::TestAuthRouter::test_register -q