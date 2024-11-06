import pyodbc

server = 'MINHDUCK\SQLEXPRESS'   # Server name từ ảnh
database = 'MYDB'                # Tên cơ sở dữ liệu
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'


def add_users(username, password, name, age, class_, school):
    try:
        # Mở kết nối khi gọi hàm
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Users")
                result = cursor.fetchone()
            
                cursor.execute("""
                    INSERT INTO Users (user_id, username, password, name, age, Class, school)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (result[0] + 1, username, password, name, int(age), int(class_), school))
                conn.commit()
            print("Data inserted into Users table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Users table:", e)
        return False

def check(username):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn kiểm tra username có tồn tại trong bảng Users
                cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", (username,))
                result = cursor.fetchone()

                # Nếu COUNT > 0, tức là username đã tồn tại
                if result[0] > 0:
                    print(f"Tên đăng nhập '{username}' đã tồn tại.")
                    return True
                else:
                    print(f"Tên đăng nhập '{username}' chưa tồn tại.")
                    return False
    except Exception as e:
        print("Lỗi khi kiểm tra tên đăng nhập:", e)
        return False


def check_login_credentials(username, password):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn kiểm tra username và password trong bảng Users
                cursor.execute("""
                    SELECT COUNT(*) FROM Users
                    WHERE username = ? AND password = ?
                """, (username, password))
                
                result = cursor.fetchone()

                # Nếu COUNT > 0, tức là username và password đã khớp
                if result[0] > 0:
                    print("Thông tin đăng nhập hợp lệ.")
                    return True
                else:
                    print("Tên đăng nhập hoặc mật khẩu không đúng.")
                    return False
    except Exception as e:
        print("Lỗi khi kiểm tra thông tin đăng nhập:", e)
        return False



# Hàm thêm bài thi
def add_exam(name, exam_type, Class):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT COUNT(*) FROM Exams")
                result = cursor.fetchone()

                cursor.execute("""
                    INSERT INTO Exams (exam_id, name, exam_type, Class)
                    VALUES (?, ?, ?, ?)
                """, (result[0] + 1, name, exam_type, int(Class)))
                conn.commit()
            print("Data inserted into Exams table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Exams table:", e)
        return False

# Hàm thêm câu hỏi
def add_question(question_id, question_type, content, answer_options, correct_answer, difficulty):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Questions (question_id, question_type, content, answer_options, correct_answer, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (question_id, question_type, content, answer_options, correct_answer, difficulty))
                conn.commit()
            print("Data inserted into Questions table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Questions table:", e)
        return False

# Các hàm khác cũng được sửa tương tự
def own_exam(user_id, exam_id, score):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO User_Exam (user_id, exam_id, completed, score)
                    VALUES (?, ?, ?, ?)
                """, (user_id, exam_id, 0, score)) 
                conn.commit()
            print("Data inserted into User_Exam table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into User_Exam table:", e)
        return False

