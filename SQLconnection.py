import mysql.connector

 # Connect to the MySQL server
try:
    conn = mysql.connector.connect(
        host="141.209.241.57",
        user="jerom1mr",
        password="TheWh33l!",
        database="BIS698M1530_GRP2"
    )
    cursor = conn.cursor()
except mysql.connector.Error as error:
    print(f"Error connecting to MySQL Server: {error}")
    exit(1)  # Exit if the initial connection fails

    