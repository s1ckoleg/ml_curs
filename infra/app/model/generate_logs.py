import random
from datetime import datetime, timedelta


def generate_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


def generate_time():
    current_time = datetime.now()
    time_offset = timedelta(minutes=random.randint(0, 1440))  # Random time within a day
    random_time = current_time - time_offset
    return random_time.strftime("%d/%b/%Y:%H:%M:%S +0000")


def generate_request():
    methods = ['GET', 'POST', 'DELETE', 'PUT']
    endpoints = ['/index.html', '/about', '/contact', '/api/data']
    return f'"{random.choice(methods)} {random.choice(endpoints)} HTTP/1.1"'


def generate_response_code(error_rate):
    if random.random() < error_rate:
        return random.choice([400, 401, 403, 404, 500, 502, 503, 504])
    else:
        return random.choice([200, 201, 202, 204])


def generate_log_line(error_rate):
    ip = generate_ip()
    timestamp = generate_time()
    request = generate_request()
    response_code = generate_response_code(error_rate)
    bytes_sent = random.randint(200, 2000)

    return f'{ip} - - [{timestamp}] {request} {response_code} {bytes_sent}'


def generate_logs(num_entries, error_rate):
    return [generate_log_line(error_rate) for _ in range(num_entries)]


num_entries = 1000
error_percentage = 0.5

logs = generate_logs(num_entries, error_percentage)
for log in logs:
    print(log)

with open('./logs/eval_logs.log', 'w') as file:
    file.write("\n".join(logs))