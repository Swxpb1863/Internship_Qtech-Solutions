import pandas as pd
import numpy as np
import joblib
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

# Load saved model and scaler
kmeans = joblib.load("kmeans_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load the dataset for visualization
data = pd.read_csv("CustomerSegmentation_dataa.csv")
numerical_features = ['Age', 'Income', 'PurchaseFrequency', 'AverageOrderValue', 'TotalSpend', 'ChurnRisk']
data_scaled = scaler.transform(data[numerical_features])
data['Cluster'] = kmeans.predict(data_scaled)

# Reduce dimensions for visualization
pca = PCA(n_components=2)
data['PCA1'], data['PCA2'] = zip(*pca.fit_transform(data_scaled))

# Streamlit app
st.title("Customer Segmentation - K-Means Clustering")

cluster_labels = {0: 'Basic Customer', 1: 'Premium Customer', 2: 'Deluxe Customer'}
data['Customer Segment'] = data['Cluster'].map(cluster_labels)

# Input form for new customer data
st.write("### Add a New Customer")
new_customer = [
    st.number_input("Age", min_value=18, max_value=80, step=1),
    st.number_input("Income", min_value=20000, max_value=150000, step=1000),
    st.number_input("Purchase Frequency (per month)", min_value=1, max_value=12, step=1),
    st.number_input("Average Order Value", min_value=5, max_value=500, step=10),
    st.number_input("Total Spend", min_value=500, max_value=20000, step=100),
    st.number_input("Risk of customer leaving", min_value=0, max_value=100, step=1)
]

if st.button("Classify New Customer"):
    # Preprocess the new customer data
    new_customer_scaled = scaler.transform([new_customer])
    
    # Predict the cluster for new customer
    new_cluster = kmeans.predict(new_customer_scaled)[0]
    st.success(f"The new customer belongs to {cluster_labels[new_cluster]}")
    
    # Add new customer to the PCA plot
    new_customer_pca = pca.transform(new_customer_scaled)
    data_new = data.copy()
    new_row = pd.DataFrame({
        'PCA1': [new_customer_pca[0][0]],
        'PCA2': [new_customer_pca[0][1]],
        'Cluster': [new_cluster],
        'Customer Segment': [cluster_labels[new_cluster]],  # Make sure to assign the correct label
    })
    data_new = pd.concat([data_new, new_row], ignore_index=True)

    # Visualize updated clusters with the new customer
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x="PCA1", y="PCA2", hue="Customer Segment", data=data_new, palette="Set1", alpha=0.6
    )
    plt.scatter(
        new_customer_pca[0][0],
        new_customer_pca[0][1],
        color="red",
        label="New Customer",
        s=75,
        edgecolor="black",
    )
    plt.title("Customer Segmentation with New Customer")
    plt.legend()
    st.pyplot(plt.gcf())
