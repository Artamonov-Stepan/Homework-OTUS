import os
import re
import json
import gzip
import tarfile
from collections import defaultdict
from typing import Dict, List, Tuple, Union
import argparse


def extract_log_file(archive_path: str, extract_to: str = None) -> str:
    if not extract_to:
        extract_to = os.path.dirname(archive_path)

    if archive_path.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(path=extract_to)
            # Ищем первый файл с логами в архиве
            for member in tar.getmembers():
                if 'access.log' in member.name:
                    return os.path.join(extract_to, member.name)
    elif archive_path.endswith('.gz'):
        log_path = os.path.join(extract_to, os.path.basename(archive_path)[:-3])
        with gzip.open(archive_path, 'rb') as f_in:
            with open(log_path, 'wb') as f_out:
                f_out.write(f_in.read())
        return log_path

    return None


def parse_log_line(line: str) -> Union[Dict[str, str], None]:
    pattern = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)" (\d+)$'
    match = re.match(pattern, line)
    if not match:
        return None

    ip, date, request, status, bytes_sent, referer, user_agent, duration = match.groups()

    method = request.split()[0] if request else '-'
    url = request.split()[1] if len(request.split()) > 1 else '-'

    return {
        'ip': ip,
        'date': f'[{date}]',
        'method': method,
        'url': url,
        'status': status,
        'bytes_sent': bytes_sent,
        'referer': referer,
        'user_agent': user_agent,
        'duration': int(duration)
    }


def analyze_log_file(file_path: str) -> Dict:
    total_requests = 0
    method_counts = defaultdict(int)
    ip_counts = defaultdict(int)
    longest_requests = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            total_requests += 1
            parsed = parse_log_line(line.strip())
            if not parsed:
                continue

            method_counts[parsed['method']] += 1

            ip_counts[parsed['ip']] += 1

            if len(longest_requests) < 3:
                longest_requests.append(parsed)
                longest_requests.sort(key=lambda x: x['duration'], reverse=True)
            elif parsed['duration'] > longest_requests[-1]['duration']:
                longest_requests[-1] = parsed
                longest_requests.sort(key=lambda x: x['duration'], reverse=True)

    top_ips = dict(sorted(ip_counts.items(), key=lambda item: item[1], reverse=True)[:3])

    formatted_longest = []
    for req in longest_requests:
        formatted_longest.append({
            'ip': req['ip'],
            'date': req['date'],
            'method': req['method'],
            'url': req['url'],
            'duration': req['duration']
        })

    return {
        'total_requests': total_requests,
        'total_stat': dict(method_counts),
        'top_ips': top_ips,
        'top_longest': formatted_longest
    }


def save_statistics(output_path: str, stats: Dict, input_filename: str) -> str:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(
        output_path,
        f"{os.path.splitext(os.path.basename(input_filename))[0]}_stats.json"
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return output_file


def print_statistics(stats: Dict) -> None:
    print(json.dumps(stats, indent=2, ensure_ascii=False))


def process_logs(input_path: str, output_dir: str = None) -> None:
    if input_path.endswith(('.tar.gz', '.gz')):
        extracted_file = extract_log_file(input_path)
        if not extracted_file:
            print(f"Не удалось распаковать архив или найти access.log в {input_path}")
            return
        input_path = extracted_file


    if not os.path.isfile(input_path):
        print(f"Файл не найден: {input_path}")
        return

    print(f"\nАнализирую файл: {input_path}")
    stats = analyze_log_file(input_path)
    print_statistics(stats)

    if output_dir:
        saved_file = save_statistics(output_dir, stats, input_path)
        print(f"Статистика сохранена в: {saved_file}")


def main():
    parser = argparse.ArgumentParser(description='Анализатор access.log файлов')
    parser.add_argument('input', help='Путь к лог-файлу, архиву (.tar.gz, .gz) или директории с логами')
    parser.add_argument('-o', '--output', help='Директория для сохранения JSON с результатами')
    args = parser.parse_args()

    process_logs(args.input, args.output)


if __name__ == "__main__":
    main()