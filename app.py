from flask import Flask, render_template
import csv
import os

app = Flask(__name__)

# Caminho do CSV
CSV_PATH = os.path.join("data", "input", "produtos.csv")

@app.route("/")
def home():
    produtos = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                produtos.append(row)
    return render_template("index.html", produtos=produtos)

if __name__ == "__main__":
    app.run(debug=True)
