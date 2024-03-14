from cleaning import *

# 1. Calculez le montant total des frais de livraison pour chaque client
delivery_fees_per_customer = df.groupby('customer_unique_id')['freight_value'].sum()
sorted_customers=delivery_fees_per_customer.sort_values(ascending=False)
top_20 = sorted_customers.head(20)


#2.Affichez les catégories de produits les plus vendues
product_sales = df.groupby('product_category_name')['order_id'].count()
sorted_product_sales = product_sales.sort_values(ascending=False)
top_product_categories = sorted_product_sales.head(10)  # Par exemple, sélectionnez les 10 premières catégories