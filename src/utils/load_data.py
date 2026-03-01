from connect_mysql import Connect_MySQL


tables = ['customers','geolocation','order_items','order_payments','order_reviews','orders','product_category_name_translation','products','sellers'] 



conn = Connect_MySQL(username='root', password='vighnesh',host='localhost',db='ecommerce')
print("Connection SUccessfull")
dataframes = conn.fetch_tables_to_dfs(table_names=tables)

print("Data retrive successful.")


for table in tables:
    dataframes[table].to_csv(f"./data/raw/{table}.csv")
    print(f'{table} saved successfully.')

