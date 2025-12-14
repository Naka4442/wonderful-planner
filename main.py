from flask import Flask, render_template, request


app = Flask(__name__)

@app.route("/")
def index():
    ip_address = request.remote_addr
    return render_template("index.html", ip_address=ip_address)


@app.route("/about")
def about():
    return "Страница о сайте!"

@app.route("/Dany")
def Dany():
    return render_template("dany.html")


@app.route("/yarik")
def yaroslav():
    return render_template("yaroslav.html")

app.run(debug=True)