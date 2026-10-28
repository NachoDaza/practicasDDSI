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

    cursor = None

    try:
        cursor = conn.cursor()
        # Solicitar datos del pedido al usuario
        id_pedido = input("\nIngrese el ID del pedido: ")
        id_cliente = input("\nIngrese el ID del cliente: ")
        fecha_pedido = input("\nIngrese la fecha del pedido (YYYY-MM-DD): ")

        # Insertar el nuevo pedido en la base de datos
        try:
            cursor.execute(
                "INSERT INTO Pedido (Cpedido, Ccliente, Fecha_pedido) "
                "VALUES (?, ?, TO_DATE(?, 'YYYY-MM-DD'))",
                (id_pedido, id_cliente, fecha_pedido)
            )
            conn.commit()
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\nPedido agregado exitosamente.")

            cursor.execute("SAVEPOINT pedido_vacio_creado")
        except pyodbc.DatabaseError:
            conn.rollback()
            print("\nError en la creacion del pedido. Abortando operacion.")
            return

        while True:
            print("\n=========== MENU DAR DE ALTA NUEVO PEDIDO ===========")
            print("\n1. Aniadir detalle de producto.")
            print("\n2. Eliminar todos los detalles de producto.")
            print("\n3. Cancelar pedido.")
            print("\n4. Finalizar pedido.")
            opcion = input("\nOpcion: ").strip()

            if opcion == "1":
                id_producto = int(input("Ingrese el ID del producto: "))
                cantidad = int(input("Ingrese la cantidad: "))

                # Comprobar que hay stock antes de insertar

                stock_cantidad = cursor.execute("SELECT Cantidad FROM Stock WHERE Cproducto = ?", (id_producto,)).fetchval()

                if stock_cantidad != None and cantidad > 0 and cantidad <= stock_cantidad:

                    # Insertar el nuevo detalles de pedido en la base de datos
                    try:
                        cursor.execute(
                        "INSERT INTO Detalle_Pedido (Cpedido, Cproducto, Cantidad) "
                        "VALUES (?, ?, ?)",
                        (id_pedido, id_producto, cantidad)
                        )
                        cursor.execute(
                            "UPDATE Stock SET Cantidad = ? WHERE Cproducto = ?", (stock_cantidad - cantidad, id_producto)
                        )
                        conn.commit()
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("\nDetalle de producto agregado exitosamente.")
                    # Ocurre una excepción.
                    except pyodbc.DatabaseError:
                        conn.rollback()
                        print("\nError en el anadido de producto.")

                # Error en la cantidad o el stock.
                else:
                    if cantidad <= 0:
                        print("\nPor favor, inserte una cantidad positiva.")
                    else:
                        if stock_cantidad == None:
                            print("\nEl producto no existe.")
                        else:
                            print("\nNo hay stock suficiente del producto.")

            elif opcion == "2":
                # Eliminar todos los detalles de un pedido
                try:
                    cursor.execute("DELETE FROM Detalle_Pedido WHERE Cpedido = ?", (id_pedido,))
                    conn.commit()
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\nTodos los detalles del pedido han sido eliminados.")
                except pyodbc.DatabaseError:
                    conn.rollback()
                    print("\nError en la eliminacion.")

            elif opcion == "3":

                try:  
                    cursor.execute("ROLLBACK TO pedido_vacio_creado")
                    
                    cursor.execute("DELETE FROM Detalle_Pedido WHERE Cpedido = ?", (id_pedido,))
                    cursor.execute("DELETE FROM Pedido WHERE Cpedido = ?", (id_pedido,))
                    conn.commit()
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\nPedido cancelado.")
                    return
                except pyodbc.DatabaseError:
                    conn.rollback()
                    print("\nError en la cancelacion.")

            elif opcion == "4":
                # Hacer cambios permanentes.
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\nPedido finalizado.")
                return

            else:
                print("\nOpcion invalida.")


    finally:

        if cursor != None:
            cursor.close()
            print("\nCerrando cursor de alta_pedido.")


def gestion_tablas(conn):
    cursor = conn.cursor()

    borrar_tablas(cursor)
    crear_tablas(cursor)
    introducir_tuplas(conn)
           
   
def borrar_tablas(cursor):
    try:
        cursor.execute("DROP TABLE Detalle_Pedido")    
    except pyodbc.DatabaseError:
        print("\nNo se pudo borrar la tabla o no existe.")

    try:
        cursor.execute("DROP TABLE Pedido")    
    except pyodbc.DatabaseError:
        print("\nNo se pudo borrar la tabla o no existe.")

    try:
        cursor.execute("DROP TABLE Stock")    
    except pyodbc.DatabaseError:
        print("\nNo se pudo borrar la tabla o no existe.") 

def crear_tablas(cursor):

    try:
        cursor.execute("""
            CREATE TABLE Stock (
                Cproducto NUMBER PRIMARY KEY,
                Cantidad NUMBER
            )
        """)
    except pyodbc.DatabaseError:
        print("\nLa tabla Stock ya existe o no se pudo crear.")

    try:
        cursor.execute("""
            CREATE TABLE Pedido (
                Cpedido NUMBER PRIMARY KEY,
                Ccliente NUMBER,
                Fecha_pedido DATE
            )
        """)
    except pyodbc.DatabaseError:
        print("\nLa tabla Pedido ya existe o no se pudo crear.")

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
        print("\nLa tabla Detalle_Pedido ya existe o no se pudo crear.")

def introducir_tuplas(conn):
    cursor = conn.cursor()
    try:
        for i in range(1, 11):
            cursor.execute("INSERT INTO Stock (Cproducto, Cantidad) VALUES (?, ?)", (i, 100))
        print("\nSe han insertado 10 tuplas en la tabla Stock.")
        conn.commit()
    except pyodbc.DatabaseError:
        conn.rollback()
        print("\nNo se pudieron insertar las tuplas en la tabla Stock.")

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
            print("\nLa tabla está vacía.")
    except pyodbc.DatabaseError:
        print("\nNo se pudo mostrar la tabla Stock.")

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
            print("\nLa tabla está vacía.")
    except pyodbc.DatabaseError:
        print("\nNo se pudo mostrar la tabla Pedido.")

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
            print("\nLa tabla está vacía.")
    except pyodbc.DatabaseError:
        print("\nNo se pudo mostrar la tabla Detalle_Pedido.")

    
def main():
    conn = iniciar_conexion()
    cursor = conn.cursor()
    try:
        while True:
            opcion = visualizar_menu()
            if opcion == "1":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\nBorrado de tablas / Creacion de tablas / Insercion 10 tuplas")
                gestion_tablas(conn)
            elif opcion == "2":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\nDar de alta nuevo pedido")
                alta_pedido(conn)
            elif opcion == "3":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\nInformacion de las tablas")
                mostrar_tablas(cursor)
            elif opcion == "4":
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                print("\nOpcion invalida.")
    finally:
        cursor.close()
        conn.close()
        print("\nFin de la conexion.")


if __name__ == "__main__":
    main()
