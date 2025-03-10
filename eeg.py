# -*- coding: utf-8 -*-
"""EEG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1q-xWxPtRhOHPAUtb45rHMjTObvneWMHl
"""

from google.colab import drive
drive.mount('/content/drive')
import pandas as pd
file_path = '/content/drive/MyDrive/DEAP Dataset/features_raw.csv'
df = pd.read_csv(file_path)
print(df.head())
print(df.info())
data = df.drop(columns=['Unnamed: 32'])
print(data.columns)                           #empty column 32 removed
print(data.isnull().sum().sum()) #as output is zero no missing values

from sklearn.preprocessing import MinMaxScaler, StandardScaler
# scaler = MinMaxScaler()
scaler = StandardScaler()
normalized_data=scaler.fit_transform(data)
normalized_df = pd.DataFrame(normalized_data, columns=data.columns)
print(normalized_df.head())
print("Minimum value:", normalized_df.min().min())
print("Maximum value:", normalized_df.max().max())

import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(normalized_df['Fp1'][:200], label='Fp1')
plt.plot(normalized_df['AF3'][:200], label='AF3')
plt.plot(normalized_df['F3'][:200], label='F3')
plt.plot(normalized_df['F7'][:200], label='F7')
plt.legend()
plt.title('EEG Signal Visualiztion')
plt.xlabel('Time Points')
plt.ylabel('Normalized Values')
plt.show()
print(normalized_df.describe())

import seaborn as sns
plt.figure(figsize=(14, 10))
sns.heatmap(normalized_df.corr(), cmap='coolwarm', annot=False)
plt.title('Correlation Matrix of EEG Channels')
plt.show()

from sklearn.decomposition import PCA
pca = PCA(n_components=10)
pca_result = pca.fit_transform(normalized_df)
print(pca_result.shape)
print("Explained variance ratio", pca.explained_variance_ratio_)
print(normalized_df.columns)

from sklearn.cluster import KMeans
#kmeans = KMeans(n_clusters=10, random_state=42)
#pseudo_labels = kmeans.fit_predict(normalized_df)
#df['Cluster'] = pseudo_labels
#print(df.head())

from sklearn.metrics import silhouette_score
#clustering again
kmeans = KMeans(n_clusters=3, random_state=42)
pseudo_labels = kmeans.fit_predict(normalized_df)
df['Cluster'] = pseudo_labels
print(df.head())
score=silhouette_score(normalized_df, pseudo_labels)
print("clusters: {score}")
centroids=pd.DataFrame(kmeans.cluster_centers_, columns=normalized_df.columns)
print("cluster Centroids:\n", centroids)
cluster_sizes = df['Cluster'].value_counts()
print("Cluster sizes:\n", cluster_sizes)
pcacluster = PCA(n_components=2, random_state=42)
reduced_data = pcacluster.fit_transform(normalized_df)
visual_df = pd.DataFrame(reduced_data, columns=['PC1', 'PC2'])
visual_df['Cluster'] = df['Cluster']
plt.figure(figsize=(12,8))
sns.scatterplot(x='PC1', y='PC2', hue='Cluster', data=visual_df, palette='viridis')
plt.title('PCA Visualization of Clusters')
plt.show()
imp_features = centroids.std(axis=0).sort_values(ascending=False)
print("Important Features:\n", imp_features.head(10))

top_features = ['FC1', 'F8', 'C3', 'P4', 'O1', 'P8', 'T7', 'AF3', 'FC6', 'CP2']
data_reduced = normalized_df[top_features]
print(data_reduced.head())
pca_let=PCA(n_components=2)
reduced_data_let = pca_let.fit_transform(data_reduced)
plt.figure(figsize=(12, 8))
sns.scatterplot(x=reduced_data_let[:, 0], y=reduced_data_let[:, 1], c=df['Cluster'], cmap='viridis', s=10)
plt.title('PCA Visualization of Clusters')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.show()

kmeans_reduced=KMeans(n_clusters=3, random_state=42)
pseudo_labels_reduced = kmeans_reduced.fit_predict(data_reduced)
df['Cluster_Reduced'] = pseudo_labels_reduced
print(df.head())
silhouette_avg_reduced = silhouette_score(data_reduced, pseudo_labels_reduced)
print(f"Silhouette score for reduced data: {silhouette_avg_reduced}")

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
X_train, X_test, y_train, y_test = train_test_split(data_reduced, df['Cluster_Reduced'], test_size=0.2, random_state=42)
clf=RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print("classification report with reduced features:\n", classification_report(y_test, y_pred))

from sklearn.model_selection import cross_val_score
scores = cross_val_score(clf, data_reduced, df['Cluster_Reduced'], cv=5)
print("Cross-validation scores:", scores)
print("Mean accuracy:", scores.mean())

from sklearn.metrics import confusion_matrix
import seaborn as sns
cm=confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',xticklabels=['Class 0', 'Class 1', 'class 2'],yticklabels=['Class 0', 'Class 1', 'Class 2'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.show()

from scipy.stats import zscore
z_scores = data.apply(zscore)
outliers = (z_scores > 3).sum(axis=0)
print("outliers of each column:", outliers,"\n")

import numpy as np

Q1 = normalized_df.quantile(0.25)
Q3 = normalized_df.quantile(0.75)
IQR = Q3 - Q1

outliers = ((normalized_df < (Q1 - 1.5 * IQR)) | (normalized_df > (Q3 + 1.5 * IQR)))

cleaned_df = normalized_df[~outliers.any(axis=1)]
print(f"Original dataset size: {normalized_df.shape[0]}")
print(f"Cleaned dataset size: {cleaned_df.shape[0]}")

from google.colab import drive
drive.mount('/content/drive')
import zipfile
zip_path="/content/drive/MyDrive/data_preprocessed_python.zip"
extract_path = "/content/eeg_data_folder"
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

import os
import pickle
data_folder = "/content/eeg_data_folder/data_preprocessed_python"
dat_files = [f for f in os.listdir(data_folder) if f.endswith('.dat')]
for file_name in dat_files:
  file_path = os.path.join(data_folder, file_name)
  with open(file_path, 'rb') as file:
    data = pickle.load(file, encoding='latin1')
    print(f"Contents of {file_name}:")
    print(data)
    print("-"*50)
file_path = 's13.dat'  # Path to the file
if os.path.exists(file_path):
    with open(file_path, 'rb') as file:
        sample_data = pickle.load(file, encoding='latin1')
    print(sample_data['labels'].shape)
    print(sample_data['data'].shape)
else:
    print(f"The file {file_path} does not exist.")

# Check the structure of a sample file
sample_file = eeg_data['s13.dat']
print(sample_file.keys())  # Display the keys ('labels' and 'data')
print(sample_file['labels'].shape)
print(sample_file['data'].shape)