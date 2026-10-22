import os
import pyodbc

def iniciar_conexion():
    cadena = (
        "DRIVER={OracleODBC};"
        "DBQ=//oracle0.ugr.es:1521/practbd;"
        f"UID={os.environ['ORACLE_USER']};PWD={os.environ['ORACLE_PASS']}"
    )
    return pyodbc.connect(cadena, autocommit=False)


def visualizar_menu():
    print("\n=========== MENU PRINCIPAL ===========")
    print("\n1. Borrar tablas/Crear tablas/Insertar 10 tuplas.")
    print("\n2. Dar de alta nuevo pedido.")
    print("\n3. Mostrar contenido de las tablas.")
    print("\n4. Salir del programa y cerrar conexion.")
    return input("\nOpcion: ").strip()

def alta_pedido(conn):
    try:
        cursor = conn.cursor()
        # Solicitar datos del pedido al usuario
        id_pedido = input("Ingrese el ID del pedido: ")
        id_cliente = input("Ingrese el ID del cliente: ")
        fecha_pedido = input("Ingrese la fecha del pedido (YYYY-MM-DD): ")

        # Insertar el nuevo pedido en la base de datos
        cursor.execute(
            "INSERT INTO Pedido (Cpedido, Ccliente, Fecha_pedido) "
            "VALUES (?, ?, TO_DATE(?, 'YYYY-MM-DD'))",
            (id_pedido, id_cliente, fecha_pedido)
        )
        conn.commit()
        print("Pedido agregado exitosamente.")

        print("\n=========== MENU DAR DE ALTA NUEVO PEDIDO ===========")
        print("\n1. Aniadir detalle de producto.")
        print("\n2. Eliminar todos los detalles de producto.")
        print("\n3. Cancelar pedido.")
        print("\n4. Finalizar pedido.")
        opcion = input("\nOpcion: ").strip()

        if opcion == "1":
            id_producto = input("Ingrese el ID del producto: ")
            cantidad = int(input("Ingrese la cantidad: "))

            # Comprobar que hay stock antes de insertar


            # Insertar el nuevo detalles de pedido en la base de datos
            cursor.execute(
                "INSERT INTO Detalle_Pedido (Cpedido, Cproducto, Cantidad) "
                "VALUES (?, ?, ?)",
                (id_pedido, id_producto, cantidad)
            )

        elif opcion == "2":
            # Eliminar todos los detalles de un pedido
            cursor.execute("DELETE FROM Detalle_Pedido WHERE Cpedido = ?", (id_pedido,))
            conn.commit()
            print("Todos los detalles del pedido han sido eliminados.")
        elif opcion == "3":
            cursor.execute("DELETE FROM Detalle_Pedido WHERE Cpedido = ?", (id_pedido,))
            cursor.execute("DELETE FROM Pedido WHERE Cpedido = ?", (id_pedido,))
            conn.commit()
            print("Pedido cancelado.")
        elif opcion == "4":
            # Hacer cambios permanentes.
            print("Pedido finalizado.")
        else:
            print("Opcion invalida. Volviendo al menu principal.")

    finally:
        print("Cerrando cursor de alta_pedido.")


def gestion_tablas(cursor):

    borrar_tablas(cursor)
    crear_tablas(cursor)
    introducir_tuplas(cursor)
           
   
def borrar_tablas(cursor):
    try:
        cursor.execute("DROP TABLE Detalle_Pedido")    
    except pyodbc.DatabaseError:
        print("No se pudo borrar la tabla o no existe.\n")

    try:
        cursor.execute("DROP TABLE Pedido")    
    except pyodbc.DatabaseError:
        print("No se pudo borrar la tabla o no existe.\n")

    try:
        cursor.execute("DROP TABLE Stock")    
    except pyodbc.DatabaseError:
        print("No se pudo borrar la tabla o no existe.\n") 

