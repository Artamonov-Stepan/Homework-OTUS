import pytest
import pymysql
from opencart_db import OpenCartDB  # Импортируем наш класс

def pytest_addoption(parser):
    parser.addoption("--host", default="127.0.0.1")
    parser.addoption("--port", type=int, default=3306)
    parser.addoption("--db", default="bitnami_opencart")
    parser.addoption("--user", default="bn_opencart")
    parser.addoption("--password", default="")

@pytest.fixture(scope="session")
def db_connection(request):
    """Фикстура создает соединение с БД"""
    try:
        return pymysql.connect(
            host=request.config.getoption("--host"),
            port=request.config.getoption("--port"),
            user=request.config.getoption("--user"),
            password=request.config.getoption("--password"),
            database=request.config.getoption("--db"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
    except pymysql.Error as e:
        pytest.skip(f"Не удалось подключиться к БД: {e}")

@pytest.fixture(scope="session")
def db(db_connection):
    """Фикстура создает экземпляр OpenCartDB"""
    if db_connection is None:
        pytest.skip("Нет подключения к БД")
    return OpenCartDB(db_connection)