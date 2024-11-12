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



def add_exam1(name, exam_type, Class):
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
    except Exception as e:
        print("Error inserting data into Exams table:", e)
        return False

# add_exam1('ádfasdf', 'ádfadsf', 12)
# add_exam1('namasdfase', 'exam_typdfasdfe', 11)
# add_exam1('asdfasdf', 'asdfasdf', 12)
# add_exam1('naasdfame', 'asdfasdfasdf', 10)
# add_exam1('asdfasdfas', 'exaasdfasdfm_type', 13)

# Hàm thêm bài thi
def add_exam(name, exam_type, Class, questions):
    cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3 = questions
    n = len(cau_hoi_trac_nghiem) + len(cau_hoi_dung_sai) + len(cau_hoi_ngan)
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT COUNT(*) FROM Exams")
                result = cursor.fetchone()

                cursor.execute("""
                    INSERT INTO Exams (exam_id, name, exam_type, num_of_questions, Class)
                    VALUES (?, ?, ?, ?, ?)
                """, (result[0] + 1, name, exam_type, n, int(Class)))
                conn.commit()
            print("Data inserted into Exams table successfully.")
    except Exception as e:
        print("Error inserting data into Exams table:", e)
        return False
    
    cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3 = questions

    for i in range(len(cau_hoi_trac_nghiem)):
        add_question(result[0] + 1, "Trac nghiem", cau_hoi_trac_nghiem[i], dap_an_trac_nghiem[i], dapan1[i], Class)

    for i in range(len(cau_hoi_dung_sai)):
        dap_an = ""
        for x in range(4):
            dap_an += dapan2[i*4 + x] + " "
        add_question(result[0] + 1 , "Dung sai", cau_hoi_dung_sai[i], dap_an_dung_sai[i], dap_an, Class)
    for i in range(len(cau_hoi_ngan)):
        add_question(result[0] + 1 , "Ngan", cau_hoi_ngan[i], None, dapan3[i], Class)
    return True

