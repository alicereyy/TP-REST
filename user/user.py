from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

#Returns all the users 
@app.route("/users", methods = ['GET'])
def get_json():
   res = make_response(jsonify(users), 200)
   return res
   
# Returns all the booked movies of a user 
@app.route("/users/<userid>", methods = ['GET'])
def get_booking_for_userid(userid):
   booking_url = f"http://127.0.0.1:3201/bookings/{userid}"
   response = requests.get(booking_url)
   for user in users:
      if str(user["id"]) == str(userid):
         if response.status_code != 200:
            return make_response(jsonify({"error": "This user does not have any bookings"}), 404)
         user_bookings = response.json()
         res = make_response(jsonify(user_bookings) ,200)
         return res
   
   return(make_response(jsonify({"error": "This user does not exist in the users database"}), 400))

# Returns the booked movies of a user on the chosen date 
@app.route("/users/<userid>/<date>", methods = ['GET'])
def get_booking_by_date_user(userid, date):
   booking_url= f"http://127.0.0.1:3201/bookings/{userid}"
   response = requests.get(booking_url)
   if response.status_code != 200:
      return make_response(jsonify({"error": "This user does not have any bookings"}), 404)
   user_bookings = response.json()
   for user in users:
      if str(user["id"]) == str(userid):
         
         for user_booking in user_bookings :
            if str(user_booking["date"]) == str(date):
               booking_for_user = make_response(jsonify(user_booking),200)
               return booking_for_user
         return make_response(jsonify({"error": "there are no bookings on this date for this user"}), 409)
   return make_response(jsonify({"error": "this user does not exist"}), 400)
      
# Returns all the booked movies' information of a user 
@app.route("/users/movie_info/<userid>", methods = ['GET'])
def get_movies_info_for_user_bookings(userid):
   bookings_url= f"http://127.0.0.1:3201/bookings/{userid}"
   response = requests.get(bookings_url)
   
   if response.status_code != 200:
      return make_response(jsonify({"error": "This user does not have any bookings"}), 404)
   user_bookings = response.json()
   
   for user in users:
      if str(user["id"]) == str(userid):
         movies_infos = []
         for user_booking in user_bookings :
            booking_info = {
               'date': user_booking["date"],
               'movies': []
            }
            for movieid in user_booking["movies"]:
               movie_url = f"http://127.0.0.1:3200/movies/{movieid}"
               response2 = requests.get(movie_url)
               movie_info = response2.json()
               #print(movie_info)
               booking_info['movies'].append(movie_info)
            movies_infos.append(booking_info)
         res = make_response(jsonify(movies_infos), 200)
         return res
   return make_response(jsonify({"error": "This user does not exist in the users database"}), 400)

# Add a booking for a user 
@app.route("/users/<userid>", methods=['POST'])
def add_booking_for_user(userid):
   req = request.get_json()
   booking_to_add = {"date": req["date"], "movies": req["movies"]}

   # Call the API of booking to add the booking for the requested user
   booking_url = f"http://127.0.0.1:3201/bookings/{userid}"
   
   response = requests.post(booking_url, json=booking_to_add)

   return (response.json())

# Delete a booking for a user
@app.route("/users/<userid>", methods=['DELETE'])
def delete_booking_for_user(userid):
   req = request.get_json()
   booking_to_delete = {"date": req["date"], "movie": req["movie"]}
   
   # Call the API of booking to add the booking for the requested user
   booking_url = f"http://127.0.0.1:3201/bookings/{userid}"

   response = requests.delete(booking_url, json=booking_to_delete)

   return (response.json())
   

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
