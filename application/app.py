import os
from flask import Flask, request, render_template
import re
from datetime import datetime, timedelta
import pytz
from calendar import monthrange
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pandas as pd
from opencage.geocoder import OpenCageGeocode

api_key = os.getenv('OPENCAGE_API_KEY')
geocoder = OpenCageGeocode(api_key)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    heading = "Philly Food Sites Locator"
    nearest_sites = None
    next_sites = None
    more_sites = False
    closest_shown = False
    start_index = 0

    if request.method == 'POST':
        address = request.form.get('address')
        continue_prompt = request.form.get('continue_prompt')

        if continue_prompt:
            start_index = int(request.form.get('start_index', 0)) + 5

        if continue_prompt == 'closest':
            heading = "Five Next Closest Sites"
            nearest_sites, more_sites = find_nearest_food_sites(address, datetime.now(pytz.timezone('America/New_York')), start_index=start_index)
            closest_shown = True
        elif continue_prompt == 'opening':
            heading = "Next 5 Food Sites Opening Soonest"
            next_sites = find_next_opening_sites(address, datetime.now(pytz.timezone('America/New_York')))
        else:
            nearest_sites, more_sites = find_nearest_food_sites(address, datetime.now(pytz.timezone('America/New_York')))

    return render_template('index.html',
                           heading=heading,
                           nearest_sites=nearest_sites,
                           next_sites=next_sites,
                           more_sites=more_sites,
                           closest_shown=closest_shown)

def nth_weekday(year, month, weekday, n):
    first_day, days_in_month = monthrange(year, month)
    first_occurrence = (weekday - first_day + 7) % 7 + 1
    nth_occurrence = first_occurrence + (n - 1) * 7
    if nth_occurrence > days in month:
        return None
    return nth_occurrence

def normalize_time_string(time_str):
    return time_str.strip().upper()

def next_opening(day_time_list, current_time):
    nth_map = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    try:
        for day_time_str in day_time_list:
            nth_pattern = re.search(r"(first|second|third|fourth|last)\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", day_time_str, re.IGNORECASE)
            if nth_pattern:
                nth, day = nth_pattern.groups()
                n = nth_map[nth.lower()]
                weekday = weekdays.index(day.lower())
                nth_day = nth_weekday(current_time.year, current_time.month, weekday, n)
                if nth_day:
                    times = re.findall(r'\d{1,2}:\d{2} [APMapm]{2}', day_time_str)
                    if len(times) == 2:
                        start_time, end_time = times
                        start_dt = datetime.combine(datetime(current_time.year, current_time.month, nth_day), datetime.strptime(normalize_time_string(start_time), '%I:%M %p').time()).replace(tzinfo=current_time.tzinfo)
                        if current_time < start_dt:
                            return start_dt
            else:
                parts = day_time_str.split(': ')
                if len(parts) != 2:
                    continue
                day, times = parts
                time_ranges = re.findall(r'\d{1,2}:\d{2} [APMapm]{2}', times)
                for i in range(0, len(time_ranges), 2):
                    if i + 1 < len(time_ranges):
                        start_time, end_time = time_ranges[i], time_ranges[i+1]
                        start_dt = datetime.combine(current_time.date(), datetime.strptime(normalize_time_string(start_time), '%I:%M %p').time()).replace(tzinfo=current_time.tzinfo)
                        while start_dt.weekday() != weekdays.index(day.lower()):
                            start_dt += timedelta(days=1)
                        if current_time < start_dt:
                            return start_dt
    except Exception as e:
        print(f"Error parsing day and time string: {day_time_str}, Error: {e}")
    return None

def create_google_maps_url(address):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    return base_url + address.replace(' ', '+')

