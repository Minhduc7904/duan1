from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database_operations import *  # Import các hàm check, add_users, check_login_credentials
import unicodedata
from readdata import *
from flask import request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime

UPLOAD_FOLDER_QUESTION = './static'

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
logs = {}
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đặt secret key để sử dụng session và flash thông báo
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER_QUESTION, exist_ok=True)
app.config['UPLOAD_FOLDER_QUESTION'] = UPLOAD_FOLDER_QUESTION

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware kiểm tra trạng thái đăng nhập
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Nếu chưa đăng nhập
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
    print(session)
    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra thông tin đăng nhập
        user_id = check_login_credentials(username, password)
        print(user_id)
        if  user_id != None:
            session['user'] = user_id  # Lưu tên người dùng vào session
            return redirect(url_for('home'))  # Chuyển đến trang main.html
        else:
            error = "Tên đăng nhập hoặc mật khẩu không đúng."
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/home') 
@login_required
def home():
    user1 = find_user_by_id(session.get('user'))
    if user1 == None:
        return render_template('index.html')
    user = user1["name"]
    events = [
        {
            "id": 1,
            "title": "Thi tốt nghiệp trung học phổ thông năm 2025",
            "date": "2025-06-26T00:00:00",  # Định dạng ISO
            "description": "Thi tốt nghiệp THPT trên toàn quốc. Thí sinh lưu ý kiểm tra lịch thi và chuẩn bị hồ sơ."
        },
    ]
    notifications = [
        {"message": "Hạn đăng ký thi THPT quốc gia là ngày 10/12/2024."},
        {"message": "Bài kiểm tra định kỳ tháng 11 đã được đăng tải."},
    ]
    return render_template('main.html', user=user, user1=user1, events=events, notifications=notifications)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Xóa thông tin người dùng khỏi session
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
def reportweb():
    if session.get('user') == None:
        return redirect('/')
    if request.method == 'POST':
        user1 = find_user_by_id(session.get('user'))
        user = user1["name"]

        # Lấy dữ liệu từ form
        erType = request.form.get('errorType')
        questionId = None
        if erType == 'question':
            questionId = request.form.get('questionId')
        errorDescription = request.form.get('errorDescription')

        add_user_report(session.get('user'), erType, errorDescription, questionId)

        flash("Báo cáo của bạn đã được gửi thành công!", "success")

        return redirect(url_for('report_confirmation', is_document = False,
        is_assignments = False,
        is_createdexam = False,
        is_wiki = False,))
    else:

        return redirect(url_for('report_confirmation', is_document = False,
        is_assignments = False,
        is_createdexam = False,
        is_wiki = False,))

@app.route('/report-confirmation')
def report_confirmation():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]

    return render_template('report.html', user=user, user1=user1)


@app.route('/documents', methods=['GET', 'POST'])
def documents():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"] 
    per_page = 9  # Số tài liệu hiển thị trên mỗi trang

    # Lấy từ khóa tìm kiếm từ query string và trạng thái bộ lọc từ session hoặc form
    search_term = request.args.get('search', '').strip()
    show_all = request.args.get('show_all', 'false') == 'true'

    if show_all:
        # Hiển thị tất cả tài liệu, xóa trạng thái tìm kiếm và lọc
        exams = get_all_exams()
        for exam in exams: print(exam)
        session.pop('search_term', None)
        session.pop('exam_types', None)
        session.pop('classes', None)
        session.pop('chapter', None)
    elif search_term:
        # Thực hiện tìm kiếm và xóa trạng thái lọc
        exams = search_exam_by_name_case_insensitive(search_term)
        session['search_term'] = search_term  # Lưu từ khóa tìm kiếm vào session
        session.pop('exam_types', None)  # Xóa trạng thái lọc
        session.pop('classes', None)
        session.pop('chapter', None)
    elif request.method == 'POST':
        # Thực hiện lọc và xóa trạng thái tìm kiếm
        selected_exam_types = request.form.getlist('exam_types')
        selected_classes = request.form.getlist('class')
        selected_chapters = request.form.getlist('chapter')

        # Lưu trạng thái lọc vào session
        session['exam_types'] = selected_exam_types
        session['classes'] = selected_classes
        session['chapter'] = selected_chapters
        session.pop('search_term', None)  # Xóa trạng thái tìm kiếm

        # Redirect tới GET để tránh "Resubmit the form"
        return redirect(url_for('documents'))
    else:
        # Trường hợp không có hành động mới
        selected_exam_types = session.get('exam_types', [])
        selected_classes = session.get('classes', [])
        selected_chapters = session.get('chapter', [])

        if selected_exam_types or selected_classes or selected_chapters:
            # Lọc theo trạng thái đã lưu
            exams = search_exams_by_types_class_and_chapter(
                exam_types=selected_exam_types,
                class_=selected_classes,
                chapters=selected_chapters
            )
        elif 'search_term' in session and session['search_term']:
            # Tìm kiếm theo trạng thái đã lưu
            exams = search_exam_by_name_case_insensitive(session['search_term'])
        else:
            # Hiển thị tất cả tài liệu
            exams = get_all_exams()

    # Phân trang
    exams.reverse()
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
        search_term=session.get('search_term', ''),  # Hiển thị từ khóa tìm kiếm nếu có
        user1 = user1,
        is_document = True,
        is_assignments = False,
        is_createdexam = False,
        is_wiki = False,
    )

@app.route('/createdexam', methods=['GET', 'POST'])
def createdexam():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"] 
    
    return render_template(
        'createdexam.html',
        user=user,
        user1=user1,
        is_document = False,
        is_assignments = False,
        is_createdexam = True,
        is_wiki = False,
    )

@app.route('/update-avatar', methods=['POST'])
def update_avatar():
    if session.get('user') == None:
        return redirect('/')
    if 'avatar' not in request.files:
        return "Không tìm thấy tệp tải lên.", 400
    
    file = request.files['avatar']

    if file.filename == '':
        return "Không có tệp nào được chọn.", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = session.get('user')  # Lấy ID người dùng từ session
        if not user_id:
            return "Người dùng chưa đăng nhập.", 403

        # Tạo thư mục riêng cho người dùng (nếu cần)
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        user = find_user_by_id(user_id)  # Hàm này trả về thông tin người dùng từ DB
        old_avatar_path = user.get('avatar_path')
        if old_avatar_path:
            # Tính đường dẫn đầy đủ của file cũ
            old_avatar_full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.relpath(old_avatar_path, start="/static"))
            # Xóa file cũ nếu tồn tại
            if os.path.exists(old_avatar_full_path):
                os.remove(old_avatar_full_path)

        
        # Lưu file vào thư mục
        filepath = os.path.join(user_folder, filename)
        file.save(filepath)

        # Đường dẫn tương đối để lưu vào cơ sở dữ liệu
        avatar_path = os.path.relpath(filepath, start=app.config['UPLOAD_FOLDER'])
        avatar_path = f"/static/{avatar_path.replace(os.sep, '/')}"  # Định dạng URL

        # Cập nhật avatar vào cơ sở dữ liệu
        success = update_user_field(user_id, 'avatar_path', avatar_path)
        if success:
            return redirect(url_for('useraccount'))
        else:
            return "Không thể cập nhật avatar.", 500

    return "Tệp không hợp lệ.", 400

