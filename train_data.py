import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Load the dataset
df = pd.read_csv('unique_urls.csv')

# Feature Engineering
df['url_length'] = df['url'].apply(lambda x: len(x))
df['num_dots'] = df['url'].apply(lambda x: x.count('.'))
df['num_slashes'] = df['url'].apply(lambda x: x.count('/'))
df['keyword_length'] = df['keyword'].apply(lambda x: len(x))
df['has_numbers'] = df['url'].str.contains(r'\d').astype(int)
df['has_special_chars'] = df['url'].str.contains(r'[^a-zA-Z0-9]').astype(int)

# Prepare features (X) and labels (y)
X = df[['url_length', 'num_dots', 'num_slashes', 'keyword_length', 'has_numbers', 'has_special_chars']]
y = df['keyword']  

# Encode the target variable (keywords)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)

# Save the trained model and label encoder
with open('trained_model.pkl', 'wb') as model_file:
    pickle.dump(rf, model_file)

with open('label_encoder.pkl', 'wb') as encoder_file:
    pickle.dump(label_encoder, encoder_file)

print("Model and label encoder saved as 'trained_model.pkl' and 'label_encoder.pkl'")
