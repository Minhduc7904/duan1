from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Truyền giá trị fullscreen=True hoặc False vào template
    return render_template('test.html', fullscreen=True)  # Giá trị có thể thay đổi

if __name__ == '__main__':
    app.run(debug=True)
