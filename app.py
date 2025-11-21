from flask import Flask, request, jsonify, render_template
from main import generate_final_story

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/story", methods=["POST"])
def api_story():
    data = request.get_json()
    prompt = data["prompt"]

    story, images, judge = generate_final_story(prompt)

    return jsonify({
        "story": story,
        "images": images,
        "judge": judge
    })

if __name__ == "__main__":
    app.run(debug=True)
