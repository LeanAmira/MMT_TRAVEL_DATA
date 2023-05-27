from flask import Flask, request, jsonify
import sqlite3
import os
import pandas as pd
import json

app = Flask(__name__)

tables = ['MMT_Bus', 'MMT_Flights', 'MMT_Reza', 'MMT_Trains']  # Noms de table correspondants aux fichiers Excel

def import_excel_files_to_database(folder_path, table_name):

    # Get the list of each excel file in the actual folder
    excel_files = [file for file in os.listdir(folder_path) if file.endswith('.xlsx')]

    # Etablish a connection to the DB
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    # Run each excel file and import datas to the DB
    for i, file in enumerate(excel_files):
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)
        table_name = tables[i]
        df.to_sql(table_name, conn, if_exists='append', index=False)

    # Close the connection to the DB
    conn.close()

def export_database_to_sql(file_path):

    # Etablish a connection to the DB
    conn = sqlite3.connect('base.db')

    # Export the database to a SQL file
    with open(os.path.join(os.getcwd(), file_path), 'w') as file:
        for line in conn.iterdump():
            file.write('%s\n' % line)

    # Close the connection to the DB
    conn.close()

def treatment_to_json_object():

    import_excel_files_to_database(os.getcwd(), tables)

    # Etablish a connection to the DB
    conn = sqlite3.connect('base.db')

    data = []

    pnr = input("Please enter your PNR : ")
    mmt_reza_number = input("Please enter your reservation number : ")

    # Run each table and print their content
    for table in tables:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT * FROM {table} WHERE PNR = '{pnr}' AND MMT_Rez_Num = '{mmt_reza_number}' ;")
        rows = cursor.fetchall()

        # Create a list of dictionnries for table actual datas
        table_rows = []
        for row in rows:
            d = dict(zip([column[0] for column in cursor.description], row))
            table_rows.append(d)

        # Add table datas to the main list
        data.append({table: table_rows})

    conn.close()

    json_data = json.dumps(data, indent=1)
    print(json_data)


if __name__ == '__main__':

    treatment_to_json_object()
    export_database_to_sql(file_path="DB.sql")
    app.run()