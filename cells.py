""" Stores the ID and formula contained in all spreadsheet cells """
import sqlite3
import requests

cells = {}
database = {}

def set_database(db, db_name):
    """
    A setter method to set the type of database to be used by the microservice 
    """
    database["type"] = db
    database["name"] = db_name
    database["url"] = "https://" + db_name + "-default-rtdb.europe-west1.firebasedatabase.app"

def create(id, formula):
    """ Stores each cell in a map containing the id and formula in the cell """
    cells[id] = {"id" : id, "formula" : formula}
    exists = False
    if database["type"] == 'sqlite':
        # Executes a SQL command to determine whether or not 
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM cells"
            )
            rows = cursor.fetchall()
            exists = False
            for row in rows:
                if id == row[0]:
                    exists = True
                    
        if exists:
            # If the cell already exists a SQL UPDATE command is executed
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE cells SET formula=? WHERE cellid=?", (formula,id)
                )
                connection.commit()
        else:
            # If the cell doesn't already exist a SQL INSERT command is executed
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO cells(cellid, formula) VALUES (?,?)",(id,formula)
                )
                connection.commit()

    elif database["type"] == "firebase":
        # Determines if the create call is to update a cell or create a new one
        # This is done by sending a GET request and examining the returned code
        response1 = requests.get(database["url"] + '/cells/'+id+'.json')
        if response1.status_code == 404:
            # Sends a POST request to the Firebase DB to create a new resource
            response2 = requests.post(database["url"]+'/cells/'+id+'.json',json={"id":id,"formula":formula})
        elif response1.status_code == 200:
            # Sends a PUT request to the Firebase DB to update a new resource
            response2 = requests.put(database["url"]+'/cells/'+id+'.json',json={"id":id,"formula":formula})
        else:
            # If any other code is returned throw an error
            print("ERROR - UNVALIDATED CODE RETURNED")

def read(id):
    """
    Reads a cells with a specified ID and allows its values to be
    calculated
    """
    if database["type"] == "sqlite":
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT cellid, formula FROM cells WHERE cellid=?",
                (id,)
            )
            row = cursor.fetchone()
            if row:
                return {"id":row[0],"formula":row[1]}
            else:
                return None

    elif database["type"] == "firebase":
        response = requests.get(database["url"] + '/cells/'+id+'.json')
        # Extract the formula and ID from the returned JSON object
        if response.status_code == 200:
            data = response.json()
            return {"id":data["id"],"formula":data["formula"]}
        else:
            return None

def delete(id):
    """ Deletes a cell with a given id """
    if database["type"] == "sqlite":
        # Find the cell to delete
        # If it exists, delete it, otherwise return False
        try:
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT cellid, formula FROM cells WHERE cellid=?",
                    (id,)
                )
                row = cursor.fetcone()
                if row:
                    cursor.execute(
                        "DELETE FROM cells WHERE cellid=?",
                        (id,)
                    )
                    return 200
                else:
                    return 404
        except:
            return 500

    elif database["type"] == "firebase":
        try:
            # First find the cell to delete then delete it
            response1 = requests.get(database["url"] + '/cells/'+id+'.json')
            # If a 200 code is returned then the cell exists
            if response1.status_code == 200:
                # Issues a DELETE request to the desired cell
                response2 = requests.delete(database["url"] + '/cells/'+id+'.json')
                # An empty json object is returned to inidicate the cell has
                # been deleted successfully
                if response2.json() == None:
                    return 200
                else:
                    return 500
            else:
                return 404
        except:
            return 500

def list():
    """ Lists all cells stored by the spreadsheet """
    cell_list = []
    if database["type"] == "sqlite":
        try:
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM cells"
                )
                rows = cursor.fetchall()
                for row in rows:
                    cell_list.append(str(row[0]))

                if len(cell_list) == 0:
                    return "[]"
                else:
                    return cell_list
        except:
            return None

    elif database["type"] == "firebase":
        # List all the cells in the spreadsheet
        response = requests.get(database["url"]+'/cells.json')
        # If the initial GET request returns a valid JSON object
        # Extract all the cell IDs from it
        if response.status_code == 200 and response.json() != None:
            data = response.json()
            for item in data:
                cell = data.get(item)
                cell_list.append(cell["id"])
            
            return cell_list
        elif response.status_code == 200 and response.json() == None:
            return "[]"
        else:
            # If a Non 200 code is returned, throw an internal server error
            return None
            
