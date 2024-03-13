import pandas as pd
# loading data
customers_ = pd.read_csv("sources/olist_customers_dataset.csv")
geolocation_ = pd.read_csv("sources/olist_geolocation_dataset.csv")
order_items_ = pd.read_csv("sources/olist_order_items_dataset.csv")
order_payments_ = pd.read_csv("sources/olist_order_payments_dataset.csv")
order_reviews_ = pd.read_csv("sources/olist_order_reviews_dataset.csv")
orders_ = pd.read_csv("sources/olist_orders_dataset.csv")
products_ = pd.read_csv("sources/olist_products_dataset.csv")
sellers_ = pd.read_csv("sources/olist_sellers_dataset.csv")
product_category_name_ = pd.read_csv("sources/product_category_name_translation.csv")

## displaying data shape
dataset = {
    'customers_': customers_,
    'geolocation_': geolocation_,
    'order_items_': order_items_,
    'order_payments_': order_payments_,
    'order_reviews_': order_reviews_,
    'orders_': orders_,
    'products_': products_,
    'sellers_': sellers_,
    'product_category_name_': product_category_name_,
}

"""
for x, y in dataset.items():
    print(f'{x}shape :       ', (list(y.shape)))
"""

import numpy as np
# generate a  DataFrame characteristics summary
def info_data(data):
    info_data = pd.DataFrame({
        'feature': data.columns.values,  # Column names
        'data_type': data.dtypes.values,  # Data types of columns
        'null_value(%)': data.isna().mean().values * 100,  # Percentage of missing values
        'neg_value(%)': [len(data[col][data[col] < 0]) / len(data) * 100 if col in data.select_dtypes(include=[np.number]).columns else 0 for col in data.columns],  # Percentage of negative values for numeric columns
        '0_value(%)': [len(data[col][data[col] == 0]) / len(data) * 100 if col in data.select_dtypes(include=[np.number]).columns else 0 for col in data.columns],  # Percentage of zero values for numeric columns
        'duplicate': data.duplicated().sum(),  # Number of duplicated rows
        'n_unique': data.nunique().values,  # Number of unique values for each column
        'n_totale': data.shape[0]  # Total number of values for each column
    })

    # Round the values in the summary DataFrame to 3 decimal places
    return info_data.round(2)

info_data(order_reviews_)
order_reviews_.head()

"""
for x, y in dataset.items():
    print(f'{x}', f'{list(y.columns)}\n')
"""