@app.route('/update-user-info', methods=['POST'])
def update_user_info():
    if session.get('user') == None:
        return redirect('/')
    field = request.form.get('field')
    value = request.form.get('value')
    user_id = session.get('user')

    if not user_id:
        return "Người dùng chưa đăng nhập.", 403

    if not field or not value:
        return "Dữ liệu không hợp lệ.", 400

    if field == 'password':
        # Tách chuỗi giá trị để lấy mật khẩu cũ và mới
        try:
            old_password, new_password = value.split(',', 1)

            # Lấy thông tin người dùng từ DB
            user = find_user_by_id(user_id)
            if not user:
                return "Người dùng không tồn tại.", 404

            # Kiểm tra mật khẩu cũ
            if user['password'] != old_password:  # `verify_password` kiểm tra hash mật khẩu
                return "Mật khẩu cũ không đúng.", 403

            # Cập nhật mật khẩu mới (hash trước khi lưu)
            hashed_new_password = new_password  # `hash_password` để mã hóa mật khẩu
            success = update_user_field(user_id, 'password', hashed_new_password)

            if success:
                return redirect('/user-account')
            else:
                return "Không thể cập nhật mật khẩu.", 500
        except ValueError:
            return "Dữ liệu không hợp lệ.", 400
    else:
        # Xử lý các trường khác
        success = update_user_field(user_id, field, value)
        if success:
            return redirect('/user-account')
        else:
            return "Không thể cập nhật thông tin.", 500

@app.route('/user-account')
def useraccount():
    if session.get('user') == None:
        return redirect('/')
    # Lấy thông tin người dùng từ cơ sở dữ liệu dựa trên ID từ session
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]

    return render_template(
        'user-account.html',
        user=user,
        user1=user1
    )

@app.route('/update-sidebar', methods=['POST'])
def update_sidebar():
    data = request.json
    session['opensidebar'] = data.get('opensidebar', False)
    print(session['opensidebar'])
    return jsonify({'opensidebar': session['opensidebar']})

@app.route('/get-sidebar-status', methods=['GET'])
def get_sidebar_status():
    opensidebar = session.get('opensidebar', True)  # Lấy giá trị từ session
    return jsonify({'opensidebar': opensidebar})

@app.route('/your-assignments')
def yourassignments():
    if session.get('user') == None:
        return redirect('/')
    value = request.args.get('value', default=1, type=int)
    page = request.args.get('page', default=1, type=int)
    user_id = session.get('user')

    if user_id == None:
        return redirect('/login')

    user1 = find_user_by_id(user_id)
    user = user1["name"]


    opensidebar = session.get('opensidebar', True)
    if value == 1:
        # Xử lý danh sách bài thi của bạn
        per_page = 6
        exams = get_all_exams_with_conditions(user_id=user_id, is_favorite=1)
        exams.reverse()
        start = (page - 1) * per_page
        end = start + per_page
        paginated_exams = exams[start:end]
        total_pages = (len(exams) + per_page - 1) // per_page

        return render_template(
            'your-assignments.html',
            user=user,
            documents=paginated_exams,
            page=page,
            total_pages=total_pages,
            total_exams=len(exams),
            value=value,
            per_page=per_page,
            user1 = user1,
            is_document = False,
            is_assignments = True,
            is_createdexam = False,
            is_wiki = False,
            opensidebar = opensidebar,
        )

    elif value == 4:
        # Xử lý lịch sử làm bài
        per_page = 8
        exams = get_user_exam_history(user_id)

        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_exams = exams[start:end]
        scores = [exam['score'] for exam in paginated_exams]
        times = [exam['completion_time'] if isinstance(exam['completion_time'], str) else exam['completion_time'].strftime('%d/%m/%Y %H:%M') for exam in paginated_exams]
        scores.reverse()
        times.reverse()
        average_score_exam =[]
        for exam in paginated_exams:
            average_score_exam.append(calculate_average_score_by_exam_id(exam['exam_id']))

        total_pages = (len(exams) + per_page - 1) // per_page

        return render_template(
            'your-assignments.html',
            user=user,
            value=value,
            completed_exams=paginated_exams,
            page=page,
            total_pages=total_pages,
            total_exams=len(exams),
            per_page=per_page,
            user1 = user1,
            is_document = False,
            is_assignments = True,
            is_createdexam = False,
            is_wiki = False,
            opensidebar = opensidebar,
            scores=json.dumps(scores),
            times=json.dumps(times),
            average_scores=json.dumps(average_score_exam),
        )

    elif value == 3:
        count_completed_exam, trung_binh, total_created_exams = get_user_exam_statistics(user_id)
        exams = get_all_exams_with_conditions(user_id=user_id)
        exams.reverse()
        correct_answers, incorrect_answers = calculate_correct_incorrect_answers(user_id)
        return render_template(
            'your-assignments.html',
            user=user,
            total_exams=len(exams),
            count_completed_exam=count_completed_exam,
            value=value,
            total_created_exams=total_created_exams,
            trung_binh=round(trung_binh, 2),
            user1 = user1,
            is_document = False,
            is_assignments = True,
            is_createdexam = False,
            is_wiki = False,
            opensidebar = opensidebar,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
        )

    else:
        per_page = 6
        exams = get_all_exams_with_conditions(user_id = user_id, created_by_user=1)
        exams.reverse()
        start = (page - 1) * per_page
        end = start + per_page
        paginated_exams = exams[start:end]
        total_pages = (len(exams) + per_page - 1) // per_page

        return render_template(
            'your-assignments.html',
            user=user,
            documents=paginated_exams,
            page=page,
            total_pages=total_pages,
            total_exams=len(exams),
            value=value,
            per_page=per_page,
            user1 = user1,
            is_document = False,
            is_assignments = True,
            is_createdexam = False,
            is_wiki = False,
            opensidebar = opensidebar,
        )


