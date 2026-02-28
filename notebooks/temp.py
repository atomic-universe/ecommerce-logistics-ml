from src.utils.connect_mysql import Connect_MySQL

conn =  Connect_MySQL(username='root',password='vighnesh',host='localhost',db='ecommerce')
print("Connection SUccessl")

conn.fetch_tables_to_dfs(table_names=['customers'])