import mysql.connector as MySql
from mysql.connector import Error as error_sql

#Esta es mi función para conectar a la base de datos,
# es decir, contiene la cadena de conexión
def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'admin',
        database = 'escuela')
    conexión_exitosa = cadena_de_conexión.is_connected()
    if conexión_exitosa:
      return cadena_de_conexión
  except error_sql as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

#Y este es para desconectar la base de datos
def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()