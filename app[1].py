from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    departure = request.form["departure"]
    destination = request.form["destination"]
    departure_date_str = request.form["departure_date"]
    return_date_str = request.form["return_date"]

    # Debug prints to check the input values
    print(f"Departure: {departure}, Destination: {destination}")

    # Check if departure and destination have more than 4 characters
    if len(departure) <= 4 or len(destination) <= 4:
        flash("Departure and destination must have more than 4 characters.", 'error')
        print("Error: Departure and destination must have more than 4 characters.")
        return redirect(url_for("home"))

    # Check if departure and destination are the same
    if departure.lower() == destination.lower():
        flash("Departure and destination cannot be the same.", 'error')
        return redirect(url_for("home"))

    try:
        # Parse dates
        departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d")
        return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", 'error')
        return redirect(url_for("home"))

    # Check if departure and return dates are in the future
    if departure_date <= datetime.now() or return_date <= datetime.now():
        flash("Both departure and return dates must be in the future.", 'error')
        return redirect(url_for("home"))

    try:
        # Import inside the function to avoid circular import
        from project import run_both_services
        # Call the run_both_services function
        run_both_services(departure, destination, departure_date_str, return_date_str)
        session['search_performed'] = True  # Set the flag to indicate a search was performed
    except Exception as e:
        flash(f"An error occurred: {e}", 'error')
        return redirect(url_for("home"))

    return redirect(url_for("results"))

@app.route("/results")
def results():
    if not session.get('search_performed'):
        flash("No search has been performed yet.", 'error')
        return render_template("results.html", expedia_data=[], google_flights_data=[])

    expedia_data = []
    google_flights_data = []

    try:
        # Read Expedia data if the file exists
        try:
            with open("data3.csv", "r", newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                expedia_data = list(reader)
        except FileNotFoundError:
            pass  # If the file does not exist, keep the list empty

        # Read Google Flights data if the file exists
        try:
            with open("data2.csv", "r", newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                google_flights_data = list(reader)
        except FileNotFoundError:
            pass  # If the file does not exist, keep the list empty
    except Exception as e:
        flash(f"An error occurred while reading the data: {e}", 'error')
        return redirect(url_for("home"))

    # Wipe the CSV files after reading the data
    try:
        open("data3.csv", "w").close()
        open("data2.csv", "w").close()
    except Exception as e:
        flash(f"An error occurred while wiping the data: {e}", 'error')
        return redirect(url_for("home"))

    return render_template("results.html", expedia_data=expedia_data, google_flights_data=google_flights_data)

if __name__ == "__main__":
    app.run(debug=True)
