from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

# Return the whole schedule
@app.route("/showtimes", methods=['GET'])
def get_schedule():
   res = make_response(jsonify(schedule), 200)
   return res

# Return the show corresponding to the showtdate mentioned in the path
@app.route("/showmovies/<date>", methods=['GET'])
def get_movies_bydate(date):
   for show in schedule : 
      if show["date"] == str(date):
         res = make_response(jsonify(show), 200)
         return res
   return make_response(jsonify({"error": "showdate not found"}), 400)
         
if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