# Hàm thêm câu hỏi
def add_question(exam_id, question_type, content, answer_options, correct_answer, Class, difficulty = "easy"):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT COUNT(*) FROM Questions")
                result = cursor.fetchone()
                cursor.execute("""
                    INSERT INTO Questions (question_id, question_type, content, answer_options, correct_answer, difficulty, Class)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (result[0] + 1, question_type, content, answer_options, correct_answer, difficulty, Class))
                conn.commit()
                add_question_to_exam(exam_id, result[0] + 1)
            print("Data inserted into Questions table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Questions table:", e)
        return False

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
    """
    Truy vấn các câu hỏi thuộc bài thi với ID tương ứng, phân loại theo dạng câu hỏi,
    và bao gồm cả đường dẫn hình ảnh nếu có.
    """
    cau_hoi_trac_nghiem = []
    dap_an_trac_nghiem = []
    cau_hoi_dung_sai = []
    dap_an_dung_sai = []
    cau_hoi_ngan = []
    dapan1 = []
    dapan2 = []
    dapan3 = []
    image_paths = []  # Danh sách lưu image_path tương ứng với câu hỏi

    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Lấy danh sách question_id từ bảng Exam_Question
                cursor.execute("SELECT question_id FROM Exam_Question WHERE exam_id = ?", (exam_id,))
                question_ids = cursor.fetchall()

                if not question_ids:
                    print(f"Không có câu hỏi nào trong bài thi với ID {exam_id}.")
                    return None

                print(f"Các câu hỏi trong bài thi ID {exam_id}:")

                # Lặp qua các question_id để lấy thông tin chi tiết từ bảng Questions
                for question_id_tuple in question_ids:
                    question_id = question_id_tuple[0]
                    cursor.execute("SELECT * FROM Questions WHERE question_id = ?", (question_id,))
                    question = cursor.fetchone()

                    if question:
                        # Lấy image_path nếu có
                        image_path = question.image_path if question.image_path else None
                        image_paths.append(image_path)

                        # Phân loại câu hỏi theo loại
                        if question.question_type == "Trac nghiem":
                            cau_hoi_trac_nghiem.append(question.content)
                            dap_an_trac_nghiem.append(question.answer_options)
                            dapan1.append(question.correct_answer)
                        elif question.question_type == "Dung sai":
                            cau_hoi_dung_sai.append(question.content)
                            dap_an_dung_sai.append(question.answer_options)
                            dapan2.append(question.correct_answer)
                        elif question.question_type == "Ngan":
                            cau_hoi_ngan.append(question.content)
                            dapan3.append(question.correct_answer)

    except Exception as e:
        print("Lỗi khi truy vấn các câu hỏi của bài thi:", e)
        return None

    return {
        "trac_nghiem": {"questions": cau_hoi_trac_nghiem, "answers": dap_an_trac_nghiem, "correct_answers": dapan1},
        "dung_sai": {"questions": cau_hoi_dung_sai, "answers": dap_an_dung_sai, "correct_answers": dapan2},
        "ngan": {"questions": cau_hoi_ngan, "correct_answers": dapan3},
        "image_paths": image_paths,  # Đường dẫn hình ảnh
    }

def get_all_exams():
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Truy vấn dữ liệu
                cursor.execute("SELECT exam_id, name, upload_time, exam_type, num_of_questions, Class FROM Exams")
                exams = cursor.fetchall()

                if not exams:
                    print("Không có bài thi nào trong hệ thống.")
                    return []

                # Chuyển đổi dữ liệu từ Row sang dictionary
                exam_list = []
                for exam in exams:
                    exam_list.append({
                        "exam_id": exam.exam_id,
                        "name": exam.name,
                        "upload_time": exam.upload_time.strftime('%d/%m/%Y %H:%M:%S'),
                        "exam_type": exam.exam_type,
                        "num_of_questions": exam.num_of_questions,
                        "class": exam.Class  # Chú ý sử dụng đúng tên cột
                    })

                return exam_list
    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)
        return []

def search_exams_by_types_and_class(exam_types=None, class_=None):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Khởi tạo câu truy vấn và danh sách tham số
                query = "SELECT exam_id, name, upload_time, exam_type, num_of_questions, Class FROM Exams"
                conditions = []
                params = []

                # Thêm điều kiện exam_type nếu có
                if exam_types:
                    placeholders = ', '.join(['?'] * len(exam_types))
                    conditions.append(f"exam_type IN ({placeholders})")
                    params.extend(exam_types)

                # Thêm điều kiện class nếu có
                if class_:
                    placeholders = ', '.join(['?'] * len(class_))
                    conditions.append(f"Class IN ({placeholders})")
                    params.extend(class_)

                # Thêm WHERE nếu có điều kiện
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                # Thực hiện truy vấn
                cursor.execute(query, params)
                exams = cursor.fetchall()

                # Chuyển đổi kết quả sang danh sách dictionary
                exam_list = []
                for exam in exams:
                    exam_list.append({
                        "exam_id": exam.exam_id,
                        "name": exam.name,
                        "upload_time": exam.upload_time.strftime('%d/%m/%Y %H:%M:%S'),
                        "exam_type": exam.exam_type,
                        "num_of_questions": exam.num_of_questions,
                        "class": exam.Class
                    })

                return exam_list
    except Exception as e:
        print("Lỗi khi tìm kiếm các bài thi:", e)
        return []
    

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


def get_exam_by_id(exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            # Sử dụng cursor để trả về dictionary
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exams WHERE exam_id = ?", (exam_id,))
            result = cursor.fetchone()
            
            if result:
                # Chuyển kết quả từ tuple sang dictionary
                columns = [column[0] for column in cursor.description]  # Lấy tên cột
                result_dict = dict(zip(columns, result))  # Map tên cột với giá trị
                return result_dict

            return None
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bài thi với ID {exam_id}: {e}")
        return None

def search_exam_by_name_case_insensitive(search_term):
    """
    Tìm kiếm bài thi theo tên trong bảng Exams (không phân biệt viết hoa hay viết thường).

    Args:
        search_term (str): Tên hoặc một phần tên bài thi cần tìm.

    Returns:
        list: Danh sách các bài thi phù hợp (mỗi bài thi là một dictionary).
    """
    try:
        # Kết nối với cơ sở dữ liệu
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Sử dụng LOWER() để tìm kiếm không phân biệt chữ hoa chữ thường
                query = """
                SELECT * 
                FROM Exams
                WHERE LOWER(name) LIKE LOWER(?)
                """
                # Thêm ký tự `%` trước và sau từ khóa tìm kiếm để tìm theo bất kỳ phần nào của tên
                cursor.execute(query, ('%' + search_term + '%',))
                results = cursor.fetchall()
                
                if results:
                    # Chuyển đổi kết quả từ tuple sang dictionary
                    columns = [column[0] for column in cursor.description]
                    exams = [dict(zip(columns, row)) for row in results]
                    return exams
                else:
                    print("Không tìm thấy bài thi nào phù hợp.")
                    return []
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bài thi theo tên: {e}")
        return []


def add_image_path_to_question(question_id):
    """
    Hàm thêm đường dẫn ảnh (image_path) vào câu hỏi dựa trên question_id.
    Trả về True nếu thêm thành công, False nếu có lỗi.
    """
    try:
        # Kết nối tới cơ sở dữ liệu
        image_path = f"{question_id}.png"
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # Cập nhật file path cho câu hỏi
            cursor.execute(
                "UPDATE Questions SET image_path = ? WHERE question_id = ?",
                (image_path, question_id)
            )
            
            # Kiểm tra số hàng bị ảnh hưởng
            if cursor.rowcount > 0:
                conn.commit()  # Lưu thay đổi
                print(f"Đã thêm file path '{image_path}' cho câu hỏi ID {question_id}.")
                return True
            else:
                print(f"Câu hỏi với ID {question_id} không tồn tại.")
                return False

    except Exception as e:
        print(f"Lỗi khi thêm file path: {e}")
        return False
    

def delete_exam_by_id(exam_id):
    """
    Xóa một bài thi khỏi bảng Exams dựa trên exam_id.

    Args:
        exam_id (int): ID của bài thi cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi xảy ra.
    """
    try:
        # Kết nối tới cơ sở dữ liệu
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Kiểm tra sự tồn tại của bài thi
                check_query = "SELECT COUNT(*) FROM Exams WHERE exam_id = ?"
                cursor.execute(check_query, (exam_id,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    print(f"Bài thi với ID {exam_id} không tồn tại.")
                    return False
                
                # Xóa bài thi
                delete_query = "DELETE FROM Exams WHERE exam_id = ?"
                cursor.execute(delete_query, (exam_id,))
                conn.commit()  # Lưu thay đổi vào cơ sở dữ liệu
                print(f"Bài thi với ID {exam_id} đã được xóa thành công.")
                return True
    except Exception as e:
        print(f"Lỗi khi xóa bài thi: {e}")
        return False

# for id in [i for i in range(3, 18)]:
#     delete_exam_by_id(id)
# s = [27, 33, 34, 38, 39, 42]
# for id in s:
#     add_image_path_to_question(id)

