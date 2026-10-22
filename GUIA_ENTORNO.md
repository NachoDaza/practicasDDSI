# Guía de entorno: Python + Oracle (Seminario 1 DDSI)

Cómo dejar listo el entorno para conectar desde Python con el servidor Oracle de la ETSIIT. Pensado para **Ubuntu 22.04** (nativo o en WSL).

> ## CADA VEZ QUE ABRO UNA TERMINAL NUEVA
>
> Repetir **estos 5 pasos** antes de ejecutar el programa:
>
> ```bash
> # 1. Entrar en la carpeta del repositorio 
> cd /mnt/c/Users/ignac/Desktop/DDSI/practicasDDSI
>
> # 2. Activar el entorno virtual
> source ~/.venvs/seminario1/bin/activate
>
> # 3. Cargar credenciales del fichero .env
> set -a; source .env; set +a
>
> # 4. Activar VPN / Eduroam para conectar Oracle.
>
> # 5. Comprobar entorno (seminario1) y credenciales cargadas echo $ORACLE_USER
> ```

## DATOS CONEXIÓN

- Lenguaje: Python 3
- Conexión: ODBC con `pyodbc` + Oracle Instant Client
- Servidor: `oracle0.ugr.es`, puerto `1521`, servicio `practbd`
- Hace falta estar en la **VPN de la UGR** o en Eduroam

## 1. Entrar en el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta_del_repositorio>
```

## 2. Paquetes del sistema

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unixodbc unixodbc-dev odbcinst
```

## 3. Entorno virtual

El entorno se crea **fuera del repositorio**. 
```bash
python3 -m venv ~/.venvs/seminario1
source ~/.venvs/seminario1/bin/activate
```

## 4. Instalar las dependencias

Con el entorno activo, desde la carpeta del repo:
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -c "import pyodbc; print(pyodbc.version)"
```

Si falla al compilar `pyodbc`:
```bash
sudo apt install -y build-essential python3-dev
pip install -r requirements.txt
```

## 5. Comprobar que hay red hasta el servidor

Con la VPN activa (en WSL, la VPN de Windows):
```bash
sudo apt install -y netcat-openbsd
nc -zv -w 5 oracle0.ugr.es 1521
```

## 6. Descargar e instalar Oracle Instant Client

1. En la web de Oracle, en la página de descargas de **Instant Client para Linux x86-64**, descargaR dos ZIP de la **misma versión**:
   - **Basic Package**
   - **ODBC Package**
2. Descomprimir en `/opt/oracle`. En mi caso es `/mnt/c/Users/ignac/Downloads`.
```bash
sudo apt install -y unzip libaio1
sudo mkdir -p /opt/oracle
cd /mnt/c/Users/ignac/Downloads
sudo unzip 'instantclient-basic*.zip' -d /opt/oracle
sudo unzip 'instantclient-odbc*.zip' -d /opt/oracle
ls /opt/oracle
```

## 7. Registrar el driver ODBC
```bash
IC=$(ls -d /opt/oracle/instantclient_*)
echo $IC
```

Que Ubuntu encuentre las librerías de Oracle:
```bash
echo $IC | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf
sudo ldconfig
ldd $IC/libsqora.so.* | grep "not found"
```

Registrar el driver en unixODBC:
```bash
DRIVER_LIB=$(ls $IC/libsqora.so.* | head -n 1)
sudo tee -a /etc/odbcinst.ini <<EOF

[OracleODBC]
Description=Oracle ODBC driver
Driver=$DRIVER_LIB
EOF
```

Comprobar que Python lo ve (con el entorno activo):
```bash
odbcinst -q -d
python -c "import pyodbc; print(pyodbc.drivers())"
```

Debe salir `['OracleODBC']`.

## 8. Credenciales 

Cada uno su propio user y password de Oracle. Se guardan en un fichero `.env` que está en el `.gitignore`.
```bash
nano .env
```

Contenido:
```
ORACLE_USER=tu_usuario
ORACLE_PASS='tu_contraseña'
```

Comprobar que Git lo ignora:
```bash
git status
```

## 9. Prueba de conexión

```bash
set -a; source .env; set +a
python test_conexion.py
```

```python
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
```

Hecho por IGNACIO J. DAZA ROMERO.
(*) Script de python realizado con ayuda de GenAI siguiendo esquema mostrado por el profesor en diapositivas (crusor, conn).
(*) Cómo registrar el driver  ODBC en unix: https://www.ibm.com/docs/es/db2/11.5.x?topic=environment-setting-up-odbc-linux-unix
(*) Creación de entornos virtuales: https://docs.python.org/es/3.8/library/venv.html
(*) Descargar e instalar Oracle Instant Client: https://www.oracle.com/es/database/technologies/instant-client/linux-x86-64-downloads.html
