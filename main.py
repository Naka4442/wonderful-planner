from flask import Flask


app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"


@app.route("/about")
def about():
    return "Страница о сайте!"

@app.route("/Dany")
def Dany():
    return "Страница Дани"

app.run(debug=True)