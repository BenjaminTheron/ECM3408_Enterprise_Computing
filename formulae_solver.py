import os
import requests

#KEY = os.environ["FORMULA_KEY"]
KEY = None

if KEY == None:
    KEY = "UAH32K-2YUK982954"

URI = "https://api.wolframalpha.com/v1/result"

def formula_solver(formula):
    """
    Provides wolframalpha with a complete formula and returns the response
    """
    parameters = {"appid":KEY, "i":formula}
    request = requests.get(URI,params=parameters)
    if request.status_code == 200:
        return request.text
    else:
        return None
