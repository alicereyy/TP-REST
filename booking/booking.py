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
   
# Bookings welcome page 
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

# Return all the bookings' information 
@app.route("/bookings", methods=['GET'])
def get_json():
   res = make_response(jsonify(bookings), 200)
   return res

# Return the booking by userid
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         res = make_response(jsonify(booking["dates"]),200)
         return res
   return make_response(jsonify({"error":"User ID not found"}),400)

def write(bookings):
    with open('{}/databases/booking.json'.format("."), 'w') as f:
        json.dump({"bookings": bookings}, f)

# Add a booking for a user 
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   new_booking = {"date": req["date"], "movies": req["movies"]}
   
   showtime_url = f"http://127.0.0.1:3202/showmovies/{new_booking['date']}"
   response = requests.get(showtime_url)
   
   if response.status_code != 200:
      return make_response(jsonify({"error": "The specified date does not exist"}), 404)
   showtimes_data = response.json()
   
   movies_available = showtimes_data["movies"]
   
   if new_booking["movies"] not in movies_available:
      return make_response(jsonify({"error": f"The movie you chose is not available on the chosen date"}), 404)

   for booking in bookings:
        if str(booking["userid"]) == str(userid):
         for b in booking["dates"]:
            if b["date"]==new_booking["date"]:
               if new_booking["movies"] in b["movies"]:
                  return make_response(jsonify({"error": "This booking already exists for the specified user"}), 409)
               else :
                  b["movies"].append(new_booking["movies"])
         # Add the brackets for b["movies"] otherwise we won't have the right format in the json file 
         booking["dates"].append({"date": new_booking["date"], "movies": [new_booking["movies"]]})
         write(bookings)
         res = make_response(jsonify({"message":"booking added for the requested user"}) ,200)
         return res  
   return make_response(jsonify({"error": "User ID not found"}), 404) 

# delete a booking for a user 
@app.route("/bookings/<userid>", methods=['DELETE'])
def delete_booking_for_user(userid):
   req = request.get_json()
   booking_to_delete = {"date": req["date"], "movie": req["movie"]}

   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         for b in booking["dates"]:
            if b["date"]==booking_to_delete["date"]:
               if booking_to_delete["movie"] in b['movies']:
                  # delete the movie from the movies list and not the date
                  b['movies'].remove(booking_to_delete["movie"])
                  # if the movies list is empty then delete the date too
                  if not b['movies']:
                     booking["dates"].remove(b)
                  write(bookings)
                  return make_response(jsonify({"message":"booking deleted for the requested user"}), 200)
               return make_response(jsonify({"message":"this movie is not booked on this date so it can't be deleted"}), 404)
         return make_response(jsonify({"message":"this booking does not exist so it can't be deleted"}), 404)
   return make_response(jsonify({"error": "User ID not found"}), 400) 

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
