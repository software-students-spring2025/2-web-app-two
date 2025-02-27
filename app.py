from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for('homepage'))
    return render_template("login.html")

@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

if __name__ == "__main__":
    app.run(debug=True)
