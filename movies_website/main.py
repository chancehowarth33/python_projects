import pandas as pd
from flask import Flask, request, jsonify, g, send_file, abort, make_response, Response
import time
from datetime import datetime, timedelta
from collections import defaultdict
import random
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tempfile import TemporaryFile
import re
from collections import deque


matplotlib.use('Agg')
app = Flask(__name__)
df = pd.read_csv("main.csv")


@app.route('/browse.html')
def browse():
    # Convert the DataFrame to HTML and avoid truncation of float data
    data_html = df.to_html(float_format = lambda x: '%.6f' % x)
    # Return the data wrapped in HTML tags
    return f"<html><body><h1>Browse Data</h1>{data_html}</body></html>"


ip_requests = defaultdict(deque)
@app.route('/browse.json')
def browse_json():
    # Get client IP
    ip = request.remote_addr

    # Get current time
    now = datetime.now()

    # Deque object to hold timestamps of requests. It removes older timestamps automatically.
    timestamps = ip_requests[ip]
    while timestamps and now - timestamps[0] > timedelta(minutes=1):
        timestamps.popleft()  # Remove timestamps older than 1 minute

    if len(timestamps) >= 1:  # Limit to 1 request per minute
        # Return 429 status code and Retry-After header
        response = make_response(jsonify({'error': 'Too Many Requests'}), 429)
        response.headers['Retry-After'] = 60  # Retry after 60 seconds
        return response

    # Add the current request timestamp to the deque
    timestamps.append(now)

    # Return data in JSON format
    data = df.to_dict(orient='records')
    return jsonify(data)


@app.route('/visitors.json')
def visitors_json():
    # Convert IP requests data to a list of IPs
    visitors = list(ip_requests.keys())
    return jsonify(visitors)


homepage_visits = 0
donation_clicks = {"A": 0, "B": 0}

@app.route('/')
def home():
    global homepage_visits
    # increase counter for each visit
    homepage_visits += 1
    with open("index.html") as f:
        html = f.read()
    # change the color and link of donation button based on visit number
    if homepage_visits <= 10:
        color = "blue" if homepage_visits % 2 == 0 else "red"
        version = "A" if color == "blue" else "B"
    else:
        # after 10 visits, use the version which received more donation clicks
        version = max(donation_clicks, key=donation_clicks.get)
        color = "blue" if version == "A" else "red"
    # create the new dynamic donation link
    donation_link = f'<p>Donate <a href="donate.html?from={version}" style="color:{color}">here</a>.</p>'
    # replace the existing static donation link in the html with the new dynamic donation link
    html = html.replace('<p>Donate <a href="donate.html">here</a>.</p>', donation_link)
    return html


@app.route('/donate.html')
def donate():
    # get the version from which the user came
    version = request.args.get("from")
    # if version is none, default to "A"
    if version is None:
        version = "A"
    # increase the counter for the respective version
    donation_clicks[version] += 1
    # the content of your donation page
    return "<h1>Thank you for your support!</h1>"

num_subscribed = 0
@app.route('/email', methods=["POST"])
def email():
    global num_subscribed
    email = str(request.data, "utf-8")
    #makes sure correct characters are in the email 
    regex = r"^[^@](\w+)(@{1})(\w+\.)(edu|com|org|net|io|gov)"
    if len(re.findall(regex, email)) > 0:
        with open("emails.txt", "a") as f: 
            f.write(email + '\n') # 2
        num_subscribed+=1
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("invalid email address") 


@app.route('/histogram.svg')
def histogram():
    fig, ax = plt.subplots()
    ratings = df['Meta_score']
    ax.hist(ratings, bins=10, edgecolor='black')
    ax.set_ylabel('Number of Movies')
    ax.set_xlabel('Rating')
    ax.set_title('Histogram of META Ratings')
    ax.grid(True)

    bytes_image = io.BytesIO()
    fig.savefig(bytes_image, format='svg')
    plt.close(fig)
    bytes_image.seek(0)
    return Response(bytes_image.getvalue(), headers = {"Content-Type": "image/svg+xml"})


@app.route('/line.svg')
def line():
    fig, ax = plt.subplots()
    # average rating by year
    avg_rating_by_year = df.groupby('Released_Year')['IMDB_Rating'].mean()
    # Plot the data
    ax.plot(avg_rating_by_year.index, avg_rating_by_year.values, marker ='o')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Rating')
    ax.set_title('Average IMDB Rating Over Time')
    # sets ticks of the x-axis
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(int(start), int(end), 10))
    
    bytes_image = io.BytesIO()
    fig.savefig(bytes_image, format='svg')
    plt.close(fig)
    bytes_image.seek(0)
    return Response(bytes_image.getvalue(), headers = {"Content-Type": "image/svg+xml"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) 
