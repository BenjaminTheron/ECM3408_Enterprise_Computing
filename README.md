# ECM3408_Spreadsheet_MVP

## Introduction
The intention of this project is to create a minimum viable product for a spreadsheet program using flask,
to handle requests and data processing.

## Prerequisites and Installation
The python standard library was extended to include the requests module and the flask module, both of which
can be installed with the commands below:
    - python3 -m pip install flask
    - python3 -m pip install requests

Additionally, this the specification for this CA was rigid with the fact that Python 3.6.8 must be used,
so in order for the project to work as intended you must be running this version of Python.

## Project Tutorial
No sophisticated file structures were used, so after installing the project simply navigate to the main folder
(cd to ../sc/) and do the following to run the program:

    - Enter a virtual environment by entering the following commands:

        - rm -rf venv
        - python3 -m venv venv
        -source venv/bin/activate

        - This removes the old virtual environment in the project directory and enters a new one.

    - Download the required modules in the virtual environment:

        - python3 -m pip install flask
        - python3 -m pip install requests

    - Execute the either one of the commands below (the only difference is the type of database used):

        - python3 main.py -r sqlite
        - python3 main.py -r firebase (This requires setting up and exporting a Firebase API Key)

        - The firebase command specifies that a cloud based database is to be used, with the sqlite flag
        specifying that a locally stored Sqlite3 database is to be used. For simiplicity sake and ease
        of repeatability use the sqlite database, unless you already have a firebase account and wish
        to see how the data is being stored graphically.


## Testing
3 Additional testing programs were created to test the create, read and list functionality of the program.
Additionally a test file with 10 practice tests were provided, before submission, the program passed all 10
of these tests when using both the sqlite and firebase databases.

### Notes
All functionality that was required by the specification was provided; however, there are a number of ways
in which the algorithms can be extended:

  - Handle more error codes and situations, instead of having single errors that were thrown for a variety of issues.
  - Further validation of the cells and formulae.
  - Further testing scripts.

## Details

#### Authors
Benjamin Theron

#### License
MIT License