def crear_tablas(cursor):

    try:
        cursor.execute("""
            CREATE TABLE Stock (
                Cproducto NUMBER PRIMARY KEY,
                Cantidad NUMBER
            )
        """)
    except pyodbc.DatabaseError:
        print("La tabla Stock ya existe o no se pudo crear.\n")

    try:
        cursor.execute("""
            CREATE TABLE Pedido (
                Cpedido NUMBER PRIMARY KEY,
                Ccliente NUMBER,
                Fecha_pedido DATE
            )
        """)
    except pyodbc.DatabaseError:
        print("La tabla Pedido ya existe o no se pudo crear.\n")

    try:
        cursor.execute("""
            CREATE TABLE Detalle_Pedido (
                Cpedido NUMBER,
                Cproducto NUMBER,
                Cantidad NUMBER,
                PRIMARY KEY (Cpedido, Cproducto),
                FOREIGN KEY (Cpedido) REFERENCES Pedido(Cpedido),
                FOREIGN KEY (Cproducto) REFERENCES Stock(Cproducto)
            )
        """)
    except pyodbc.DatabaseError:
        print("La tabla Detalle_Pedido ya existe o no se pudo crear.\n")

def introducir_tuplas(cursor):
    try:
        for i in range(1, 11):
            cursor.execute("INSERT INTO Stock (Cproducto, Cantidad) VALUES (?, ?)", (i, 100))
        print("Se han insertado 10 tuplas en la tabla Stock.")
    except pyodbc.DatabaseError:
        print("No se pudieron insertar las tuplas en la tabla Stock.\n")

def mostrar_tablas(cursor):
    try:
        cursor.execute("SELECT * FROM Stock")
        rows = cursor.fetchall()
        print("\n=================== TABLA STOCK ===================")
        print(f"{'Cproducto':<12} | {'Cantidad':<10}")
        print("-" * 27)
        if rows:
            for row in rows:
                print(f"{row[0]:<12} | {row[1]:<10}")
        else:
            print("La tabla está vacía.")
    except pyodbc.DatabaseError:
        print("No se pudo mostrar la tabla Stock.\n")

    try:
        cursor.execute("SELECT * FROM Pedido")
        rows = cursor.fetchall()
        print("\n=================== TABLA PEDIDO ===================")
        print(f"{'Cpedido':<10} | {'Ccliente':<10} | {'Fecha_pedido':<12}")
        print("-" * 40)
        if rows:
            for row in rows:
                fecha = str(row[2])[:10] if row[2] else ""
                print(f"{row[0]:<10} | {row[1]:<10} | {fecha:<12}")
        else:
            print("La tabla está vacía.")
    except pyodbc.DatabaseError:
        print("No se pudo mostrar la tabla Pedido.\n")

    try:
        cursor.execute("SELECT * FROM Detalle_Pedido")
        rows = cursor.fetchall()
        print("\n=============== TABLA DETALLE_PEDIDO ===============")
        print(f"{'Cpedido':<10} | {'Cproducto':<12} | {'Cantidad':<10}")
        print("-" * 38)
        if rows:
            for row in rows:
                print(f"{row[0]:<10} | {row[1]:<12} | {row[2]:<10}")
        else:
            print("La tabla está vacía.")
    except pyodbc.DatabaseError:
        print("No se pudo mostrar la tabla Detalle_Pedido.\n")

    
def main():
    conn = iniciar_conexion()
    cursor = conn.cursor()
    try:
        while True:
            opcion = visualizar_menu()
            if opcion == "1":
                print("Borrado de tablas / Creacion de tablas / Insercion 10 tuplas")
                gestion_tablas(cursor)
            elif opcion == "2":
                alta_pedido(conn)
            elif opcion == "3":
                print("Informacion de las tablas")
                mostrar_tablas(cursor)
            elif opcion == "4":
                break
            else:
                print("Error. Opcion invalida.")
    finally:
        cursor.close()
        conn.close()
        print("Fin de la conexion.")


if __name__ == "__main__":
    main()
