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


def main():
    conn = iniciar_conexion()
    try:
        while True:
            opcion = visualizar_menu()
            if opcion == "1":
                print("Borrado de tablas / Creacion de tablas / Insercion 10 tuplas")
            elif opcion == "2":
                print("Dar de alta un nuevo medido")
            elif opcion == "3":
                print("Informacion de las tablas")
            elif opcion == "4":
                break
            else:
                print("Error. Opcion invalida.")
    finally:
        conn.close()
        print("Fin de la conexion.")


if __name__ == "__main__":
    main()
