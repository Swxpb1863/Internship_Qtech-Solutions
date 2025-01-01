from flask import Flask, request, render_template, redirect, jsonify
import random
import string
import socket

app = Flask(__name__)

# In-memory storage for URLs and click counts
url_data = {}

# Get the machine's local IP address
def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# Generate a short URL
def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html', url_data=url_data)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    short_url = generate_short_url()
    # Dynamically generate the full short URL with the machine's IP and port
    host_ip = get_local_ip()
    full_short_url = f"http://{host_ip}:8080/{short_url}"
    url_data[short_url] = {'original_url': original_url, 'clicks': 0, 'full_short_url': full_short_url}
    return redirect('/')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    if short_url in url_data:
        # Increment the click count
        url_data[short_url]['clicks'] += 1
        return redirect(url_data[short_url]['original_url'])
    else:
        return "URL not found", 404

@app.route('/api/urls', methods=['GET'])
def get_urls():
    return jsonify(url_data)

if __name__ == '__main__':
    # Run the app on port 8080 and dynamically get the local IP
    app.run(debug=True, host='0.0.0.0', port=8080)
