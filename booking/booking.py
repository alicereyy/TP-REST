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

# Return the bookin information by userid
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking["dates"]),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),400)
 

# Add a booking for a user 
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   print(req)
   for booking in bookings:
        if str(booking["userid"]) == str(userid):
         if req in booking["dates"]:
            
            return make_response(jsonify({"error":"this booking already exists"}),409)
         booking["dates"].append(req)
         write(bookings)
         res = make_response(jsonify({"message":"booking added for the requested user"}) ,200)
         return res   
      
def write(bookings):
    with open('{}/databases/booking.json'.format("."), 'w') as f:
        json.dump({"bookings": bookings}, f)
'''
# Method 2 Add a booking for a user 
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   new_booking = {"date": req["date"], "movies": req["movies"]}
   for booking in bookings:
        if str(booking["userid"]) == str(userid):
         for b in booking["dates"]:
            if b["date"]==new_booking["date"]:
               if b["movies"] in new_booking["movies"]:
                  return make_response(jsonify({"error": "This booking already exists for the specified user"}), 409)
         booking["dates"].append(req)
         #write(bookings)
         res = make_response(jsonify({"message":"booking added for the requested user"}) ,200)
         return res  
   return make_response(jsonify({"error": "User ID not found"}), 404) 
'''

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
