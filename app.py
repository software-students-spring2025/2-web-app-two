from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for('homepage'))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for('homepage'))
    return render_template("register.html")

@app.route("/homepage")
def homepage():
    if request.method == "POST":
        return redirect(url_for('gyms'))
    return render_template("homepage.html")

@app.route("/gyms")
def gyms():
    return render_template("gyms.html")

if __name__ == "__main__":
    app.run(debug=True)
