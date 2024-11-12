from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database_operations import *  # Import các hàm check, add_users, check_login_credentials

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đặt secret key để sử dụng session và flash thông báo

# Middleware kiểm tra trạng thái đăng nhập
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Nếu chưa đăng nhập
            flash("Bạn cần đăng nhập để truy cập trang này.", "warning")
            return redirect(url_for('index'))  # Chuyển hướng đến trang index.html
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def root():
    if 'user' in session:
        return redirect(url_for('home'))
    return redirect(url_for('index'))

@app.route('/index')
def index():
    # Nếu đã đăng nhập, chuyển hướng đến main.html
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('index.html')  # Hiển thị trang index.html

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
    # Nếu đã đăng nhập, chuyển hướng đến main.html
    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra thông tin đăng nhập
        if check_login_credentials(username, password):
            session['user'] = username  # Lưu tên người dùng vào session
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('home'))  # Chuyển đến trang main.html
        else:
            error = "Tên đăng nhập hoặc mật khẩu không đúng."
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/home') 
@login_required
def home():
    user = session.get('user')  # Lấy tên người dùng từ session
    return render_template('main.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Xóa thông tin người dùng khỏi session
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for('index'))

@app.route('/documents', methods=['GET', 'POST'])
def documents():
    user = session.get('user')
    per_page = 8  # Số tài liệu hiển thị trên mỗi trang

    # Lấy từ khóa tìm kiếm từ query string và trạng thái bộ lọc từ session hoặc form
    search_term = request.args.get('search', '').strip()
    show_all = request.args.get('show_all', 'false') == 'true'

    if show_all:
        # Hiển thị tất cả tài liệu, xóa trạng thái tìm kiếm và lọc
        exams = get_all_exams()
        session.pop('search_term', None)
        session.pop('exam_types', None)
        session.pop('classes', None)
    elif search_term:
        # Thực hiện tìm kiếm và xóa trạng thái lọc
        exams = search_exam_by_name_case_insensitive(search_term)
        session['search_term'] = search_term  # Lưu từ khóa tìm kiếm vào session
        session.pop('exam_types', None)  # Xóa trạng thái lọc
        session.pop('classes', None)
    elif request.method == 'POST':
        # Thực hiện lọc và xóa trạng thái tìm kiếm
        selected_exam_types = request.form.getlist('exam_types')
        selected_classes = request.form.getlist('class')

        # Lưu trạng thái lọc vào session
        session['exam_types'] = selected_exam_types
        session['classes'] = selected_classes
        session.pop('search_term', None)  # Xóa trạng thái tìm kiếm

        # Redirect tới GET để tránh "Resubmit the form"
        return redirect(url_for('documents'))
    else:
        # Trường hợp không có hành động mới
        selected_exam_types = session.get('exam_types', [])
        selected_classes = session.get('classes', [])

        if selected_exam_types or selected_classes:
            # Lọc theo trạng thái đã lưu
            exams = search_exams_by_types_and_class(
                exam_types=selected_exam_types,
                class_=selected_classes
            )
        elif 'search_term' in session and session['search_term']:
            # Tìm kiếm theo trạng thái đã lưu
            exams = search_exam_by_name_case_insensitive(session['search_term'])
        else:
            # Hiển thị tất cả tài liệu
            exams = get_all_exams()

    # Phân trang
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_exams = exams[start:end]
    total_pages = (len(exams) + per_page - 1) // per_page

    return render_template(
        'documents.html',
        user=user,
        documents=paginated_exams,
        page=page,
        total_pages=total_pages,
        total_exams=len(exams),
        selected_exam_types=session.get('exam_types', []),
        selected_classes=session.get('classes', []),
        search_term=session.get('search_term', '')  # Hiển thị từ khóa tìm kiếm nếu có
    )




@app.route('/showexam/<int:exam_id>')
def showexam(exam_id):
    user = session.get('user')
    showmenu = request.args.get('showmenu', 'false').lower() == 'true'
    try:
        # Lấy danh sách câu hỏi từ bài thi
        questions = get_questions_in_exam(exam_id)
        exam = get_exam_by_id(exam_id)

        if not questions:
            flash(f"Bài thi với ID {exam_id} không có câu hỏi nào.", "warning")
            return redirect(url_for('documents'))

        # Giải nén danh sách câu hỏi
        trac_nghiem_data = questions["trac_nghiem"]
        dung_sai_data = questions["dung_sai"]
        cau_hoi_ngan = questions["ngan"]["questions"]
        cau_hoi_ngan_image_paths = questions["image_paths"][-len(cau_hoi_ngan):]  # Hình ảnh cho trả lời ngắn

        # Tách đáp án bằng dấu "--" và lọc phần tử rỗng
        trac_nghiem_answers_splitted = [
            [answer.strip() for answer in answers.split('--') if answer.strip()]
            for answers in trac_nghiem_data["answers"]
        ]
        dung_sai_answers_splitted = [
            [answer.strip() for answer in answers.split('--') if answer.strip()]
            for answers in dung_sai_data["answers"]
        ]

        # Chuẩn bị dữ liệu cho phần trắc nghiệm với nhãn A, B, C, D
        trac_nghiem = [
            {
                "question": question,
                "answers": [{"label": label, "text": answer} for label, answer in zip(['A.', 'B.', 'C.', 'D.'], answers)],
                "image_path": questions["image_paths"][i]  # Đường dẫn hình ảnh tương ứng (nếu có)
            }
            for i, (question, answers) in enumerate(zip(trac_nghiem_data["questions"], trac_nghiem_answers_splitted))
        ]

        # Chuẩn bị dữ liệu cho phần đúng/sai với nhãn a), b), c), d)
        dung_sai = [
            {
                "question": question,
                "answers": [{"label": label, "text": answer} for label, answer in zip(['a)', 'b)', 'c)', 'd)'], answers)],
                "image_path": questions["image_paths"][len(trac_nghiem) + i]  # Đường dẫn hình ảnh cho đúng/sai
            }
            for i, (question, answers) in enumerate(zip(dung_sai_data["questions"], dung_sai_answers_splitted))
        ]

        # Chuẩn bị dữ liệu cho phần trả lời ngắn
        short_answer = [
            {
                "question": question,
                "image_path": cau_hoi_ngan_image_paths[i]  # Đường dẫn hình ảnh cho câu hỏi trả lời ngắn (nếu có)
            }
            for i, question in enumerate(cau_hoi_ngan)
        ]

        # Render template ShowExam.html
        return render_template(
            'ShowExam.html',
            user=user,
            exam_name=exam['name'],
            trac_nghiem=trac_nghiem,
            dung_sai=dung_sai,
            short_answer=short_answer,
            exam_id=exam_id,
            showmenu=showmenu
        )
    except Exception as e:
        print(showmenu)
        print(f"Lỗi khi tải bài thi với ID {exam_id}: {e}")
        flash(f"Lỗi khi tải bài thi với ID {exam_id}.", "danger")
        return redirect(url_for('documents'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