@app.route('/showexam/<int:exam_id>')
def showexam(exam_id):
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    showmenu = request.args.get('showmenu', 'false').lower() == 'true'
    user_id = session.get('user')
    his_id = session.get(str(exam_id))
    full_screen = False
    if showmenu: full_screen=True


    if showmenu and his_id == None:
        his_id = Done_exam(user_id, exam_id, 0)
        session[str(exam_id)] = his_id

    start_time = None
    end_time = None

    if his_id != None:
        time = get_exam_time_by_summary_id(his_id)
        start_time = time['start_time']
        end_time = time['end_time']
    
    if start_time and end_time:
        now = datetime.now()

        if start_time <= now <= end_time:
            showmenu = True
        else:
            session.pop(str(exam_id), None)
            showmenu = False
    
    start_time_str=""
    end_time_str=""
    if showmenu and start_time and end_time:
        start_time = datetime.strptime(str(start_time), '%Y-%m-%d %H:%M:%S.%f')
        end_time = datetime.strptime(str(end_time), '%Y-%m-%d %H:%M:%S.%f')
        # Nếu start_time hoặc end_time là None
        # Chuyển đổi datetime sang string để truyền qua HTML
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    if request.args.get('showmenu') == 'true':
        return jsonify({
            "start_time": start_time_str,
            "end_time": end_time_str,
            "showmenu": True,
        })
    is_favorite = check_user_exam_is_favorite(user_id, exam_id)

    summary_id = get_latest_summary_id(user_id, exam_id)
    # Lấy danh sách câu hỏi từ bài thi
    questions = get_questions_in_exam(exam_id)
    exam = get_exam_by_id(exam_id)
    completed = 0
    if (summary_id != None):
        completed = 1

    if not questions:
        print(f"Bài thi với ID {exam_id} không có câu hỏi nào.", "warning")
        return redirect(url_for('documents'))

    # Giải nén danh sách câu hỏi
    trac_nghiem_data = questions["trac_nghiem"]
    dung_sai_data = questions["dung_sai"]
    cau_hoi_ngan = questions["ngan"]

    # Tách đáp án bằng dấu "--" và lọc phần tử rỗng
    trac_nghiem_answers_splitted = [
        [answer.strip() for answer in question["answer_options"].split('--') if answer.strip()]
        for question in trac_nghiem_data
    ]
    dung_sai_answers_splitted = [
        [answer.strip() for answer in question["answer_options"].split('--') if answer.strip()]
        for question in dung_sai_data
    ]

    trac_nghiem = [
        {
            "question_id": question["question_id"],
            "question": question["content"],
            "answers": [{"label": label, "text": answer} for label, answer in zip(['A.', 'B.', 'C.', 'D.'], answers)],
            "image_path": question["image_path"] 
        }
        for i, (question, answers) in enumerate(zip(trac_nghiem_data, trac_nghiem_answers_splitted))
    ]

    # Chuẩn bị dữ liệu cho phần đúng/sai với nhãn a), b), c), d)
    dung_sai = [
        {
            "question_id": question["question_id"],
            "question": question["content"],
            "answers": [{"label": label, "text": answer} for label, answer in zip(['a)', 'b)', 'c)', 'd)'], answers)],
            "image_path": question["image_path"]
        }
        for i, (question, answers) in enumerate(zip(dung_sai_data, dung_sai_answers_splitted))
    ]

    # Chuẩn bị dữ liệu cho phần trả lời ngắn
    short_answer = [
        {
            "question_id": question["question_id"],
            "question": question["content"],
            "image_path": question["image_path"]
        }
        for i, question in enumerate(cau_hoi_ngan)
    ]
    print(full_screen)
    return render_template(
        'ShowExam.html',
        user=user,
        exam_name=exam['name'],
        duration=exam['duration'],
        trac_nghiem=trac_nghiem,
        dung_sai=dung_sai,
        short_answer=short_answer,
        exam_id=exam_id,
        summary_id=summary_id,
        showmenu=showmenu,
        len1 = len(trac_nghiem),
        len2 = len(dung_sai),
        len3 = len(short_answer),
        completed=completed,
        is_favorite = is_favorite,
        user1=user1,
        start_time=start_time_str,
        end_time=end_time_str,
        fullscreen=full_screen,   
    )

def normalize_text(text):
    """Chuẩn hóa và thay thế các ký tự đặc biệt"""
    # Chuẩn hóa Unicode (NFC)
    text = unicodedata.normalize("NFC", text)

    # Thay thế ký tự "Ð" thành "Đ" để đồng nhất
    text = text.replace("Ð", "Đ")

    # Loại bỏ khoảng trắng thừa
    return text.strip()

@app.route('/nopbai/<int:exam_id>', methods=['POST'])
def nopbai(exam_id):
    if session.get('user') == None:
        return redirect('/')
    his_id = session.get(str(exam_id))
    if his_id == None:
        return redirect('/')
    trac_nghiem, dung_sai, ngan = get_key_from_exam(exam_id)
    score = 0
    user1 = find_user_by_id(session.get('user'))
    user_id = user1["user_id"] 
    print(trac_nghiem, dung_sai, ngan)
    for i, question in enumerate(trac_nghiem, start=1):
        question_id = question["question_id"]
        correct_answer = question["correct_answer"]
        answer = request.form.get(f'question-{i}')
        if answer and answer == correct_answer:
            score += 0.25  # Cộng điểm nếu đúng
            User_does_Answers(his_id, user_id, exam_id, question_id, answer, 1)
        else :
            User_does_Answers(his_id, user_id, exam_id, question_id, answer, 0)

    for i, question in enumerate(dung_sai, start=1):  # Lặp qua từng câu hỏi đúng/sai
        count = 0
        question_id = question["question_id"]
        correct_answers = question["correct_answer"].split(' ')  # Tách các đáp án đúng thành danh sách
        answers = ""  # Biến lưu các câu trả lời của người dùng

        for sub_question, correct_answer in zip(['a', 'b', 'c', 'd'], correct_answers):  # Duyệt qua từng lựa chọn
            answer = request.form.get(f'tf-question-{i}-{sub_question}')  # Lấy đáp án người dùng
            answer = str(answer) if answer else ""  # Đảm bảo answer luôn là chuỗi

            answer_normalized = normalize_text(answer)
            correct_answer_normalized = normalize_text(correct_answer[2:])  # Loại bỏ tiền tố a), b), ...
            answers += f"{sub_question}){answer} "

            if answer_normalized == correct_answer_normalized:  # So sánh chuỗi đã chuẩn hóa
                count += 1  

        is_correct = 0
        if count == 4:
            is_correct = 1
            
            score += 1
        elif count == 3:
            score += 0.5
        elif count == 2:
            score += 0.25
        elif count == 1:
            score += 0.1
        User_does_Answers(his_id, user_id, exam_id, question_id, answers, is_correct)
    for i, question in enumerate(ngan, start=1):
        question_id = question["question_id"]
        correct_answer = question["correct_answer"]
        answer = request.form.get(f'short-answer-{i}')
        if answer and answer.strip() == correct_answer.strip():
            User_does_Answers(his_id, user_id, exam_id, question_id, answer, 1)
            score += 0.5
        else : User_does_Answers(his_id, user_id, exam_id, question_id, answer, 0)
    

    his_id_str = str(his_id)
    if his_id_str in logs:
        log = logs[his_id_str]
        update_user_exam_score(his_id, score, log)
        del logs[str(his_id)]
    else:
        update_user_exam_score(his_id, score, None)
    print(score)
    update_score_lastest(user_id, exam_id, score)
    session.pop(str(exam_id), None)
    return redirect(url_for('score_page', summary_id = his_id))


