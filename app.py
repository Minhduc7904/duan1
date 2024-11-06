from flask import *
from database_operations import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đặt secret key để sử dụng flash cho thông báo

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        age = request.form.get('age')
        class_ = request.form.get('class')
        school = request.form.get('school')

        # Kiểm tra nếu tên đăng nhập đã tồn tại
        if check(username):
            return jsonify(success=False, message="Tên đăng nhập đã tồn tại.")
        
        # Thêm người dùng mới
        if add_users(username, password, name, age, class_, school):
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="Đăng ký thất bại. Vui lòng thử lại.")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)
        # Kiểm tra thông tin đăng nhập
        if check_login_credentials(username, password):
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('dashboard'))
        else:
            error = "Tên đăng nhập hoặc mật khẩu không đúng."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return "<h1>Chào mừng bạn đến với Dashboard!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)