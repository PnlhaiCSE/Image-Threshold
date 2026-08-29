from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    # return "<h1>Hello, World!</h1>"
    return render_template('homePage.jinja', role='devops')

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=5000,
        debug=True
    )