@app.route('/score')
def score_page():
    if session.get('user') == None:
        return redirect('/')
    summary_id = request.args.get('summary_id', type=int)
    value = get_summary_details(summary_id)
    user_id = value["user_id"]
    exam_id = value["exam_id"]
    score = value["score"]
    log = value["logs"]
    formatted_logs = []
    if log:
        try:
            log = json.loads(log)  # Chuyển JSON string thành Python object (list)
            for entry in log:  # Duyệt qua từng phần tử của danh sách
                entry['formatted_time'] = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                formatted_logs.append(entry)
        except Exception as e:
            print(f"Lỗi xử lý log: {e}")
    exam = get_exam_by_id(exam_id)
    if user_id != None and exam_id != None and score != None:
        user = find_user_by_id(user_id)
        
        questions = get_user_answers_and_correct_answers(summary_id)
        num_correct = sum(1 for q in questions if q['is_correct'] is True)
        num_wrong = sum(1 for q in questions if q['is_correct'] is False)
        return render_template(
            'score.html',
            user=user['name'],
            score=score,
            total_score=10,  
            exam_id = exam_id,
            exam_name=exam['name'],
            questions=questions,  
            user1=user,
            num_correct=num_correct,
            num_wrong=num_wrong,
            logs=formatted_logs,
            num_errors=len(formatted_logs),
        )
    else:
        return redirect('/')  

@app.route('/unfavorite_exam/<int:exam_id>', methods=['POST'])
def unfavorite_exam(exam_id):
    """
    Route để xử lý yêu cầu bỏ bài thi khỏi danh sách "Yêu thích".
    """
    if session.get('user') == None:
        return redirect('/')
    try:
        # Lấy user_id từ session (giả định user_id được lưu trong session)
        user_id = session.get('user')  # Đảm bảo 'user' là key chính xác trong session
        
        if user_id is None:
            return redirect('/login')  # Chuyển hướng nếu người dùng chưa đăng nhập

        # Gọi hàm cập nhật is_favorite thành 0
        success = update_is_favorite(user_id, exam_id, 0)

        if success:
            print("Bài thi đã được xóa khỏi danh sách yêu thích.", "success")
        else:
            print("Đã xảy ra lỗi khi xóa bài thi khỏi danh sách yêu thích.", "error")
        
        # Chuyển hướng lại trang chi tiết bài thi
        return redirect(url_for('showexam', exam_id=exam_id))

    except Exception as e:
        print("Error in unfavorite_exam route:", e)
        print("Đã xảy ra lỗi. Vui lòng thử lại.", "error")
        return redirect(url_for('showexam', exam_id=exam_id))

@app.route('/favorite_exam/<int:exam_id>', methods=['POST'])
def favorite_exam(exam_id):
    """
    Route để xử lý yêu cầu thêm bài thi vào danh sách "Yêu thích".
    """
    try:
        # Lấy user_id từ session (hoặc thông qua request)
        user_id = session.get('user')  # Giả định user_id được lưu trong session
        
        
        if user_id == None:
            return redirect('/login')  # Chuyển hướng nếu người dùng chưa đăng nhập
        print(user_id, exam_id)
        success = update_is_favorite(user_id, exam_id, 1)
        if success:
            print("Bài thi đã được thêm vào danh sách yêu thích.")
        else:
            print("Đã xảy ra lỗi khi thêm bài thi vào danh sách yêu thích.")
        
        # Quay lại trang hiện tại sau khi xử lý
        return redirect(url_for('showexam', exam_id=exam_id))
    
    except Exception as e:
        print("Error in favorite_exam route:", e)
        print("Đã xảy ra lỗi. Vui lòng thử lại.")
        return redirect(url_for('showexam', exam_id=exam_id))

@app.route("/admin/add-exam", methods=["GET", "POST"])
def add_exam():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))

    type_exam = request.form.get("typeExam")
    class_name = request.form.get("class")
    name = request.form.get("name")
    correct_multiple_choice = request.form.get("multipleChoice")
    correct_true_false = request.form.get("trueFalse")
    correct_short_answer = request.form.get("shortAnswer")
    exam_content = request.form.get("examContent")
    print(correct_multiple_choice, correct_true_false, correct_short_answer)
    if request.method == "POST":

        questions = read_exam(exam_content)
        for q in questions:
            if q == []:
                return render_template(
                "admin/add-exam.html",
                success=False,
                type_exam=type_exam,
                class_name=class_name,
                name=name,
                correct_multiple_choice=correct_multiple_choice,
                correct_true_false=correct_true_false,
                correct_short_answer=correct_short_answer,
                exam_content=exam_content,
                success_add=False
            )

        multiple_choice_questions = list(zip(questions[0], questions[1]))
        true_false_questions = list(zip(questions[2], questions[3]))
        short_questions = questions[4]
        # Chuẩn bị dữ liệu để hiển thị
        data = {
            "multiple_choice_questions": multiple_choice_questions,
            "true_false_questions": true_false_questions,
            "short_questions": short_questions,
        }

        # Gửi lại dữ liệu nhập vào form
        return render_template(
            "admin/add-exam.html",
            success=True,
            data=data,
            type_exam=type_exam,
            class_name=class_name,
            name=name,
            correct_multiple_choice=correct_multiple_choice,
            correct_true_false=correct_true_false,
            correct_short_answer=correct_short_answer,
            exam_content=exam_content,
            success_add=True,
            user1=user1,
            user=user,
        )
    # print(correct_true_false)
    if correct_true_false == None:
        correct_true_false = 'a) b) c) d) - a) b) c) d) - a) b) c) d) - a) b) c) d)'

    return render_template(
            "admin/add-exam.html",
            success=False,
            type_exam=type_exam,
            class_name=class_name,
            name=name,
            correct_multiple_choice=correct_multiple_choice,
            correct_true_false=correct_true_false,
            correct_short_answer=correct_short_answer,
            exam_content=exam_content,
            user1=user1,
            user=user,
        )

@app.route('/Add_Exam')
def addexam():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    # Lấy dữ liệu từ query string
    type_exam = request.args.get("type_exam")
    class_name = request.args.get("class_name")
    name = request.args.get("name")
    correct_multiple_choice = request.args.get("correct_multiple_choice")
    correct_true_false = request.args.get("correct_true_false")
    correct_short_answer = request.args.get("correct_short_answer")
    exam_content = request.args.get("exam_content")

    if classify_questions(type_exam, class_name, name, correct_multiple_choice, correct_true_false, correct_short_answer, exam_content):
        return render_template("admin/add-exam.html", success=False, success_add=True, user1=user1, user=user,)
    else :
        return render_template(
            "admin/add-exam.html",
            success=False,
            type_exam=type_exam,
            class_name=class_name,
            name=name,
            correct_multiple_choice=correct_multiple_choice,
            correct_true_false=correct_true_false,
            correct_short_answer=correct_short_answer,
            exam_content=exam_content,
            success_add=False,
            user1=user1,
            user=user,
        )

