from flask import Flask, jsonify, render_template, request

from src.data_loader import load_data
from src.analytics import calculate_summary
from src.gemini_service import ask_gemini


app = Flask(__name__)


# Load the data once when the application starts
products, stores, sales, stock = load_data()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    result = calculate_summary(
        products,
        stores,
        sales,
        stock
    )

    return jsonify(result)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        }), 400

    # Calculate verified business evidence
    analytics = calculate_summary(
        products,
        stores,
        sales,
        stock
    )

    # Send verified evidence to Gemini
    answer = ask_gemini(
        question,
        analytics
    )

    return jsonify({
        "question": question,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )