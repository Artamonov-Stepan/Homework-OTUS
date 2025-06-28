import pytest
from faker import Faker

fake = Faker('ru_RU')


@pytest.fixture
def random_customer():
    return {
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'email': fake.unique.email(),
        'password': fake.password(length=12),
        'telephone': fake.phone_number()
    }


def test_create_customer(db, random_customer):
    """Тест создания клиента"""
    customer_id = db.create_customer(random_customer)
    assert customer_id > 0
    customer = db.get_customer(customer_id)
    assert customer['email'] == random_customer['email']


def test_update_customer(db, random_customer):
    """Тест обновления клиента"""
    # Создаем клиента
    customer_id = db.create_customer(random_customer)

    # Новые данные
    update_data = {
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'email': fake.unique.email(),
        'telephone': fake.phone_number()
    }

    # Обновляем
    assert db.update_customer(customer_id, update_data)
    updated = db.get_customer(customer_id)
    assert updated['email'] == update_data['email']


def test_delete_customer(db, random_customer):
    """Тест удаления клиента"""
    customer_id = db.create_customer(random_customer)
    assert db.delete_customer(customer_id)
    assert db.get_customer(customer_id) is None


@pytest.mark.negative
def test_update_nonexistent_customer(db):
    """Негативный тест обновления"""
    with pytest.raises(ValueError, match="не найден"):
        db.update_customer(999999, {
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test@example.com',
            'telephone': '+79160000000'
        })

@pytest.mark.negative
def test_delete_nonexistent_customer(db):
    """Негативный тест удаления"""
    with pytest.raises(ValueError, match="не найден"):
        db.delete_customer(999999)