def is_site_open(day_time_list, current_time):
    nth_map = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    try:
        for day_time_str in day_time_list:
            if '24/7' in day_time_str:
                return True, "24/7"
            nth_pattern = re.search(r"(first|second|third|fourth|last)\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", day_time_str, re.IGNORECASE)
            if nth_pattern:
                nth, day = nth_pattern.groups()
                n = nth_map[nth.lower()]
                weekday = weekdays.index(day.lower())
                nth_day = nth_weekday(current_time.year, current_time.month, weekday, n)
                if nth_day is None:
                    continue
                if nth_day and current_time.day == nth_day:
                    times = re.findall(r'\d{1,2}:\d{2} [APMapm]{2}', day_time_str)
                    if len(times) == 2:
                        start_time, end_time = times
                        start_dt = datetime.strptime(normalize_time_string(start_time), '%I:%M %p').time()
                        end_dt = datetime.strptime(normalize_time_string(end_time), '%I:%M %p').time()
                        if start_dt <= current_time.time() <= end_dt:
                            return True, end_dt.strftime('%I:%M %p')
            else:
                parts = day_time_str.split(': ')
                if len(parts) != 2:
                    continue
                day, times = parts
                time_ranges = re.findall(r'\d{1,2}:\d{2} [APMapm]{2}', times)
                for i in range(0, len(time_ranges), 2):
                    if i + 1 < len(time_ranges):
                        start_time, end_time = time_ranges[i], time_ranges[i+1]
                        start_dt = datetime.strptime(normalize_time_string(start_time), '%I:%M %p').time()
                        end_dt = datetime.strptime(normalize_time_string(end_time), '%I:%M %p').time()
                        if day.lower() == current_time.strftime('%A').lower() and start_dt <= current_time.time() <= end_dt:
                            return True, end_dt.strftime('%I:%M %p')
    except Exception as e:
        print(f"Error parsing day and time string: {day_time_str}, Error: {e}")
    return False, None

def find_nearest_food_sites(user_address, current_time, start_index=0):
    # Load the food sites data
    df = pd.read_csv('complete_food_site_list_with_coordinates.csv')

    # Initialize geolocator
    geolocator = Nominatim(user_agent="food_site_locator")

    try:
        # Get coordinates of user address
        location = geolocator.geocode(user_address)
        user_coords = (location.latitude, location.longitude)
    except AttributeError:
        return "Could not determine location from the provided address.", False

    open_sites = []

    # Check each site if it's open
    for index, row in df.iterrows():
        if isinstance(row['Day and Time'], str):
            day_time_list = row['Day and Time'].split(';')
            is_open, close_time = is_site_open(day_time_list, current_time)
            if is_open:
                site_coords = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_coords, site_coords).miles
                phone_number = row['Phone Number'] if pd.notna(row['Phone Number']) else "no phone number"
                google_maps_url = create_google_maps_url(row['Address'])
                open_sites.append((row['Name'], row['Address'], phone_number, distance, close_time, google_maps_url))

    # Sort sites by distance
    open_sites = sorted(open_sites, key=lambda x: x[3])

    if not open_sites:
        return "No open food sites found.", False

    nearest_sites = "The nearest open food sites are:<br>"
    for site in open_sites[start_index:start_index + 5]:  # Limit to 5 results
        if site[4] == "24/7":
            nearest_sites += f"{site[0]} at {site[1]} (Phone: {site[2]}). It's {site[3]:.2f} miles away and this site is open 24/7. <a href='{site[5]}' target='_blank'>View on Google Maps</a><br><br>"
        else:
            nearest_sites += f"{site[0]} at {site[1]} (Phone: {site[2]}). It's {site[3]:.2f} miles away and closes at {site[4]}. <a href='{site[5]}' target='_blank'>View on Google Maps</a><br><br>"

    return nearest_sites.rstrip("<br><br>"), len(open_sites) > start_index + 5

def find_next_opening_sites(user_address, current_time):
    # Load the food sites data
    df = pd.read_csv('complete_food_site_list_with_coordinates.csv')

    # Initialize geolocator
    geolocator = Nominatim(user_agent="food_site_locator")

    # Get coordinates of user address
    location = geolocator.geocode(user_address)
    user_coords = (location.latitude, location.longitude)

    opening_sites = []

    # Check each site for next opening time
    for index, row in df.iterrows():
        if isinstance(row['Day and Time'], str):
            day_time_list = row['Day and Time'].split(';')
            next_open = next_opening(day_time_list, current_time)
            if next_open:
                site_coords = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_coords, site_coords).miles
                phone_number = row['Phone Number'] if pd.notna(row['Phone Number']) else "no phone number"
                google_maps_url = create_google_maps_url(row['Address'])
                opening_sites.append((row['Name'], row['Address'], phone_number, distance, next_open, google_maps_url))

    # Sort sites by next opening time and then by distance
    opening_sites = sorted(opening_sites, key=lambda x: (x[4], x[3]))

    if not opening_sites:
        return "No upcoming openings found.", False

    next_sites = "The next 5 food sites opening soonest are:<br>"
    for site in opening_sites[:5]:  # Limit to 5 results
        next_sites += f"{site[0]} at {site[1]} (Phone: {site[2]}). It's {site[3]:.2f} miles away. Opening at {site[4].strftime('%B %d %Y at %I:%M %p')}. <a href='{site[5]}' target='_blank'>View on Google Maps</a><br><br>"

    return next_sites

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