# Hàm thêm câu hỏi vào bài thi
def add_question_to_exam(exam_id, question_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Exam_Question (exam_id, question_id)
                    VALUES (?, ?)
                """, (exam_id, question_id))
                conn.commit()
            print("Data inserted into Exam_Question table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Exam_Question table:", e)
        return False

# Hàm ghi câu trả lời của người dùng cho câu hỏi
def User_does_Answers(user_id, exam_id, question_id, user_answer, is_correct):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO User_Answers (user_id, exam_id, question_id, user_answer, is_correct)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, exam_id, question_id, user_answer, is_correct))
                conn.commit()
            print("Data inserted into User_Answers table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into User_Answers table:", e)
        return False

def Done_exam(user_id, exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Cập nhật thuộc tính completed cho bản ghi trong bảng User_Exam
                cursor.execute("""
                    UPDATE User_Exam
                    SET completed = ?
                    WHERE user_id = ? AND exam_id = ?
                """, (1, user_id, exam_id))
                conn.commit()
                
            print("Updated completed status in User_Exam table successfully.")
            return True
    except Exception as e:
        print("Error updating completed status in User_Exam table:", e)
        return False

def get_all_users():
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn tất cả các bản ghi trong bảng Users
                cursor.execute("SELECT * FROM Users")
                users = cursor.fetchall()

                if not users:
                    print("Không có người dùng nào trong hệ thống.")
                    return

                print("Danh sách người dùng:")
                for user in users:
                    print("\nID người dùng:", user.user_id)
                    print("Tên đăng nhập:", user.username)
                    print("Mật khẩu:", user.password)  # Chỉ hiển thị nếu cần thiết
                    print("Họ và tên:", user.name)
                    print("Tuổi:", user.age)
                    print("Lớp:", user.Class)
                    print("Trường:", user.school)
    except Exception as e:
        print("Lỗi khi truy vấn danh sách người dùng:", e)

def get_questions_in_exam(exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn các question_id của bài thi từ bảng Exam_Question
                cursor.execute("SELECT question_id FROM Exam_Question WHERE exam_id = ?", (exam_id,))
                question_ids = cursor.fetchall()

                if not question_ids:
                    print("Không có câu hỏi nào trong bài thi với ID đã cho.")
                    return

                print(f"Các câu hỏi trong bài thi ID {exam_id}:")

                # Lặp qua các question_id để lấy thông tin chi tiết từ bảng Questions
                for question_id_tuple in question_ids:
                    question_id = question_id_tuple[0]
                    cursor.execute("SELECT * FROM Questions WHERE question_id = ?", (question_id,))
                    question = cursor.fetchone()

                    if question:
                        print("\nID câu hỏi:", question.question_id)
                        print("Loại câu hỏi:", question.question_type)
                        print("Nội dung:", question.content)
                        print("Các đáp án:", question.answer_options)
                        print("Đáp án đúng:", question.correct_answer)
                        print("Độ khó:", question.difficulty)
                    else:
                        print(f"Không tìm thấy câu hỏi với ID {question_id}.")
    except Exception as e:
        print("Lỗi khi truy vấn các câu hỏi của bài thi:", e)

def get_all_exams():
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn tất cả các bản ghi trong bảng Exams
                cursor.execute("SELECT * FROM Exams")
                exams = cursor.fetchall()

                if not exams:
                    print("Không có bài thi nào trong hệ thống.")
                    return

                print("Danh sách bài thi:")
                for exam in exams:
                    print("\nID bài thi:", exam.exam_id)
                    print("Tên bài thi:", exam.name)
                    print("Loại bài thi:", exam.exam_type)
                    print("Lớp:", exam.Class)  # Nếu cột class tồn tại
    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)

def search_exams_by_types_and_class(exam_types=None, class_=None):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Khởi tạo câu truy vấn và danh sách tham số
                query = "SELECT * FROM Exams"
                conditions = []
                params = []

                # Thêm điều kiện exam_type nếu exam_types được cung cấp
                if exam_types:
                    placeholders = ', '.join(['?'] * len(exam_types))
                    conditions.append(f"exam_type IN ({placeholders})")
                    params.extend(exam_types)

                # Thêm điều kiện class nếu class_ được cung cấp
                if class_ is not None:
                    conditions.append("class = ?")
                    params.append(class_)

                # Nếu có điều kiện nào, thêm WHERE vào truy vấn
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                # Thực hiện truy vấn với các điều kiện
                cursor.execute(query, params)
                exams = cursor.fetchall()

                if not exams:
                    print(f"Không tìm thấy bài thi nào với các loại {exam_types} và lớp '{class_}' (nếu được cung cấp).")
                    return

                print(f"Danh sách các bài thi với các loại {exam_types} và lớp '{class_}' (nếu có):")
                for exam in exams:
                    print("\nID bài thi:", exam.exam_id)
                    print("Tên bài thi:", exam.name)
                    print("Loại bài thi:", exam.exam_type)
                    print("Lớp:", exam.Class)
    except Exception as e:
        print("Lỗi khi tìm kiếm các bài thi:", e)

def get_latest_exams(limit=10):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn để lấy 10 bài thi mới nhất theo upload_time
                cursor.execute("""
                    SELECT TOP (?) * FROM Exams
                    ORDER BY upload_time DESC
                """, (limit,))
                
                exams = cursor.fetchall()

                if not exams:
                    print("Không có bài thi nào trong hệ thống.")
                    return

                print(f"Danh sách {limit} bài thi mới nhất:")
                for exam in exams:
                    print("\nID bài thi:", exam.exam_id)
                    print("Tên bài thi:", exam.name)
                    print("Loại bài thi:", exam.exam_type)
                    print("Lớp:", exam.Class)
                    print("Thời gian tải lên:", exam.upload_time)
    except Exception as e:
        print("Lỗi khi truy vấn các bài thi mới nhất:", e)
