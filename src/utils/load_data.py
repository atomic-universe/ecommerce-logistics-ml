from connect_mysql import Connect_MySQL
import os

# import mysql connectivity credentials 
from credentials  import database_connection_credentials as connectivity_info

# tables = ['customers','geolocation','order_items','order_payments','order_reviews','orders','product_category_name_translation','products','sellers'] 
tables = ['customers','geolocation','order_items','order_payments','order_reviews','orders','product_category_name_translation','products','sellers','leads_closed','leads_qualified'] 

conn = None

try:
    username = connectivity_info['username']
    password = connectivity_info['password']
    host = connectivity_info['host']
    db = connectivity_info['db']    

    # create a object of connection to mysql server.
    conn = Connect_MySQL(username=username, password=password,host=host,db=db)
    print("Connection SUccessfull")


   
except Exception as e:
    print("Failed to connect to server.")
    print(e)




try: 
    path =  os.path.join('data','raw')
    if not os.path.exists(path):
        os.makedirs(path)

    dataframes = conn.fetch_tables_to_dfs(table_names=tables)
    print("Data retrive successful.")
    

    for table in tables:
        
        dataframes[table].to_csv(f"./data/raw/{table}.csv",index=False)
        print(f'{table} saved successfully.')


    del conn

except OSError as e:
    print("Check the save path exist or not.")

except Exception as e :
    print(f"Failed to load data. {e}")