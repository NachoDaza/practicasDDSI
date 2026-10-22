import os
import pyodbc

conn = pyodbc.connect(
    "DRIVER={OracleODBC};"
    "DBQ=//oracle0.ugr.es:1521/practbd;"
    f"UID={os.environ['ORACLE_USER']};PWD={os.environ['ORACLE_PASS']}",
    autocommit=False,
)
cur = conn.cursor()
cur.execute("select 'conexion ok' from dual")
print(cur.fetchone()[0])
conn.close()
