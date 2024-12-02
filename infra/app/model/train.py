import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

from get_geolocation import get_geolocation

def parse_nginx_logs_with_geo(log_file):
    logs = []
    with open(log_file) as f:
        for line in f:
            parts = line.split()
            ip = parts[0]
            country, city = get_geolocation(ip)
            logs.append({
                'ip': ip,
                'method': parts[5].strip('"'),
                'url': parts[6],
                'status': int(parts[8]),
                'size': int(parts[9]) if parts[9].isdigit() else 0,
                'datetime': parts[3].strip('['),
                'country': country,
                'city': city,
            })
    return pd.DataFrame(logs)

df = parse_nginx_logs_with_geo('./logs/train_logs.log')

df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%b/%Y:%H:%M:%S')
df['hour'] = df['datetime'].dt.hour
df['request_rate'] = df.groupby('ip')['ip'].transform('count')

ip_encoder = LabelEncoder()
method_encoder = LabelEncoder()
country_encoder = LabelEncoder()
city_encoder = LabelEncoder()

df['ip_encoded'] = ip_encoder.fit_transform(df['ip'])
df['method_encoded'] = method_encoder.fit_transform(df['method'])
df['country_encoded'] = country_encoder.fit_transform(df['country'])
df['city_encoded'] = city_encoder.fit_transform(df['city'])

df['is_anomaly'] = np.where(
    (df['status'] >= 400) | 
    (df['request_rate'] > 100) | 
    (df['hour'] < 6) | 
    (df['size'] > 1_000_000) |
    (df['country'] == 'UNKNOWN'), 1, 0
)

X = df[['ip_encoded', 'method_encoded', 'size', 'request_rate', 'hour', 'country_encoded', 'city_encoded']]
y = df['is_anomaly']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

joblib.dump(clf, 'random_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(ip_encoder, 'ip_encoder.pkl')
joblib.dump(method_encoder, 'method_encoder.pkl')
joblib.dump(country_encoder, 'country_encoder.pkl')
joblib.dump(city_encoder, 'city_encoder.pkl')
