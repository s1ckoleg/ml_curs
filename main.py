import pandas as pd
import numpy as np
import requests
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from geopy.geocoders import Nominatim  # Optional for geolocation (requires API or local DB)

IPINFO_TOKEN = 'b534c3e4cc0345'

def get_geolocation(ip):
    """Fetch geolocation data using IPinfo API."""
    url = f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url)
        data = response.json()
        country = data.get('country', 'UNKNOWN')
        city = data.get('city', 'UNKNOWN')
        print(f"Country: {country}, City: {city}")
        return country, city
    except Exception as e:
        return 'UNKNOWN', 'UNKNOWN'

def parse_nginx_logs_with_geo(log_file):
    logs = []
    with open(log_file) as f:
        for line in f:
            parts = line.split()
            ip = parts[0]
            country, city = get_geolocation(ip)
            logs.append({
                'ip': ip,
                'country': country,
                'city': city,
                'datetime': parts[3].strip('['),
                'method': parts[5].strip('"'),
                'url': parts[6],
                'status': int(parts[8]),
                'size': int(parts[9]) if parts[9].isdigit() else 0,
                'user_agent': ' '.join(parts[11:]).strip('"')
            })
    return pd.DataFrame(logs)

df = parse_nginx_logs_with_geo('./logs/train_logs.log')

df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%b/%Y:%H:%M:%S')
df['hour'] = df['datetime'].dt.hour  # Hour of request
df['request_rate'] = df.groupby('ip')['ip'].transform('count')  # Requests per IP


df['ip_encoded'] = LabelEncoder().fit_transform(df['ip'])
df['method_encoded'] = LabelEncoder().fit_transform(df['method'])
df['user_agent_encoded'] = LabelEncoder().fit_transform(df['user_agent'])
df['country_encoded'] = LabelEncoder().fit_transform(df['country'])
df['city_encoded'] = LabelEncoder().fit_transform(df['city'])

df['is_anomaly'] = np.where(
    (df['status'] >= 400) | 
    (df['request_rate'] > 100) | 
    (df['hour'] < 6) | 
    (df['size'] > 1_000_000) |
    (df['country'] == 'UNKNOWN'), 1, 0
)

X = df[['ip_encoded', 'method_encoded', 'size', 'request_rate', 'hour', 'user_agent_encoded', 'country_encoded', 'city_encoded']]
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
