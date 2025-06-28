import random
from datetime import datetime, timedelta


def generate_access_log(filename: str, num_entries: int = 100):
    methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
    resources = ["/", "/index.html", "/login", "/api/data", "/images/logo.png"]
    user_agents = [
        "Mozilla/5.0",
        "Chrome/120.0.0.0",
        "curl/7.68.0"
    ]
    ips = ["192.168.1.{}".format(i) for i in range(1, 20)]

    with open(filename, 'w') as f:
        for _ in range(num_entries):
            ip = random.choice(ips)
            method = random.choice(methods)
            resource = random.choice(resources)
            status = random.choice([200, 200, 200, 404, 500, 301])
            bytes_sent = random.randint(100, 5000)
            referer = "-"
            user_agent = random.choice(user_agents)
            duration = random.randint(1, 5000)

            # Генерируем случайную дату в последних 7 днях
            log_time = datetime.now() - timedelta(days=random.randint(0, 7))
            time_str = log_time.strftime('[%d/%b/%Y:%H:%M:%S +0000]')

            line = f'{ip} - - {time_str} "{method} {resource} HTTP/1.1" {status} {bytes_sent} "{referer}" "{user_agent}" {duration}\n'
            f.write(line)

    print(f"Файл {filename} успешно создан с {num_entries} записями")


if __name__ == "__main__":
    generate_access_log("access.log", 50)  # Создаст файл с 50 записями