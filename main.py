from flask import Flask, request, jsonify
import requests
import formulae_solver
import cells
import re
import sys
import sqlite3
import os

app = Flask(__name__)

@app.route("/cells/<string:id>", methods=["PUT"])
def create_cells(id):
    """
    This part of the  microservice takes a JSON object that has an id
    and formula property and creates a cell in the spreadsheet according
    to their values. 
    """
    data = request.get_json()
    if id != data.get("id"):
        # Returns a 400 code if the id in the request doesn't match the id made by the request
        return "",400
    else:
        id = data.get("id")
    formula = data.get("formula")

    if id != None and formula != None:
        # Check if the cell id already exists (updating a cell or creating a new cell)
        cell_list = cells.list()
        if cell_list != None:
            if id in cell_list:
                try:
                    cells.create(id, formula)
                    # 204 code is returned if a cell is being updated
                    return "",204
                except:
                    # 500 internal server error is returned if there is any problem updating the cell
                    return "", 500
            else:
                try:
                    cells.create(id, formula)
                    # 201 code and the location of the new cell is returned if a cell is being created
                    return "",201,{"Location":"/cells/"}
                except:
                    # 500 Internal server error is returned if there is any problem creating the cell
                    return "", 500
        else:
            return "",500 # Internal server error if there is a problem listing the cells
    else:
        # Returns a 400 code if the request is bad
        return "",400


@app.route("/cells/<string:id>", methods=["GET"])
def read_cells(id):
    """
    This part of the microservice finds a cell with a given ID and formula
    property and allows for it to be read and for its value to be calculated.
    """
    cell = cells.read(id)
    if cell != None:
        # The cell is returned as a dictionary entry containing a id and
        # formula value
        id = cell['id']
        formula = cell['formula']

        # Calculate the value represented by the formula - using WOLFRAMALHPA
        # Creates a clone of the formula and replaces any found instances of
        # cell ids with their formula recursively
        new_formula = formula
        swap_made = True
        list_of_cells = cells.list()
        list_digits = ["0","1","2","3","4","5","6","7","8","9", " "]
        list_operators = ["(",")","-","+","*","/", " "]


        # Loop through each known element and substitute its value into the formula
        # This is recursively done until there are no more elements in the equation
        while swap_made == True:
            swap_made = False
            for elem in list_of_cells:
                val = re.search(elem, formula)
                if val:
                    swap = True
                    # Find the formula of the cell we seek to replace
                    nested_cell = cells.read(elem)
                    formula = re.sub(elem,"(" + nested_cell["formula"] + ")", formula)

        # Do one final scan through to uncover any uncreated cells in the equation
        # These get evaluated to 0
        new_formula = formula
        # Use a copy of the formula to allow the formula to be iterated through
        for character in range(0, len(formula)):
            if formula[character] not in list_digits and formula[character] not in list_operators:
                start_pointer = character
                end_pointer = character
                while formula[end_pointer] not in list_operators and end_pointer > len(formula) - 1:
                    end_pointer += 1
                
                # Substitute the invalid cell in the formula with 0
                new_formula = re.sub(formula[start_pointer:end_pointer:], "0", formula)

        # Give the new formula to the formulae solver
        # Solve the formula by sending it to wolframalpha
        result = formulae_solver.formula_solver(new_formula)
        if result != None:
            data = {"id":id,"formula":result}
            # Returns a 200 code if the cell is correctly 
            # found and the value of its formula is calculated
            return data, 200 # Returns a JSON object with an id and
                                                   # formula property, along with a 200 OK
                                                   # code if the result of the formula is correctly found
        else:
            # Returns a 500 Internal server error for any reason that wolfram alpha is unable to return a result
            return "",500
    else:
        # Returns a 404 code if the cell cannot be found
        return "",404


@app.route("/cells/<string:id>",methods=["DELETE"])
def delete_cells(id):
    """
    This part of the microservice finds a cell with a given ID and deletes
    it from the spreadsheet.
    """
    delete = cells.delete(id)
    if delete == 200:
        # Returns a 204 successful no content code if the cell is successfully
        # found and deleted
        return "",204
    elif delete == 404:
        # Returns a 404 if the cell cannot be found and therefore cannot be deleted
        return "",404
    elif delete == 500:
        # Returns a 500 error for any reason that the cell is unable to be deleted
        return "",500


@app.route("/cells",methods=["GET"])
def list_cells():
    """ Lists the IDs of all cells in the spreadsheet """
    list_cells = cells.list()
    if list_cells != None and type(list_cells) != str:
        # Can't return a list with flask so need to jsonify the response
        return jsonify(list_cells),200
    elif list_cells != None and type(list_cells) == str:
        return list_cells
    else:
        # Returns a 500 code for any reason that causes an unsuccessful listing of
        # the cells
        return "",500


if __name__ == "__main__":
    # Gets the value of the Firebase API key and the wolframalpha API key
    # If the Wolframalpha API key is not set a default value is provided
    FBASE_KEY = os.getenv("FBASE")

    if os.getenv("FORMULA_KEY") == None:
        formulae_solver.KEY = "UAH32K-2YUK982954"

    # Reads the provided compiler flag to determine whether or not a sqlite or
    # firebase database is to be used
    # This should always be the second index of the array of arguments
    if len(sys.argv) < 3:
        print("ERROR: MISSING REQUIRED FLAGS")
    else:
        if sys.argv[2] == 'sqlite':
            # If there already exists a database with the same name as is about to be
            # created it is deleted so there are no pre-existing conflicts within the database
            os.remove('database.db')
            cells.set_database('sqlite', 'database.db')
    
            # Sets the name of the database to be used
            db = "database.db"
            # Creates the table for the database if it does not exist already
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS cells" +
                    "(cellid TEXT PRIMARY KEY, formula TEXT)"
                )
                connection.commit()
            app.run(host="localhost", port=3000)

        elif sys.argv[2] == 'firebase':
            cells.set_database('firebase', FBASE_KEY)        
            # Clear the database so that there are no preexisting conflicts
            cell_list = cells.list()
            for cell in cell_list:
                success = cells.delete(cell)
                if success is False:
                    print("ERROR: THE FIREBASE DB HAS NOT BEEN CLEARED")
                
            app.run(host="localhost", port=3000)
        else:
            print("ERROR: Database not provided, please specify the database type to be used")
