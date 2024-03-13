from main import *
import re
import missingno as msno
import matplotlib.pyplot as plt

#GEOLOCATION TABLE
# Drop duplicates data
geolocation_= geolocation_.drop_duplicates()
# Filter invalid city names based on pattern of protugies lang
def filtered_city(data, col):
    pattern = re.compile("[^a-z\sA-Z0-9-\'+]")
    filtered_df = data[data[col].str.contains(pattern)]
    return filtered_df
# Searching for city names that do not follow a pattern
geolocation_: object= filtered_city(geolocation_, 'geolocation_city')
# function to replace non-standard special characters with standard characters in a string
def replace_char(city_name):
    city_name = re.sub(r'[ãââàáä]', 'a', city_name)
    city_name = re.sub(r'[íîì]', 'i', city_name)
    city_name = re.sub(r'[úûùü]', 'u', city_name)
    city_name = re.sub(r'[éêèë]', 'e', city_name)
    city_name = re.sub(r'[óõôòö]', 'o', city_name)
    city_name = re.sub(r'[ç]', 'c', city_name)
    return city_name
# Applying the function to clean 'geolocation_city' column
geolocation_['geolocation_city']= geolocation_['geolocation_city'].apply(replace_char)
# Check a sample zip code
geolocation_[geolocation_['geolocation_zip_code_prefix']==45936].head(15)
# Cleaning all geolocation city
for i in geolocation_['geolocation_zip_code_prefix'].unique():
    mode_city = geolocation_[geolocation_['geolocation_zip_code_prefix'] == i]['geolocation_city'].mode().values[0]
    geolocation_.loc[geolocation_['geolocation_zip_code_prefix'] == i, 'geolocation_city'] = mode_city
# Convert the city name column to title case
geolocation_['geolocation_city']= geolocation_['geolocation_city'].str.title()


#CUSTOMERS DATA
customers_=customers_.merge(geolocation_[['geolocation_zip_code_prefix', 'geolocation_city']].drop_duplicates(),
                        left_on='customer_zip_code_prefix',
                        right_on='geolocation_zip_code_prefix',
                        how='left')
# Fill missing values in geolocation_city with customer_city title-cased
customers_['geolocation_city'].fillna(customers_['customer_city'].str.title(),inplace=True)
# Update customer_city with geolocation_city value
customers_['customer_city'] = customers_['geolocation_city']
# Drop the unnecessary columns from the merged DataFrame
customers_ = customers_.drop(columns=['geolocation_zip_code_prefix', 'geolocation_city'])



#ORDER ITEM DATA
# Convert datetime datatype
order_items_['shipping_limit_date'] = pd.to_datetime(order_items_['shipping_limit_date'])

#ORDER PAIEMENT DATA
order_payments_ = order_payments_[order_payments_['payment_installments']!=0]
notdefined_0 = order_payments_[(order_payments_['payment_value']==0) & (order_payments_['payment_type']=='not_defined')]
order_payments_.drop(notdefined_0.index, inplace=True)
order_payments_['payment_type'] = order_payments_['payment_type'].str.replace('_', ' ').str.title()

#ORDER REVIEW DATA
order_reviews_.drop(columns=['review_comment_title', 'review_comment_message', 'review_answer_timestamp'], inplace=True)
order_reviews_['review_creation_date'] = pd.to_datetime(order_reviews_['review_creation_date'])

#ORDERS DATA
orders_.dropna(inplace=True)
orders_['order_status'] = orders_['order_status'].str.title()
orders_['order_purchase_timestamp'] = pd.to_datetime(orders_['order_purchase_timestamp'])
orders_['order_approved_at'] = pd.to_datetime(orders_['order_approved_at'])
orders_['order_delivered_carrier_date'] = pd.to_datetime(orders_['order_delivered_carrier_date'])
orders_['order_delivered_customer_date'] = pd.to_datetime(orders_['order_delivered_customer_date'])
orders_['order_estimated_delivery_date'] = pd.to_datetime(orders_['order_estimated_delivery_date'])

#PRODUCTS DATA
products_.dropna(inplace=True)
products_.drop(products_[products_['product_weight_g']==0].index, inplace=True)

#SELLERS DATA
sellers_= sellers_.merge(geolocation_[['geolocation_zip_code_prefix', 'geolocation_city']].drop_duplicates(),
                              left_on='seller_zip_code_prefix',
                              right_on='geolocation_zip_code_prefix',
                              how='left')
sellers_['geolocation_city'].fillna(sellers_['seller_city'].str.title(), inplace=True)
sellers_['seller_city'] = sellers_['geolocation_city']
sellers_.drop(columns=['geolocation_zip_code_prefix', 'geolocation_city'], inplace=True)

#PRODUCT CATEGORY NAME
product_category_name_['product_category_name_english'] = product_category_name_['product_category_name_english'].str.replace('_', ' ').str.title()

#FINAL DF
df = pd.merge(orders_, customers_, on='customer_id', how='left')
df = df.merge(order_items_, on='order_id', how='left')
df = df.merge(sellers_, on='seller_id', how='left')
df = df.merge(products_, on='product_id', how='left')
df = df.merge(product_category_name_, on='product_category_name', how='left')
df = df.merge(order_payments_, on='order_id', how='left')
df = df.merge(order_reviews_, on='order_id', how='left')
df.dropna(inplace=True)
df['product_category_name'] = df['product_category_name_english']
df.drop(columns='product_category_name_english', inplace=True)

#show
msno.matrix(df, figsize=(20, 6))
plt.show()