from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
  n = int(request.args.get("n", 3))

  cell_size = min(app.config["width"], app.config["height"]) * 0.8 / n

  return render_template("index.html", n=n, cell_size=cell_size)

@app.template_filter()
def cell_size(n):
  return min(app.config["width"], app.config["height"]) * 0.8 / n

if __name__ == "__main__":
  app.run()
