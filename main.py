import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


def parse_log_entry(log_entry):  # TODO: logstash
    parts = log_entry.split()
    ip_address = parts[0]
    timestamp = parts[3].strip('[]')
    request = parts[5].strip('"')
    response_code = int(parts[8])
    bytes_sent = int(parts[9])
    return ip_address, timestamp, request, response_code, bytes_sent


def process_logs(logs):
    data = []
    for log in logs:
        ip, time, request, response, bytes_sent = parse_log_entry(log)
        data.append({'ip': ip, 'response': response, 'bytes': bytes_sent})
    return pd.DataFrame(data)


with open('./logs/train_logs.log', 'r') as file:
    lines = file.readlines()
    logs = [line.strip() for line in lines]

df = process_logs(logs)
df['is_error'] = df['response'].apply(lambda x: 1 if x >= 400 else 0)
df['label'] = df['is_error']

X = df[['is_error', 'bytes']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=10)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

with open('./logs/eval_logs.log', 'r') as test_file:
    test_lines = test_file.readlines()
    new_logs = [line.strip() for line in test_lines]

new_log_df = process_logs(new_logs)
new_log_df['is_error'] = new_log_df['response'].apply(lambda x: 1 if x >= 400 else 0)

predictions = model.predict(new_log_df[['is_error', 'bytes']])
anomaly_count = sum(predictions)
total_count = len(predictions)
anomaly_fraction = anomaly_count / total_count
anomaly_threshold = 0.2

if anomaly_fraction > anomaly_threshold:
    print(f"Overall anomaly detected! {anomaly_fraction * 100:.1f}% of logs are anomalous.")
else:
    print(f"No overall anomaly detected. Only {anomaly_fraction * 100:.1f}% of logs are anomalous.")

# current train_logs.log contains 20% errors
# current eval_logs.log contains 50% errors
# code return "Overall anomaly detected! 48.7% of logs are anomalous."

# for log_entry, prediction in zip(new_logs, predictions):
#     print(f'Log entry: {log_entry} - Predicted anomaly' if prediction == 1 else f'Log entry: {log_entry} - No anomaly detected')
