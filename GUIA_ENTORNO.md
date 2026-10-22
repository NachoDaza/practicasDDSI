# Guía de entorno: Python + Oracle (Seminario 1 DDSI)

Cómo dejar listo el entorno para conectar desde Python con el servidor Oracle de la ETSIIT. Pensado para **Ubuntu 22.04** (nativo o en WSL).

> ## ⚡ CADA VEZ QUE ABRAS UNA TERMINAL NUEVA
>
> La instalación de esta guía se hace **una sola vez**. Pero cada vez que abras una terminal (o reinicies el ordenador) tienes que repetir **estos 3 pasos** antes de ejecutar el programa:
>
> ```bash
> # 1. Entra en la carpeta del repositorio (usa la ruta de tu equipo)
> cd /mnt/c/Users/TU_USUARIO_WINDOWS/Desktop/DDSI/practicasDDSI
>
> # 2. Activa el entorno virtual
> source ~/.venvs/seminario1/bin/activate
>
> # 3. Carga tus credenciales del fichero .env
> set -a; source .env; set +a
> ```
>
> **Y además:**
> - Activa la **VPN de la UGR** (o conéctate a Eduroam). Sin ella no hay conexión con Oracle.
> - Sabrás que el entorno está activo porque verás `(seminario1)` al principio de la línea.
> - Comprueba que las credenciales están cargadas con `echo $ORACLE_USER` (debe imprimir tu usuario).

## Datos de la conexión

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

El entorno se crea **fuera del repositorio**. Si el repo está en el disco de Windows (`/mnt/c/...` en WSL), crearlo dentro es muy lento y parece que se cuelga.

```bash
python3 -m venv ~/.venvs/seminario1
source ~/.venvs/seminario1/bin/activate
```

Verás `(seminario1)` al principio de la línea de la terminal.

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

Debe decir `succeeded`. Si da *timed out* o *refused*, no sigas: el problema es la VPN o la red.

## 6. Descargar e instalar Oracle Instant Client

1. En la web de Oracle, en la página de descargas de **Instant Client para Linux x86-64**, descarga dos ZIP de la **misma versión**:
   - **Basic Package**
   - **ODBC Package**
2. Descomprímelos en `/opt/oracle`. La ruta de Descargas depende de tu sistema. En WSL suele ser `/mnt/c/Users/TU_USUARIO_WINDOWS/Downloads`.

```bash
sudo apt install -y unzip libaio1
sudo mkdir -p /opt/oracle
cd /mnt/c/Users/TU_USUARIO_WINDOWS/Downloads
sudo unzip 'instantclient-basic*.zip' -d /opt/oracle
sudo unzip 'instantclient-odbc*.zip' -d /opt/oracle
ls /opt/oracle
```

Debe aparecer **una sola** carpeta `instantclient_XX_XX`. No la muevas ni la borres después, porque el driver se registra apuntando a ella.

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

El último comando **no debe imprimir nada**. Después, registra el driver en unixODBC:

```bash
DRIVER_LIB=$(ls $IC/libsqora.so.* | head -n 1)
sudo tee -a /etc/odbcinst.ini <<EOF

[OracleODBC]
Description=Oracle ODBC driver
Driver=$DRIVER_LIB
EOF
```

Comprueba que Python lo ve (con el entorno activo):

```bash
odbcinst -q -d
python -c "import pyodbc; print(pyodbc.drivers())"
```

Debe salir `['OracleODBC']`.

## 8. Credenciales (nunca se suben a GitHub)

Cada persona usa **su propio usuario y contraseña** de Oracle. Se guardan en un fichero `.env` que está en el `.gitignore`.

```bash
nano .env
```

Contenido (con tus datos; si la contraseña tiene caracteres especiales, entre comillas simples):

```
ORACLE_USER=tu_usuario
ORACLE_PASS='tu_contraseña'
```

Comprueba que Git lo ignora (`.env` **no** debe aparecer en la lista):

```bash
git status
```

## 9. Prueba de conexión

Carga las variables en la terminal y ejecuta el script de prueba del repositorio:

```bash
set -a; source .env; set +a
python test_conexion.py
```

Debe imprimir `conexion ok`. El script es:

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

## Cada vez que abras una terminal nueva

Repite los 3 pasos del recuadro **⚡ del principio de esta guía** (entrar en el repo, activar el entorno y cargar el `.env`) y activa la VPN.

## Problemas frecuentes

| Síntoma | Causa probable y solución |
|---|---|
| `python3 -m venv` se queda colgado | El repo está en `/mnt/c` (WSL). Crea el entorno en `~/.venvs`, como en el paso 3 |
| `Can't open lib 'OracleODBC'` | Driver mal registrado o ruta incorrecta en `/etc/odbcinst.ini`. Repite el paso 7 |
| `libaio.so.1: cannot open shared object file` | Falta `libaio1`: `sudo apt install -y libaio1` |
| `ORA-01017` | Usuario o contraseña incorrectos |
| Tarda y da *timeout* al conectar | VPN o Eduroam sin activar, o WSL sin salida a la VPN |
| Error de conexión con la contraseña correcta | Si contiene `;` o `}` rompe la cadena de conexión: cámbiala por otra |
| Hay sesiones colgadas y no deja conectar | Límite de 3 o 4 conexiones: usa `select * from mis_sesiones;` y `execute mata_sesion(sid, serial);` en SQL Developer |
