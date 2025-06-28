import socket
from http import HTTPStatus


def validate_status_code(status_code):
    """Проверяет, является ли статус-код допустимым"""
    try:
        status_code = int(status_code)
        if status_code in HTTPStatus:
            return status_code, f"{status_code} {HTTPStatus(status_code).phrase}"
        return 200, "200 OK"
    except (ValueError, TypeError):
        return 200, "200 OK"


def validate_http_method(method):
    """Проверяет допустимость HTTP-метода"""
    valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'}
    return method if method in valid_methods else 'GET'


def validate_headers(headers):
    """Очищает и проверяет заголовки"""
    valid_headers = {}
    for key, value in headers.items():
        if isinstance(key, str) and isinstance(value, str):
            # Удаляем потенциально опасные символы
            clean_key = ''.join(c for c in key if c.isalnum() or c in '-_')
            clean_value = ''.join(c for c in value if c.isprintable() and c not in '\r\n')
            valid_headers[clean_key] = clean_value
    return valid_headers


def handle_request(client_socket, client_address):
    try:
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            return

        lines = [line.strip() for line in data.split('\r\n') if line.strip()]
        if not lines:
            return

        # Валидация request line
        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            return

        method = validate_http_method(parts[0])
        path = parts[1]

        # Парсинг и валидация статуса
        status_code, status_phrase = 200, "200 OK"
        if '?' in path:
            path, query = path.split('?', 1)
            params = query.split('&')
            for param in params:
                if param.startswith('status='):
                    status_code, status_phrase = validate_status_code(param.split('=')[1])

        # Валидация заголовков
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        headers = validate_headers(headers)

        # Формирование ответа
        response_lines = [
            f"Request Method: {method}",
            f"Request Source: {client_address}",
            f"Response Status: {status_phrase}",
        ]

        for key, value in headers.items():
            response_lines.append(f"{key}: {value}")

        response_body = '\r\n'.join(response_lines)

        response = (
            f"HTTP/1.1 {status_phrase}\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            f"{response_body}"
        )

        client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        error_response = (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 0\r\n"
            "\r\n"
        )
        client_socket.sendall(error_response.encode('utf-8'))
        print(f"Error handling request: {e}")

    finally:
        client_socket.close()


def run_server(host='127.0.0.1', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server started on {host}:{port}")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                handle_request(client_socket, client_address)
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")


if __name__ == '__main__':
    run_server()