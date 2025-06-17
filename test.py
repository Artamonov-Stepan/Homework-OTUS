import subprocess
from datetime import datetime


def parse_ps_output():
    output = subprocess.check_output(['ps', 'aux'], text=True)
    lines = output.strip().splitlines()[1:]

    data = {'users': [], 'procs': {}, 'mem_total': 0, 'cpu_total': 0, 'max_mem_proc': '', 'max_cpu_proc': ''}

    for line in lines:
        fields = line.split()
        user = fields[0]
        mem = float(fields[3])
        cpu = float(fields[2])
        proc_name = fields[-1][:20]

        data['users'].append(user)
        data['procs'][user] = data['procs'].get(user, 0) + 1
        data['mem_total'] += mem
        data['cpu_total'] += cpu

        if mem > data.get('max_mem', 0):
            data['max_mem_proc'] = (proc_name, mem)

        if cpu > data.get('max_cpu', 0):
            data['max_cpu_proc'] = (proc_name, cpu)

    return data

def generate_report(data):
    now = datetime.now().strftime('%d-%m-%Y_%H:%M')
    filename = f'/tmp/system_scan_{now}.txt'

    with open(filename, 'w') as f:
        f.write(f"Отчет о состоянии системы ({now})\n\n")
        f.write(f"Пользователи системы: {', '.join(set(data['users']))}\n")
        f.write(f"Количество процессов: {sum(data['procs'].values())}\n\n")
        f.write("Пользовательские процессы:\n")
        for user, count in data['procs'].items():
            f.write(f"{user}: {count}\n")
        f.write("\n")
        f.write(f"Всего памяти используется: {data['mem_total']} %\n")
        f.write(f"Всего CPU используется: {data['cpu_total']} %\n")
        f.write(f"Максимально потребляющий память процесс: {data['max_mem_proc'][0]} ({data['max_mem_proc'][1]}%)\n")
        f.write(f"Максимально загружающий CPU процесс: {data['max_cpu_proc'][0]} ({data['max_cpu_proc'][1]}%)\n")

    print(f"Отчет успешно сохранен в файле: {filename}")

if __name__ == '__main__':
    data = parse_ps_output()
    generate_report(data)