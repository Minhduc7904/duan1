from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.json  # Lấy dữ liệu từ form
    print("Collected Answers:", data)
    return jsonify({"message": "Đáp án đã được nhận!"})

if __name__ == '__main__':
    app.run(debug=True)
