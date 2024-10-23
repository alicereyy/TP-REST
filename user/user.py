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
   
   # Call the API of booking to delete the booking for the requested user
   booking_url = f"http://127.0.0.1:3201/bookings/{userid}"

   response = requests.delete(booking_url, json=booking_to_delete)

   return (response.json())

# Get movies available on a date
@app.route("/users/movies/<date>", methods=['GET'])
def get_movies_on_date(date):
   # We cannot directly write this because users shouldn't access showtime directly
   #showtimes_url= f"http://127.0.0.1:3202/showmovies/{date}"
   #showtimes_response = requests.get(showtimes_url)
   
   # We have to go through booking 
   booking_response = requests.get(f'http://127.0.0.1:3201/bookings/available_movies/{date}')
   
   if booking_response.status_code != 200:
      return make_response(jsonify({"message": "No movies on this date"}), 400)

   response = booking_response.json()
   if not response.get("movies"):
      return make_response(jsonify({"message": "No movies on this date"}), 400)
   
   
   movie_info = []
   for movieid in response["movies"]:
      # Call the movie service to get the movie info 
      movie_response = requests.get(f'http://127.0.0.1:3200/movies/{movieid}')

      if movie_response.status_code == 200:
         movie_info.append(movie_response.json())  
      else:
         return {"message": f"Movie with id {movieid} not found"}

   date_movies = {
      "date": date,
      "movies": movie_info
   }
   return make_response(jsonify(date_movies), 200)

# Get the showdates of a movie
@app.route("/users/schedule/title", methods=['GET'])
def get_dates_with_title():
   
   req = request.get_json()
   title = req.get('title')

   # Get movie information from the title (pass the movie title as a parameter)
   movie_response = requests.get(f'http://127.0.0.1:3200/moviesbytitle?title={title}')
   if not movie_response:
      return make_response(jsonify({"message": "Movie title not found in database"}), 400)
   # Get the movie id from the movie information
   movieid = movie_response.json().get('id')

   # Get the dates available for the chosen movie 
   booking_response = requests.get(f'http://127.0.0.1:3201/bookings/dates/{movieid}')

   if booking_response.status_code != 200:
      return make_response(jsonify({"message": "No available dates for this movie"}), 400)

   response = booking_response.json()

   movie_dates = {
      "movie": movieid,
      "dates": response['dates']
   }
   return make_response(jsonify(movie_dates), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
