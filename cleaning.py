from main import *
import re
import missingno as msno
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


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
"""
msno.matrix(df, figsize=(20, 6))
plt.show()"""

df['customercity'] = df['customer_city'].str.title()
df['payment_type'] = df['payment_type'].str.replace('', ' ').str.title()

# cleaning up name columns
df['customer_city'] = df['customer_city'].str.title()
df['payment_type'] = df['payment_type'].str.replace('_', ' ').str.title()
# engineering new/essential columns
df['delivery_against_estimated'] = (df['order_estimated_delivery_date'] - df['order_delivered_customer_date']).dt.days
df['order_purchase_year'] = df.order_purchase_timestamp.apply(lambda x: x.year)
df['order_purchase_month'] = df.order_purchase_timestamp.apply(lambda x: x.month)
df['order_purchase_dayofweek'] = df.order_purchase_timestamp.apply(lambda x: x.dayofweek)
df['order_purchase_hour'] = df.order_purchase_timestamp.apply(lambda x: x.hour)
df['order_purchase_day'] = df['order_purchase_dayofweek'].map({0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'})
df['order_purchase_mon'] = df.order_purchase_timestamp.apply(lambda x: x.month).map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
# Changing the month attribute for correct ordenation
df['month_year'] = df['order_purchase_month'].astype(str).apply(lambda x: '0' + x if len(x) == 1 else x)
df['month_year'] = df['order_purchase_year'].astype(str) + '-' + df['month_year'].astype(str)
#creating year month column
df['month_y'] = df['order_purchase_timestamp'].map(lambda date: 100*date.year + date.month)


df['month_year'] = df['order_purchase_month'].astype(str).apply(lambda x: '0' + x if len(x) == 1 else x)
df['month_year'] = df['order_purchase_year'].astype(str) + '-' + df['month_year'].astype(str)
#creating year month column
df['month_y'] = df['order_purchase_timestamp'].map(lambda date: 100*date.year + date.month)
rfm = df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (pd.to_datetime('2018-08-29 15:00:37') - pd.to_datetime(x.max())).days,
    'order_id': 'count',
    'payment_value': 'sum'
}).reset_index()

rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']
inertia = []
X = rfm.drop(columns=['customer_id'])