@app.route('/delete-question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    # Gọi hàm xóa câu hỏi
    if session.get('user') == None:
        return redirect('/')
    if delete_question_by_id(question_id):
        print('Xóa câu hỏi thành công!', )
    else:
        print('Xóa câu hỏi thất bại!',) 
    page = request.args.get('page')
    return redirect(url_for('manage_questions', page=page))

def allowed_file_question(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit-question', methods=['POST'])
def edit_question():
    if session.get('user') == None:
        return redirect('/')
    question_id = request.form.get('question_id')
    content = request.form.get('content')
    question_type = request.form.get('question_type')
    answer_options = request.form.get('answer_options')
    difficulty = request.form.get('difficulty')
    chapter = request.form.get('chapter')
    class_ = request.form.get('Class')
    correct_answer = request.form.get('correct_answer')

    solution = request.form.get('solution')
    
    illustration = request.files.get('illustration')
    file_path = None
    print(illustration)
    print("Received files:", request.files)  # Debug

    if illustration and allowed_file_question(illustration.filename):
    # Sử dụng question_id làm tên file, giữ nguyên phần mở rộng
        extension = illustration.filename.rsplit('.', 1)[1].lower()
        filename = f"{question_id}.{extension}"  # Đặt tên file là question_id
        file_path = os.path.join(app.config['UPLOAD_FOLDER_QUESTION'], filename)
        add_image_path_to_question(question_id)
        try:
            illustration.save(file_path)
            print(f"File saved successfully at {file_path}")  # Debug
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("No valid file uploaded or file type not allowed.")
    update_question(
        question_id=question_id,
        content=content,
        question_type=question_type,
        answer_options=answer_options,
        difficulty=difficulty,
        chapter=chapter,
        Class=class_,
        correct_answer=correct_answer,
        solution=solution,
    )

    # Quay lại trang quản lý câu hỏi
    page = request.form.get('page', 1, type=int)
    
    # Quay lại trang quản lý câu hỏi với trang hiện tại
    return redirect(url_for('manage_questions', page=page))

@app.route('/admin/manage-questions', methods=['GET', 'POST'])
def manage_questions():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    per_page = 10  # Số lượng câu hỏi trên mỗi trang

    cs = request.form.get('cs', '').lower() == 'true'
    if not cs:
        if request.method == 'POST':
            session['search_keyword'] = request.form.get('search_keyword')
            if session['search_keyword']:
                # Nếu tìm kiếm, xóa các bộ lọc
                session['question_type'] = None
                session['difficulty'] = None
                session['chapter'] = None
                session['Class'] = None
            else:
                # Nếu không tìm kiếm, cập nhật các bộ lọc
                session['question_type'] = request.form.get('question_type', session.get('question_type', None))
                session['difficulty'] = request.form.get('difficulty', session.get('difficulty', None))
                session['chapter'] = request.form.get('chapter', session.get('chapter', None))
                session['Class'] = request.form.get('Class', session.get('Class', None))
    
    # Lấy bộ lọc và từ khóa tìm kiếm từ session
    question_type_filter = session.get('question_type', None)
    difficulty_filter = session.get('difficulty', None)
    chapter_filter = session.get('chapter', None)
    class_filter = session.get('Class', None)
    search_keyword = session.get('search_keyword')

    # Trang hiện tại
    page = request.args.get('page', 1, type=int)

    # Lấy danh sách câu hỏi từ cơ sở dữ liệu
    questions = get_all_questions()
    questions.reverse()

    # Áp dụng tìm kiếm
    if search_keyword:
        try:
            search_keyword = int(search_keyword)  # Kiểm tra nếu search_keyword là số
            questions = [q for q in questions if search_keyword == q['question_id']]
        except ValueError:
            questions = [q for q in questions if search_keyword.lower() in (q['content'] or '').lower()]
    else:
        # Áp dụng các bộ lọc
        if question_type_filter:
            questions = [q for q in questions if q['question_type'] == question_type_filter]
        if difficulty_filter:
            questions = [q for q in questions if q['difficulty'] == difficulty_filter]
        if chapter_filter:
            questions = [q for q in questions if q['chapter'] == chapter_filter]
        if class_filter:
            questions = [q for q in questions if q['Class'] == class_filter]

    # Phân trang
    start = (page - 1) * per_page
    end = start + per_page
    paginated_questions = questions[start:end]

    # Tính tổng số trang
    total_pages = (len(questions) + per_page - 1) // per_page

    # Xử lý nút "Chỉnh sửa"
    cs = request.form.get('cs', '').lower() == 'true'
    if cs:
        question_id = request.form.get('question_id')
        question_to_edit = get_question_by_id(question_id)

        # Render với trạng thái tìm kiếm hoặc lọc được giữ nguyên
        return render_template(
            'admin/manage_questions.html',
            questions=paginated_questions,
            page=page,
            total_pages=total_pages,
            question_type_filter=question_type_filter,
            difficulty_filter=difficulty_filter,
            chapter_filter=chapter_filter,
            class_filter=class_filter,
            search_keyword=search_keyword,
            chinhsua=question_to_edit,
            user = user,
            user1=user1,
        )

    # Render danh sách câu hỏi
    return render_template(
        'admin/manage_questions.html',
        questions=paginated_questions,
        page=page,
        total_pages=total_pages,
        question_type_filter=question_type_filter,
        difficulty_filter=difficulty_filter,
        chapter_filter=chapter_filter,
        class_filter=class_filter,
        search_keyword=search_keyword,
        user = user,
        user1=user1,
    )

# ---------------------------
@app.route('/delete-exam/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    if session.get('user') == None:
        return redirect('/')
    # Gọi hàm xóa câu hỏi
    if delete_exam_by_id(exam_id):
        print('Xóa câu hỏi thành công!')
    else:
        print('Xóa câu hỏi thất bại!')
    page = request.args.get('page')
    return redirect(url_for('manage_exams', page=page))

@app.route('/edit-exam', methods=['POST'])
def edit_exam():
    exam_id = request.form.get('exam_id')
    name = request.form.get('name')
    exam_type = request.form.get('exam_type')
    class_ = request.form.get('Class')
    list_cau_hoi = request.form.get('List_questions')
    duration = request.form.get('duration')
    chapter = request.form.get('chapter')
    update_Exam_Question(exam_id, list_cau_hoi)
    # Cập nhật dữ liệu trong cơ sở dữ liệu
    update_exam(
        exam_id=exam_id,
        name=name,
        exam_type=exam_type,
        Class=class_,
        duration=duration,
        chapter=chapter,
    )

    # Quay lại trang quản lý câu hỏi
    return redirect(url_for('manage_exams'))

@app.route('/admin/manage_exams', methods=['GET', 'POST'])
def manage_exams():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    per_page = 10  # Số lượng câu hỏi trên mỗi trang

    cs = request.form.get('cs', '').lower() == 'true'
    if not cs:
        if request.method == 'POST':
            session['search_keyword'] = request.form.get('search_keyword')
            if session['search_keyword']:
                # Nếu tìm kiếm, xóa các bộ lọc
                session['exam_type'] = None
                session['Class'] = None
            else:
                # Nếu không tìm kiếm, cập nhật các bộ lọc
                session['exam_type'] = request.form.get('exam_type', session.get('exam_type', None))
                session['Class'] = request.form.get('Class', session.get('Class', None))
    
    # Lấy bộ lọc và từ khóa tìm kiếm từ session
    exam_type_filter = session.get('exam_type', None)
    class_filter = session.get('Class', None)
    search_keyword = session.get('search_keyword')

    # Trang hiện tại
    page = request.args.get('page', 1, type=int)

    # Lấy danh sách câu hỏi từ cơ sở dữ liệu
    exams = get_all_exams()
    exams.reverse()
    for exam in exams:
        exam['List_cau_hoi'] = get_question_ids_by_exam(exam['exam_id'])

    # Áp dụng tìm kiếm
    if search_keyword:
        try:
            search_keyword = int(search_keyword)  # Kiểm tra nếu search_keyword là số
            exams = [q for q in exams if search_keyword == q['exam_id']]
        except ValueError:
            exams = [q for q in exams if search_keyword.lower() in (q['exam_id'] or '').lower()]
    else:
        # Áp dụng các bộ lọc
        if exam_type_filter:
            exams = [q for q in exams if q['exam_type'] == exam_type_filter]
        if class_filter:
            exams = [q for q in exams if str(q['Class']) == class_filter]

    # Phân trang
    start = (page - 1) * per_page
    end = start + per_page
    paginated_exams = exams[start:end]

    # Tính tổng số trang
    total_pages = (len(exams) + per_page - 1) // per_page

    # Xử lý nút "Chỉnh sửa"
    cs = request.form.get('cs', '').lower() == 'true'
    if cs:
        exam_id = request.form.get('exam_id')
        exam_to_edit = get_exam_by_id(exam_id)
        exam_to_edit['List_cau_hoi'] = get_question_ids_by_exam(exam_to_edit['exam_id'])

        # Render với trạng thái tìm kiếm hoặc lọc được giữ nguyên
        return render_template(
            'admin/manage_exams.html',
            exams=paginated_exams,
            page=page,
            total_pages=total_pages,
            exam_type_filter=exam_type_filter,
            class_filter=class_filter,
            search_keyword=search_keyword,
            chinhsua=exam_to_edit,
            user = user,
            user1=user1,
        )

    # Render danh sách câu hỏi
    return render_template(
        'admin/manage_exams.html',
        exams=paginated_exams,
        page=page,
        total_pages=total_pages,
        exam_type_filter=exam_type_filter,
        class_filter=class_filter,
        search_keyword=search_keyword,
        user = user,
        user1=user1,
    )

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('user') == None:
        return redirect('/')
    # Gọi hàm xóa câu hỏi
    if delete_user_by_id(user_id):
        print('Xóa câu hỏi thành công!')
    else:
        print('Xóa câu hỏi thất bại!')
    page = request.args.get('page')
    return redirect(url_for('manage_users', page=page))

@app.route('/edit-user', methods=['POST'])
def edit_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    age = request.form.get('age')
    Class = request.form.get('Class')
    type_user = request.form.get('type_user')
    avatar_path = request.form.get('avatar_path')
    coins = request.form.get('coins')
    update_user(
        user_id=user_id,
        username=username,
        password=password,
        name=name,
        age=age,
        Class=Class,
        type_user=type_user,
        avatar_path=avatar_path,
        coins=coins,
    )

    # Quay lại trang quản lý câu hỏi
    return redirect(url_for('manage_users'))

@app.route('/admin/manage_users', methods=['GET', 'POST'])
def manage_users():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    per_page = 10  # Số lượng câu hỏi trên mỗi trang

    cs = request.form.get('cs', '').lower() == 'true'
    if not cs:
        if request.method == 'POST':
            session['search_keyword'] = request.form.get('search_keyword')
            if session['search_keyword']:
                # Nếu tìm kiếm, xóa các bộ lọc
                session['user_type'] = None
                session['Class'] = None
            else:
                # Nếu không tìm kiếm, cập nhật các bộ lọc
                session['user_type'] = request.form.get('user_type', session.get('user_type', None))
                session['Class'] = request.form.get('Class', session.get('Class', None))
    
    # Lấy bộ lọc và từ khóa tìm kiếm từ session
    user_type_filter = session.get('user_type', None)
    class_filter = session.get('Class', None)
    search_keyword = session.get('search_keyword')

    # Trang hiện tại
    

    # Lấy danh sách câu hỏi từ cơ sở dữ liệu
    users = get_all_users()

    # Áp dụng tìm kiếm
    if search_keyword:
        try:
            search_keyword = int(search_keyword)  # Kiểm tra nếu search_keyword là số
            users = [q for q in users if search_keyword == q['user_id']]
        except ValueError:
            users = [q for q in users if search_keyword.lower() in (q['user_id'] or '').lower()]
    else:
        # Áp dụng các bộ lọc
        if user_type_filter:
            users = [q for q in users if q['type_user'] == user_type_filter]
        if class_filter:
            users = [q for q in users if str(q['Class']) == class_filter]

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]

    # Tính tổng số trang
    total_pages = (len(users) + per_page - 1) // per_page

    # Xử lý nút "Chỉnh sửa"
    cs = request.form.get('cs', '').lower() == 'true'
    if cs:
        user_id = request.form.get('user_id')
        user_to_edit = get_user_by_id(user_id)
        # Render với trạng thái tìm kiếm hoặc lọc được giữ nguyên
        return render_template(
            'admin/manage_users.html',
            users=paginated_users,
            page=page,
            total_pages=total_pages,
            user_type_filter=user_type_filter,
            class_filter=class_filter,
            search_keyword=search_keyword,
            chinhsua=user_to_edit,
            user = user,
            user1=user1,
        )

    # Render danh sách câu hỏi
    return render_template(
        'admin/manage_users.html',
        users=paginated_users,
        page=page,
        total_pages=total_pages,
        user_type_filter=user_type_filter,
        class_filter=class_filter,
        search_keyword=search_keyword,
        user = user,
        user1=user1,
    )


@app.route('/delete-report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if session.get('user') == None:
        return redirect('/')
    # Gọi hàm xóa câu hỏi
    if delete_report_by_id(report_id):
        print('Xóa câu hỏi thành công!')
    else:
        print('Xóa câu hỏi thất bại!')
    page = request.args.get('page')
    return redirect(url_for('manage_reports', page=page))

@app.route('/admin/manage_reports', methods=['GET', 'POST'])
def manage_reports():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    per_page = 10  # Số lượng câu hỏi trên mỗi trang

    cs = request.form.get('cs', '').lower() == 'true'
    if not cs:
        if request.method == 'POST':
            session['search_keyword'] = request.form.get('search_keyword')
            if session['search_keyword']:
                # Nếu tìm kiếm, xóa các bộ lọc
                session['error_type'] = None
            else:
                # Nếu không tìm kiếm, cập nhật các bộ lọc
                session['error_type'] = request.form.get('error_type', session.get('error_type', None))
    
    # Lấy bộ lọc và từ khóa tìm kiếm từ session
    error_type_filter = session.get('user_type', None)
    search_keyword = session.get('search_keyword')

    # Trang hiện tại
    

    # Lấy danh sách câu hỏi từ cơ sở dữ liệu
    reports = get_all_reports()

    # Áp dụng tìm kiếm
    if search_keyword:
        try:
            search_keyword = int(search_keyword)  # Kiểm tra nếu search_keyword là số
            reports = [q for q in reports if search_keyword == q['report_id']]
        except ValueError:
            reports = [q for q in reports if search_keyword.lower() in (q['report_id'] or '').lower()]
    else:
        # Áp dụng các bộ lọc
        if error_type_filter:
            reports = [q for q in reports if q['error_type'] == error_type_filter]

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_reports = reports[start:end]

    # Tính tổng số trang
    total_pages = (len(reports) + per_page - 1) // per_page

    # Xử lý nút "Chỉnh sửa"
    cs = request.form.get('cs', '').lower() == 'true'
    if cs:
        report_id = request.form.get('report_id')
        report_to_edit = get_user_by_id(report_id)
        # Render với trạng thái tìm kiếm hoặc lọc được giữ nguyên
        return render_template(
            'admin/manage_users.html',
            reports=paginated_reports,
            page=page,
            total_pages=total_pages,
            error_type_filter=error_type_filter,
            search_keyword=search_keyword,
            chinhsua=report_to_edit,
            user = user,
            user1=user1,
        )

    # Render danh sách câu hỏi
    return render_template(
        'admin/manage_reports.html',
        reports=paginated_reports,
        page=page,
        total_pages=total_pages,
        report_type_filter=error_type_filter,
        search_keyword=search_keyword,
        user = user,
        user1=user1,
    )

@app.route('/admin/add-question')
def form():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]
    if user1['type_user'] != 'admin':
        return redirect(url_for('home'))
    return render_template('admin/add-question.html', user1=user1, user=user) 

@app.route('/admin/submit-question', methods=['POST'])
def submit_question():
    if session.get('user') == None:
        return redirect('/')
    try:
        content = request.form['content']
        type_question = request.form['type_question']
        answer_options = request.form.get('answer_options', '')
        print(answer_options)
        dap_an = ""
        if answer_options != '':
            answer_options = answer_options.split('\n')  # Tách đáp án thành danh sách
            print("Danh sách đáp án sau khi tách:", answer_options)
            
            if type_question == "Trac nghiem":
                x = 0
                while x < len(answer_options):
                    line = answer_options[x].strip()  # Loại bỏ khoảng trắng thừa
                    
                    # Bỏ qua các dòng trống
                    if line == "":
                        x += 1
                        continue
                    
                    # Kiểm tra đáp án bắt đầu bằng A., B., C., hoặc D.
                    if line.startswith("A."):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("B."):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("C."):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("D."):
                        dap_an += "--" + line[2:].strip()
                    else:
                        # Xử lý trường hợp dòng không khớp
                        print(f"Dòng không khớp với định dạng: {line}")
                        dap_an += " " + line

                    x += 1
                    
            elif type_question == "Dung sai":
                x = 0
                while x < len(answer_options):
                    line = answer_options[x].strip()  # Loại bỏ khoảng trắng thừa
                    
                    # Bỏ qua các dòng trống
                    if line == "":
                        x += 1
                        continue
                    
                    # Kiểm tra đáp án bắt đầu bằng A., B., C., hoặc D.
                    if line.startswith("a)"):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("b)"):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("c)"):
                        dap_an += "--" + line[2:].strip()
                    elif line.startswith("d)"):
                        dap_an += "--" + line[2:].strip()
                    else:

                        print(f"Dòng không khớp với định dạng: {line}")
                        dap_an += " " + line

                    x += 1
        print(dap_an)
        solution = request.form['solution']
        correct_answer = request.form['correct_answer']
        chapter = request.form['chapter']
        difficulty = request.form['difficulty']
        Class = request.form['Class']
        question_id = add_question1(type_question, content, dap_an, correct_answer, difficulty, chapter, Class, solution)

        illustration = request.files.get('illustration')
        file_path = None

        print("Received files:", request.files)  # Debug

        if illustration and allowed_file_question(illustration.filename):
        # Sử dụng question_id làm tên file, giữ nguyên phần mở rộng
            extension = illustration.filename.rsplit('.', 1)[1].lower()
            filename = f"{question_id}.{extension}"  # Đặt tên file là question_id
            file_path = os.path.join(app.config['UPLOAD_FOLDER_QUESTION'], filename)
            add_image_path_to_question(question_id)
            try:
                illustration.save(file_path)
                print(f"File saved successfully at {file_path}")  # Debug
            except Exception as e:
                print(f"Error saving file: {e}")
        else:
            print("No valid file uploaded or file type not allowed.")
        
        # Trả về kết quả
        flash("Thêm câu hỏi thành công!", "success")
        return redirect(url_for('form'))
    except Exception as e:
        flash("Có lỗi xảy ra khi thêm câu hỏi!", "danger")
        print(e)
        return redirect(url_for('form'))

@app.route('/generate-exam', methods=['POST'])
def generate_exam():
    user_id = session.get('user')
    update_user_coins(user_id)

    exam_name = request.form.get('examName')  # Tên đề thi
    exam_class = request.form.get('class')   # Lớp
    exam_type = request.form.get('examType') # Loại đề thi
    difficulty = request.form.get('difficulty')  # Độ khó
    time = request.form.get('time')
    if time == 'None' : time = None  # Thời gian
    chapter = request.form.get('chapter')  # Chương (có thể là None)
    table_data = request.form.get('tableData')
    table_data = json.loads(table_data)

    filtered_table_data = []
    for row in table_data:
        filtered_values = [
            value for value in row['values'] if int(value['value']) > 0
        ]
        if filtered_values:
            filtered_table_data.append({
                'rowIndex': row['rowIndex'],
                'noiDung': row['noiDung'],
                'capDo': row['capDo'],
                'values': filtered_values
            })
    exam_id = add_exam1(exam_type=exam_type, name=exam_name, Class=exam_class, chapter=chapter, duration=time)
    if exam_id == None:
        return jsonify({"status": "error", "message": "NO EXAM"}), 400

    for data in filtered_table_data:
        for value in data['values']:
            capDo = value['capDo'].split(" - ")
            TN = 0
            DS = 0
            TLN = 0
            difficulty = ""
            if capDo[0].startswith("Phần I"):
                TN = int(value['value'])
            elif capDo[0].startswith("Phần II"):
                DS = int(value['value']) / 4
            elif capDo[0].startswith("Phần III"):
                TLN = int(value['value'])
            if capDo[1] == "Nhận biết":
                difficulty = "NB"
            elif capDo[1] == "Thông hiểu":
                difficulty = "TH"
            elif capDo[1] == "Vận dụng":
                difficulty = "VD"
            elif capDo[1] == "Vận dụng cao":
                difficulty = "VDC"
            print(data['noiDung'], difficulty, TN, DS, TLN)
            if data['noiDung']:
                ids = get_random_questions_by_chapter(chapter=data['noiDung'], difficulty=difficulty, num_trac_nghiem=TN, num_dung_sai=DS, num_ngan=TLN)
                if not add_questions_to_exam(exam_id=exam_id, question_ids=ids):
                    return jsonify({"status": "error", "message": "Can't add questions to exam"}), 400
            
    own_exam(user_id=user_id, exam_id=exam_id, created_by_user=1)

    # Redirect hoặc hiển thị thông báo thành công
    return jsonify({"status": "success", "message": "Exam created successfully!"})


@app.route('/search_question', methods=['POST'])
def search_question():
    user_id = session.get('user')
    user1 = find_user_by_id(user_id)
    user = user1["name"]

    question_id = request.form.get('search_query')

    question = get_question_by_id(question_id)

    if (question == None): return redirect('/')
    if question['question_type'] != "Ngan":
        question['answer_options'] = [
        option.strip() for option in question['answer_options'].split('--') if option.strip()]
    if question['question_type'] == 'Trac nghiem':
        question['answer_options'] = [
            f"{chr(65 + i)}. {option}" for i, option in enumerate(question['answer_options'])
        ] 
    elif question['question_type'] == 'Dung sai':
        question['answer_options'] = [
            f"{chr(97 + i)}) {option}" for i, option in enumerate(question['answer_options'])
        ]
    

    return render_template(
        'question_details.html',
        question=question,
        user=user,
        user1=user1,
        is_document = False,
        is_assignments = False,
        is_createdexam = False,
        is_wiki = False,
    )

@app.route('/ranking')
def ranking():
    user_id = session.get('user')
    user1 = find_user_by_id(user_id)
    user = user1["name"]
    exam_id = request.args.get('exam_id')
    exam = get_exam_by_id(exam_id)
    students = get_user_exam_summary_with_duration_by_exam_id(exam_id)
    students = [student for student in students if student['duration'] != "N/A"]
    students = sorted(
        students,
        key=lambda x: (
            -x['score'],  # Điểm giảm dần
            int(x['duration'].split('phút')[0]) * 60 + int(x['duration'].split('phút')[1].split('giây')[0])  # Thời gian tăng dần
        )
    )

    per_page = 10
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_students = students[start:end]

    # Tính tổng số trang
    total_pages = (len(students) + per_page - 1) // per_page

    # Sắp xếp học sinh theo điểm số giảm dần
    

    return render_template('ranking.html', page= page, exam_id=exam_id, exam_name=exam['name'], students=paginated_students, user=user, user1=user1, total_pages=total_pages,)



@app.route('/log_event', methods=['POST'])
def log_event():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received'}), 400

    username = data.get('username', 'Anonymous')
    action = data.get('action', 'Unknown Action')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    log_entry = {
        'username': username,
        'action': action,
        'timestamp': timestamp
    }

    # Lưu log vào danh sách tạm
    
    exam_id = request.args.get('exam_id')
    summary_id = session[str(exam_id)]
    summary_id = str(summary_id)

    if summary_id not in logs:
        logs[summary_id] = []  # Tạo danh sách mới nếu chưa tồn tại

    logs[summary_id].append(log_entry)

    print(f"Log received: {log_entry}")  # Ghi log vào console (hoặc ghi vào file/database)

    return jsonify({'message': 'Log ghi thành công', 'log': log_entry}), 200

@app.route('/log-tracker')
def lock():
    return render_template('logtracker.html')

def split_questions(content):
    cau_hoi_trac_nghiem = []
    dap_an_trac_nghiem = []
    x = 0
    cau = False
    content = content.split("\n")
    
    while x < len(content):
        if content[x] == "":
            x += 1
            continue
        if content[x].startswith("Câu"):
            question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
            cau_hoi_trac_nghiem.append(question.strip())
            dap_an_trac_nghiem.append("")
            cau = True
            x += 1
            continue
        if content[x].startswith("A.") or content[x].startswith("B.") or content[x].startswith("C.") or content[x].startswith("D."):
            dap_an_trac_nghiem[-1] += "--" + content[x][2:].strip()
            cau = False
        if cau:
            cau_hoi_trac_nghiem[-1] += " " + content[x].strip()
        x += 1

    result = []
    for i, question in enumerate(cau_hoi_trac_nghiem):
        answers = dap_an_trac_nghiem[i].split("--")[1:]  # Bỏ phần tử rỗng đầu tiên
        result.append({
            'question': question,
            'answers': answers
        })
        print(result)
    return result

# API xử lý yêu cầu từ frontend
@app.route('/parse_questions', methods=['POST'])
def parse_questions_endpoint():
    data = request.json
    content = data.get('content', '')

    if not content:
        return jsonify({'error': 'Nội dung trống!'}), 400

    questions = split_questions(content)
    return jsonify({'questions': questions})



@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    if request.is_json:
        data = request.get_json()  # Lấy dữ liệu JSON từ request
        print("Dữ liệu nhận được:", data)  # Kiểm tra dữ liệu nhận được
        
        # Gọi hàm xử lý dữ liệu
        try:
            processed_data, status = validate_and_process_data(data)
            if status != 200:
                return jsonify(processed_data), status  # Trả về lỗi nếu dữ liệu không hợp lệ
            
            # TODO: Lưu dữ liệu đã xử lý vào cơ sở dữ liệu hoặc thực hiện các thao tác cần thiết
            print("Dữ liệu đã xử lý:", processed_data)

            return jsonify({
                "status": "success",
                "message": "Dữ liệu đã được xử lý thành công!",
                "processed_data": processed_data
            }), 200
        except Exception as e:
            return jsonify({"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}), 500
    else:
        return jsonify({"error": "Request content-type must be application/json"}), 415

@app.route('/wiki')
def wiki():
    if session.get('user') == None:
        return redirect('/')
    user1 = find_user_by_id(session.get('user'))
    user = user1["name"]

    return render_template('wiki.html', user=user, user1=user1, is_wiki=True, is_document = False,
        is_assignments = False,
        is_createdexam = False,)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



