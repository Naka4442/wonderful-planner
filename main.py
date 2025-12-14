from flask import Flask, render_template, request


app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def index():
    ip_address = request.remote_addr
    return render_template("index.html", ip_address=ip_address)


@app.route("/signup")
def signup():
    return render_template("signup.html")


app.run(debug=True)