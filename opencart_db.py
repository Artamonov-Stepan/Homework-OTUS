import pymysql
from typing import Dict, Optional, Union


class OpenCartDB:
    def __init__(self, connection: pymysql.connections.Connection):
        """
        Инициализация подключения к БД OpenCart

        :param connection: Активное соединение pymysql
        """
        self.connection = connection

    def check_connection(self) -> bool:
        """
        Проверяет активность соединения с БД

        :return: True если соединение активно, False в противном случае
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except pymysql.Error:
            return False

    def customer_exists(self, customer_id: int) -> bool:
        """
        Проверяет существование клиента в БД

        :param customer_id: ID клиента для проверки
        :return: True если клиент существует, False если нет
        :raises RuntimeError: При ошибках выполнения запроса
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT customer_id FROM oc_customer WHERE customer_id = %s",
                    (customer_id,)
                )
                return cursor.fetchone() is not None
        except pymysql.Error as e:
            raise RuntimeError(f"Ошибка проверки существования клиента: {e}")

    def create_customer(self, customer_data: Dict) -> int:
        """
        Создает нового клиента в таблице oc_customer

        :param customer_data: Словарь с данными клиента
        :return: ID созданного клиента
        :raises ValueError: При отсутствии обязательных полей
        :raises RuntimeError: При ошибках выполнения запроса
        """
        required_fields = ['firstname', 'lastname', 'email', 'password']
        if not all(field in customer_data for field in required_fields):
            raise ValueError(f"Отсутствуют обязательные поля: {required_fields}")

        try:
            with self.connection.cursor() as cursor:
                sql = """
                INSERT INTO oc_customer (
                    customer_group_id, store_id, language_id,
                    firstname, lastname, email, telephone,
                    password, custom_field, newsletter,
                    ip, status, safe, token, code, date_added
                ) VALUES (
                    1, 0, 1, %s, %s, %s, %s,
                    %s, '', 0, '', 1, 0, '', '', NOW()
                )
                """
                cursor.execute(sql, (
                    customer_data['firstname'],
                    customer_data['lastname'],
                    customer_data['email'],
                    customer_data.get('telephone', ''),
                    customer_data['password']
                ))
                self.connection.commit()
                return cursor.lastrowid
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при создании клиента: {e}")

    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """
        Получает данные клиента по ID

        :param customer_id: ID клиента
        :return: Словарь с данными клиента или None если не найден
        :raises RuntimeError: При ошибках выполнения запроса
        """
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM oc_customer WHERE customer_id = %s",
                    (customer_id,)
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            raise RuntimeError(f"Ошибка при получении клиента: {e}")

    def update_customer(self, customer_id: int, update_data: Dict) -> bool:
        """
        Обновляет данные клиента

        :param customer_id: ID клиента
        :param update_data: Словарь с обновляемыми полями
        :return: True если обновление успешно
        :raises ValueError: Если клиент не существует или нет обязательных полей
        :raises RuntimeError: При ошибках выполнения запроса
        """
        if not self.customer_exists(customer_id):
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        required_fields = ['firstname', 'lastname', 'email', 'telephone']
        if not all(field in update_data for field in required_fields):
            raise ValueError(f"Отсутствуют обязательные поля: {required_fields}")

        try:
            with self.connection.cursor() as cursor:
                sql = """
                UPDATE oc_customer 
                SET firstname = %s, lastname = %s, email = %s, telephone = %s
                WHERE customer_id = %s
                """
                cursor.execute(sql, (
                    update_data['firstname'],
                    update_data['lastname'],
                    update_data['email'],
                    update_data['telephone'],
                    customer_id
                ))
                self.connection.commit()
                return cursor.rowcount > 0
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при обновлении клиента: {e}")

    def delete_customer(self, customer_id: int) -> bool:
        """
        Удаляет клиента из БД

        :param customer_id: ID клиента
        :return: True если удаление успешно
        :raises ValueError: Если клиент не существует
        :raises RuntimeError: При ошибках выполнения запроса
        """
        if not self.customer_exists(customer_id):
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        try:
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM oc_customer WHERE customer_id = %s"
                cursor.execute(sql, (customer_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при удалении клиента: {e}")