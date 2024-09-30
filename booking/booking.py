from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
import sys

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

# Return all the bookings' information 
@app.route("/bookings", methods=['GET'])
def get_json():
   res = make_response(jsonify(bookings), 200)
   return res

@app.route("/bookings/<userid>", methods=['GET', 'POST'])
def handle_booking_for_user(userid):
   if request.method == 'GET': # get booking for user
      user_bookings = []
      for booking in bookings:
         if str(booking["userid"]) == str(userid):
            user_bookings.append(booking)
      if user_bookings != []:
         res = make_response(jsonify(user_bookings),200)
         return res
      else:
         return make_response(jsonify({"error":"No booking found for this user ID"}),400)
   
   if request.method == 'POST': # add booking by user
      req = request.get_json() # movie to book (date, movieid)
      print(req)
      if movie_exists(req["movies"], req["date"]): # if the movie is valid 
         for booking in bookings:
            if str(booking["userid"]) == str(userid):
               for booked_movies in booking["dates"]:
                  if booked_movies["date"] == req["date"]:
                     for movie in booked_movies["movies"]: # check if movie is already booked by this user
                        if movie == req["movies"]:
                           return make_response(jsonify({"error":"movie is already booked"}),409)
                     booked_movies["movies"].append(req["movies"])
                     res = make_response(jsonify(booking),200)
                     return res
               nouvelle_date = {
                  "date": req["date"],
                  "movies": req["movies"]
                  }
               booking["dates"].append(nouvelle_date)
               res = make_response(jsonify(booking), 200)
      else:
         return make_response(jsonify({"error":"this movie is not scheduled at this date"}),400)
            



def movie_exists(movieid, date):
   '''checks if the movie exists at this date,
   returns a boolean'''
   address = 'http://192.168.1.52:3201/showmovies?' + date
   schedule = requests.get(address) # get the schedule for this date 
   for movie in schedule.movies:
      if movie == movieid:
         return True
   return False



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
