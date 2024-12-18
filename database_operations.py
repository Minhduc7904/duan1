import pyodbc
import ast
from datetime import datetime, timedelta
import json

server = 'MINHDUCK\SQLEXPRESS'   
database = 'MYDB'               
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

"""
TẤT CẢ CÁC HÀM 
STT                            TÊN HÀM                                                                                             Ý NGHĨA
1   add_users(username, password, name, age, class_, school)                                                        Hàm dùng để thêm tài khoản cũng như đăng kí
2   add_exam1(name, exam_type, Class)                                                                               Hàm dùng để add đề bất kì
3   add_exam(name, exam_type, Class, questions)                                                                     Hàm dùng đề add đề kèm theo câu hỏi có trong đề
4   add_question(exam_id, question_type, content, answer_options, correct_answer, Class, difficulty = "easy")       Hàm dùng để add câu hỏi độ khó đang mặc định là dễ 
5   own_exam(user_id, exam_id)                                                                                      Hàm dùng để add vào bảng User_Exam thể hiện người dùng sở hữu đề
6   add_question_to_exam(exam_id, question_id)                                                                      Hàm dùng để add vào bảng Exam_Question thể hiện câu hỏi có trong đề
7   add_image_path_to_question(question_id)                                                                         Hàm dùng để add đường dẫn ảnh minh họa vào câu hỏi
8   User_does_Answers(summary_id, user_id, exam_id, question_id, user_answer, is_correct)                           Thêm câu trả lời của người dùng vào bảng User_Answers.
9   Done_exam(user_id, exam_id, score)                                                                              Đánh dấu bài thi của một người dùng là đã hoàn thành và thêm bản ghi vào User_Exam_Summary.
10  get_user_answers_and_correct_answers(summary_id)                                                                Lấy câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct cho tất cả các câu hỏi trong một bài thi.
11  get_all_users()                                                                                                 Hàm trả về tất cả người dùng có trong hệ thống
12  get_questions_in_exam(exam_id)                                                                                  Hàm trả về tất cả câu hỏi có trong bài thi
13  get_key_from_exam(exam_id)                                                                                      Trích xuất danh sách đáp án đúng và ID của các câu hỏi từ bài thi.
14  get_all_exams(user_id = None)                                                                                   Nếu user_id = None hàm trả về tất cả bài thi còn không thì trả về tất cả bài thi mà user_id sở hữu
15  get_user_answers_and_correct_answers(summary_id)                                                                Lấy câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct cho tất cả các câu hỏi trong một bài thi.
16  get_latest_summary_id(user_id, exam_id)                                                                         Truy vấn summary_id của lần làm bài gần nhất từ bảng User_Exam_Summary theo user_id và exam_id. Nếu không tìm thấy, trả về None.
17  get_latest_exams(limit=10)                                                                                      Truy vấn để lấy 10 bài thi mới nhất theo upload_time
18  get_exam_by_id(exam_id)                                                                                         Hàm trả về exam theo exam_id
19  get_summary_details(summary_id)                                                                                 Hàm trả về user_id exam_id và score theo summary_id
20  get_user_exam_history(user_id)                                                                                  Truy vấn lịch sử làm bài của người dùng từ bảng User_Exam_Summary.
21  find_user_by_id(user_id)                                                                                        Hàm tìm kiếm người dùng theo id
22  search_exams_by_types_and_class(exam_types=None, class_=None)                                                   Hàm trả về bài thi theo exam_types và class_
23  search_exam_by_name_case_insensitive(search_term)                                                               Hàm tìm kiếm theo từ khóa
24  update_user_exam_score(summary_id, new_score)                                                                   Cập nhật giá trị score trong bảng User_Exam_Summary.   
25  Done_exam(user_id, exam_id, score)                                                                              Đánh dấu bài thi của một người dùng là đã hoàn thành và thêm bản ghi vào User_Exam_Summary.
26  update_question_content(question_id, new_content)                                                               hàm sửa lại câu hỏi cho question
27  reset_identity_all_tables()                                                                                     Hàm reset lại id của các bảng
28  update_question_chapter(question_id, new_chapter)                                                               Hàm upadte chapter cho câu hỏi
29  update_exam_attribute(exam_id, column_name, new_value)                                                          Hàm cập nhật lại thuộc tính của bảng Exams
30  check(username)                                                                                                 Kiểm tra xem usernam đã tồn tại trong bảng chưa
31  check_login_credentials(username, password)                                                                     Kiểm tra thông tin đăng nhập và trả về user_id nếu hợp lệ.
32  check_user_exam_exists(user_id, exam_id)                                                                        Kiểm tra xem user_id và exam_id đã tồn tại trong bảng User_Exam hay chưa.
33  check_exam_status(user_id, exam_id)                                                                             Kiểm tra xem người dùng đã làm bài thi này chưa
34  delete_exam_by_id(exam_id)                                                                                      Xóa một bài thi khỏi bảng Exams dựa trên exam_id.
35  delete_questions_by_ids(ids)                                                                                    Xóa các câu hỏi từ 1 list id
36  delete_exam_question(exam_id, question_id)                                                                      Truy vấn xóa bản ghi từ bảng Exam_Question
"""


"""
add_users(username, password, name, age, class_, school)                                                        Hàm dùng để thêm tài khoản cũng như đăng kí
add_exam1(name, exam_type, Class)                                                                               Hàm dùng để add đề bất kì
add_exam(name, exam_type, Class, questions)                                                                     Hàm dùng đề add đề kèm theo câu hỏi có trong đề
add_question(exam_id, question_type, content, answer_options, correct_answer, Class, difficulty = "easy")       Hàm dùng để add câu hỏi độ khó đang mặc định là dễ 
own_exam(user_id, exam_id)                                                                                      Hàm dùng để add vào bảng User_Exam thể hiện người dùng sở hữu đề
add_question_to_exam(exam_id, question_id)                                                                      Hàm dùng để add vào bảng Exam_Question thể hiện câu hỏi có trong đề
add_image_path_to_question(question_id)                                                                         Hàm dùng để add đường dẫn ảnh minh họa vào câu hỏi
User_does_Answers(summary_id, user_id, exam_id, question_id, user_answer, is_correct)                           Thêm câu trả lời của người dùng vào bảng User_Answers.
Done_exam(user_id, exam_id, score)                                                                              Đánh dấu bài thi của một người dùng là đã hoàn thành và thêm bản ghi vào User_Exam_Summary.

"""

def add_users(username, password, name, age, class_, school):
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Users (username, password, name, age, Class, school)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, password, name, int(age), int(class_), school))
                conn.commit()
            print("Data inserted into Users table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into Users table:", e)
        return False

def add_exam(name, exam_type, Class, questions):
    cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3 = questions
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO Exams (name, exam_type, Class)
                    OUTPUT INSERTED.exam_id
                    VALUES (?, ?, ?);
                """
                cursor.execute(query, (name, exam_type, int(Class)))
                exam_id = cursor.fetchone()[0]
                print("Data inserted into Exams table successfully.")
                for i in range(len(cau_hoi_trac_nghiem)):
                    if not add_question(exam_id, "Trac nghiem", cau_hoi_trac_nghiem[i], dap_an_trac_nghiem[i], dapan1[i], Class, cursor):
                        raise Exception(f"Failed to add multiple choice question at index {i}")

                for i in range(len(cau_hoi_dung_sai)):
                    dap_an = ""
                    for x in range(4):
                        dap_an += dapan2[i*4 + x] + " "
                    if not add_question(exam_id, "Dung sai", cau_hoi_dung_sai[i], dap_an_dung_sai[i], dap_an, Class, cursor):
                        raise Exception(f"Failed to add true/false question at index {i}")
                    
                for i in range(len(cau_hoi_ngan)):
                    if not add_question(exam_id , "Ngan", cau_hoi_ngan[i], None, dapan3[i], Class, cursor):
                        raise Exception(f"Failed to add short answer question at index {i}")
                conn.commit()
                print(f"All data for exam {exam_id} committed successfully.")
                return True
    except Exception as e:
        print("Error inserting data into Exams table:", e)
        conn.rollback()
        return False
    
    
    


def add_question(exam_id, question_type, content, answer_options, correct_answer, Class, cursor, difficulty = "easy"):
    try:
        query = """
            INSERT INTO Questions (question_type, content, answer_options, correct_answer, difficulty, Class)
            OUTPUT INSERTED.question_id
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(query, (question_type, content, answer_options, correct_answer, difficulty, Class))
        question_id = cursor.fetchone()[0]  

        if not add_question_to_exam(exam_id, question_id, cursor):
            raise Exception(f"Failed to link question {question_id} to exam {exam_id}")
        print(f"Question {question_id} added successfully.")
        return True
    except Exception as e:
        print(f"Error inserting question:, Error: {e}")
        return False

def add_question1(question_type, content, answer_options, correct_answer, difficulty, chapter, Class, solution):
    """
    Thêm câu hỏi mới vào bảng Questions.
    
    Args:
        question_type (str): Loại câu hỏi (VD: Trắc nghiệm, Tự luận, ...).
        content (str): Nội dung của câu hỏi.
        answer_options (str): Các lựa chọn đáp án.
        correct_answer (str): Đáp án đúng.
        difficulty (str): Độ khó của câu hỏi (VD: Dễ, Trung bình, Khó).
        chapter (str): Chương của câu hỏi.
        Class (str): Lớp tương ứng với câu hỏi.
        image_path (str): Đường dẫn hình ảnh liên quan đến câu hỏi.

    Returns:
        int or None: ID của câu hỏi vừa được thêm nếu thành công, None nếu có lỗi.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    INSERT INTO Questions (question_type, content, answer_options, correct_answer, difficulty, chapter, Class, solution)
                    OUTPUT INSERTED.question_id
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (question_type, content, answer_options, correct_answer, difficulty, chapter, Class, solution))
                question_id = cursor.fetchone()[0]
                conn.commit()

                
                return question_id
    except Exception as e:
        print("Lỗi khi thêm câu hỏi mới:", e)
        return None

def add_question_to_exam(exam_id, question_id, cursor):
    try:
        query = """
            INSERT INTO Exam_Question (exam_id, question_id)
            VALUES (?, ?);
        """
        cursor.execute(query, (exam_id, question_id))
        print(f"Linked question {question_id} to exam {exam_id} successfully.")
        return True
    except Exception as e:
        print(f"Error linking question {question_id} to exam {exam_id}: {e}")
        return False

def add_exam1(name, exam_type, Class, chapter = None, duration=None):
    """
    Thêm một đề thi mới vào bảng Exams và trả về exam_id của đề thi vừa được thêm.

    Args:
        name (str): Tên của đề thi.
        exam_type (str): Loại đề thi.
        Class (int): Lớp của đề thi.

    Returns:
        int: ID của đề thi vừa được thêm nếu thành công.
        None: Nếu có lỗi xảy ra trong quá trình thêm dữ liệu.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    INSERT INTO Exams (name, exam_type, Class, chapter, duration)
                    OUTPUT INSERTED.exam_id
                    VALUES (?, ?, ?, ?, ?)
                """, (name, exam_type, int(Class), chapter, duration))
                exam_id = cursor.fetchone()[0]
                conn.commit()
                print("Data inserted into Exams table successfully. Exam ID:", exam_id)
                return exam_id
    except Exception as e:
        print("Error inserting data into Exams table:", e)
        return None

def own_exam(user_id, exam_id, created_by_user = 0):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO User_Exam (user_id, exam_id, completed, created_by_user)
                    VALUES (?, ?, ?, ?)
                """, (user_id, exam_id, 0, created_by_user)) 
                conn.commit()
            print("Data inserted into User_Exam table successfully.")
            return True
    except Exception as e:
        print("Error inserting data into User_Exam table:", e)
        return False
    
def add_image_path_to_question(question_id):
    """
    Hàm thêm đường dẫn ảnh (image_path) vào câu hỏi dựa trên question_id.
    Trả về True nếu thêm thành công, False nếu có lỗi.
    """
    try:
        
        image_path = f"{question_id}.png"
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            
            cursor.execute(
                "UPDATE Questions SET image_path = ? WHERE question_id = ?",
                (image_path, question_id)
            )
            
            
            if cursor.rowcount > 0:
                conn.commit()  
                print(f"Đã thêm file path '{image_path}' cho câu hỏi ID {question_id}.")
                return True
            else:
                print(f"Câu hỏi với ID {question_id} không tồn tại.")
                return False

    except Exception as e:
        print(f"Lỗi khi thêm file path: {e}")
        return False

def User_does_Answers(summary_id, user_id, exam_id, question_id, user_answer, is_correct):
    """
    Thêm câu trả lời của người dùng vào bảng User_Answers.

    Args:
        summary_id (int): ID của bản ghi trong bảng User_Exam_Summary.
        user_id (int): ID của người dùng.
        exam_id (int): ID của bài thi.
        question_id (int): ID của câu hỏi.
        user_answer (str): Câu trả lời của người dùng.

    Returns:
        bool: True nếu thêm thành công, False nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM User_Answers
                    WHERE summary_id = ? AND question_id = ?
                """, (summary_id, question_id))
                result = cursor.fetchone()

                if result[0] > 0:
                    print("Record already exists in User_Answers table. Skipping insertion.")
                else:
                    
                    cursor.execute("""
                        INSERT INTO User_Answers (summary_id, user_id, exam_id, question_id, user_answer, is_correct)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (summary_id, user_id, exam_id, question_id, user_answer, is_correct))
                    print("Inserted new record into User_Answers table.")

                
                conn.commit()
            return True
    except Exception as e:
        print("Error inserting data into User_Answers table:", e)
        return False

def add_user_report(user_id, error_type, description, question_id=None):
    """
    Thêm báo cáo từ người dùng vào bảng User_Reports.

    Args:
        user_id (int): ID của người dùng gửi báo cáo.
        error_type (str): Loại lỗi báo cáo.
        description (str): Mô tả chi tiết lỗi.
        question_id (int, optional): ID của câu hỏi liên quan. Nếu không có, truyền None.

    Returns:
        bool: True nếu thêm thành công, False nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                print(user_id, error_type, question_id, description)
                query = """
                    INSERT INTO User_Reports (user_id, error_type, question_id, description)
                    VALUES (?, ?, ?, ?)
                """
                

                
                cursor.execute(query, (user_id, error_type, question_id, description))

                
                conn.commit()
                print("Báo cáo đã được thêm thành công!")
                return True
    except Exception as e:
        print(f"Lỗi khi thêm báo cáo: {e}")
        return False

def add_questions_to_exam(exam_id, question_ids):
    """
    Thêm danh sách câu hỏi vào bảng Exam_Question.

    Args:
        exam_id (int): ID của bài thi.
        question_ids (list): Danh sách các question_id để thêm vào bài thi.

    Returns:
        bool: True nếu thêm thành công, False nếu có lỗi xảy ra.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                for question_id in question_ids:
                    
                    cursor.execute("""
                        INSERT INTO Exam_Question (exam_id, question_id)
                        VALUES (?, ?)
                    """, (exam_id, question_id))
                conn.commit()  
            print(f"Thêm thành công {len(question_ids)} câu hỏi vào bài thi ID {exam_id}.")
            return True
    except Exception as e:
        print(f"Lỗi khi thêm câu hỏi vào Exam_Question cho exam_id {exam_id}: {e}")
        return False

def get_question_by_id(question_id):
    """
    Truy vấn thông tin câu hỏi từ bảng Questions theo question_id.

    Args:
        question_id (int): ID của câu hỏi cần truy vấn.

    Returns:
        dict: Thông tin câu hỏi dưới dạng dictionary nếu tìm thấy.
        None: Nếu không tìm thấy câu hỏi hoặc xảy ra lỗi.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT question_id, question_type, content, answer_options,
                        correct_answer, difficulty, chapter, Class, image_path, solution
                    FROM Questions
                    WHERE question_id = ?;
                """
                cursor.execute(query, (question_id,))
                result = cursor.fetchone()

                
                if not result:
                    print(f"Không tìm thấy câu hỏi với question_id: {question_id}")
                    return None

                
                question = {
                    "question_id": result.question_id,
                    "question_type": result.question_type,
                    "content": result.content,
                    "answer_options": result.answer_options,
                    "correct_answer": result.correct_answer,
                    "difficulty": result.difficulty,
                    "chapter": result.chapter,
                    "Class": result.Class,
                    "image_path": result.image_path,
                    "solution" : result.solution
                }
                return question

    except Exception as e:
        print(f"Lỗi khi truy vấn câu hỏi với question_id {question_id}: {e}")
        return None


"""
get_user_answers_and_correct_answers(summary_id)                            Lấy câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct cho tất cả các câu hỏi trong một bài thi.
get_all_users()                                                             Hàm trả về tất cả người dùng có trong hệ thống
get_questions_in_exam(exam_id)                                              Hàm trả về tất cả câu hỏi có trong bài thi
get_key_from_exam(exam_id)                                                  Trích xuất danh sách đáp án đúng và ID của các câu hỏi từ bài thi.
get_all_exams(user_id = None)                                               Nếu user_id = None hàm trả về tất cả bài thi còn không thì trả về tất cả bài thi mà user_id sở hữu
get_user_answers_and_correct_answers(summary_id)                            Lấy câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct cho tất cả các câu hỏi trong một bài thi.
get_latest_summary_id(user_id, exam_id)                                     Truy vấn summary_id của lần làm bài gần nhất từ bảng User_Exam_Summary theo user_id và exam_id. Nếu không tìm thấy, trả về None.
get_latest_exams(limit=10)                                                  Truy vấn để lấy 10 bài thi mới nhất theo upload_time
get_exam_by_id(exam_id)                                                     Hàm trả về exam theo exam_id
get_summary_details(summary_id)                                             Hàm trả về user_id exam_id và score theo summary_id
get_user_exam_history(user_id)                                              Truy vấn lịch sử làm bài của người dùng từ bảng User_Exam_Summary.
find_user_by_id(user_id)                                                    Hàm tìm kiếm người dùng theo id
search_exams_by_types_and_class(exam_types=None, class_=None)               Hàm trả về bài thi theo exam_types và class_
search_exam_by_name_case_insensitive(search_term)                           Hàm tìm kiếm theo từ khóa
get_user_exam_statistics(user_id)                                           Hàm trả về tổng số đề đã làm, số đề được tạo bởi người dùng và điểm trung bình
"""
def get_all_users():
    """
    Lấy tất cả người dùng từ bảng Users.

    Returns:
        list: Danh sách người dùng dưới dạng dictionary.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT 
                        user_id,
                        username,
                        password,
                        name,
                        age,
                        Class,
                        school,
                        coins,
                        avatar_path,
                        type_user
                    FROM Users
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if not results:
                    print("Không có người dùng nào trong hệ thống.")
                    return []

                
                users = [
                    {
                        "user_id": row[0],
                        "username": row[1],
                        "password": row[2],  
                        "name": row[3],
                        "age": row[4],
                        "Class": row[5],
                        "school": row[6],
                        "coins": row[7],
                        "avatar_path": row[8],
                        "type_user": row[9]
                    }
                    for row in results
                ]
                return users

    except Exception as e:
        print("Lỗi khi truy vấn danh sách người dùng:", e)
        return []

def get_questions_in_exam(exam_id):
    """
    Truy vấn các câu hỏi thuộc bài thi với ID tương ứng, phân loại theo dạng câu hỏi,
    bao gồm cả question_id, nội dung, đáp án, đáp án đúng, và đường dẫn hình ảnh nếu có.
    """
    trac_nghiem = []
    dung_sai = []
    ngan = []

    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("SELECT question_id FROM Exam_Question WHERE exam_id = ?", (exam_id,))
                question_ids = cursor.fetchall()

                if not question_ids:
                    print(f"Không có câu hỏi nào trong bài thi với ID {exam_id}.")
                    return None

                print(f"Các câu hỏi trong bài thi ID {exam_id}:")

                
                for question_id_tuple in question_ids:
                    question_id = question_id_tuple[0]
                    cursor.execute("SELECT * FROM Questions WHERE question_id = ?", (question_id,))
                    question = cursor.fetchone()

                    if question:
                        if question.question_type == "Trac nghiem":
                            trac_nghiem.append({
                                "question_id": question_id,
                                "content": question.content,
                                "answer_options": question.answer_options,
                                "correct_answer": question.correct_answer,
                                "image_path": question.image_path
                            })
                        elif question.question_type == "Dung sai":
                            dung_sai.append({
                                "question_id": question_id,
                                "content": question.content,
                                "answer_options": question.answer_options,
                                "correct_answer": question.correct_answer,
                                "image_path": question.image_path
                            })
                        elif question.question_type == "Ngan":
                            ngan.append({
                                "question_id": question_id,
                                "content": question.content,
                                "correct_answer": question.correct_answer,
                                "image_path": question.image_path
                            })

    except Exception as e:
        print("Lỗi khi truy vấn các câu hỏi của bài thi:", e)
        return None

    return {
        "trac_nghiem": trac_nghiem,  
        "dung_sai": dung_sai,        
        "ngan": ngan,                
    }


def get_key_from_exam(exam_id):
    """
    Trích xuất danh sách đáp án đúng và ID của các câu hỏi từ bài thi.
    """
    questions = get_questions_in_exam(exam_id)

    
    trac_nghiem_answers = [
        {"question_id": q["question_id"], "correct_answer": q["correct_answer"]}
        for q in questions["trac_nghiem"]
    ]

    dung_sai_answers = [
        {"question_id": q["question_id"], "correct_answer": q["correct_answer"]}
        for q in questions["dung_sai"]
    ]

    ngan_answers = [
        {"question_id": q["question_id"], "correct_answer": q["correct_answer"]}
        for q in questions["ngan"]
    ]

    return trac_nghiem_answers, dung_sai_answers, ngan_answers

def get_all_exams():
    """
    Lấy tất cả các bài thi từ bảng Exams.

    Returns:
        list: Danh sách các bài thi dưới dạng dictionary.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT 
                        exam_id,
                        name,
                        upload_time,
                        exam_type,
                        Class,
                        duration,
                        chapter
                    FROM Exams
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if not results:
                    print("Không có bài thi nào trong hệ thống.")
                    return []

                
                exams = [
                    {
                        "exam_id": row[0],
                        "name": row[1],
                        "upload_time": row[2].strftime('%d/%m/%Y %H:%M:%S'),
                        "exam_type": row[3],
                        "Class": row[4],
                        "duration": row[5],
                        "chapter": row[6],
                    }
                    for row in results
                ]
                return exams

    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)
        return []

def get_latest_exams_by_class():
    """
    Lấy 5 bài thi mới nhất cho từng lớp (10, 11, 12).

    Returns:
        dict: Dictionary chứa danh sách các bài thi cho từng lớp.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:

                # Truy vấn lấy 5 bài thi mới nhất cho từng lớp
                query = """
                    WITH RankedExams AS (
                        SELECT 
                            exam_id,
                            name,
                            upload_time,
                            exam_type,
                            Class,
                            duration,
                            chapter,
                            ROW_NUMBER() OVER (PARTITION BY Class ORDER BY upload_time DESC) AS rn
                        FROM Exams
                        WHERE Class IN (10, 11, 12)
                    )
                    SELECT 
                        exam_id,
                        name,
                        upload_time,
                        exam_type,
                        Class,
                        duration,
                        chapter
                    FROM RankedExams
                    WHERE rn <= 5
                """

                cursor.execute(query)
                results = cursor.fetchall()

                # Đảm bảo dữ liệu cho từng lớp luôn tồn tại
                exams_by_class = {"10": [], "11": [], "12": []}

                for row in results:
                    exam = {
                        "exam_id": row[0],
                        "name": row[1],
                        "upload_time": row[2].strftime('%d/%m/%Y %H:%M:%S'),
                        "exam_type": row[3],
                        "Class": str(row[4]),
                        "duration": row[5],
                        "chapter": row[6],
                        "image_path": "/static/images-exam/default-image2.png"
                    }
                    exams_by_class[str(row[4])].append(exam)

                return exams_by_class

    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)
        return {"10": [], "11": [], "12": []}


    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)
        return {}




def get_all_exams_with_conditions(user_id=None, created_by_user=None, is_favorite=None):
    """
    Lấy danh sách các bài thi dựa trên các tiêu chí lọc.

    Args:
        user_id (int): ID của người dùng.
        created_by_user (int): ID của người tạo bài thi.
        is_favorite (bool): Lọc theo trạng thái is_favorite (True/False).

    Returns:
        list: Danh sách các bài thi dưới dạng dictionary.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT 
                        ue.exam_id,
                        ue.user_id,
                        ue.score_lastest,
                        ue.completed,
                        ue.created_by_user,
                        ue.is_favorite,
                        e.Class,
                        e.exam_type,
                        e.upload_time,
                        e.name
                    FROM User_Exam ue
                    JOIN Exams e ON ue.exam_id = e.exam_id
                    WHERE 1=1
                """
                params = []

                
                if user_id is not None:
                    query += " AND ue.user_id = ?"
                    params.append(user_id)
                if created_by_user is not None:
                    query += " AND ue.created_by_user = ?"
                    params.append(created_by_user)
                if is_favorite is not None:
                    query += " AND ue.is_favorite = ?"
                    params.append(1 if is_favorite else 0)

                
                cursor.execute(query, params)
                results = cursor.fetchall()

                
                exams = [
                    {
                        "exam_id": row[0],
                        "user_id": row[1],
                        "score_lastest": row[2],
                        "completed": row[3],
                        "created_by_user": row[4],
                        "is_favorite": bool(row[5]),
                        "Class": row[6],
                        "exam_type": row[7],
                        "upload_time": row[8].strftime('%d/%m/%Y %H:%M:%S'),
                        "name": row[9],
                    }
                    for row in results
                ]
                return exams

    except Exception as e:
        print("Lỗi khi truy vấn danh sách bài thi:", e)
        return []


def get_user_answers_and_correct_answers(summary_id):
    """
    Lấy câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct cho tất cả các câu hỏi trong một bài thi.

    Args:
        summary_id (int): ID của bản ghi trong bảng User_Exam_Summary.

    Returns:
        list[dict]: Danh sách các câu hỏi với câu trả lời của người dùng, đáp án đúng, và trạng thái is_correct.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT 
                        q.question_id,
                        q.content AS question_content,
                        q.correct_answer,
                        ua.user_answer,
                        ua.is_correct
                    FROM Exam_Question eq
                    INNER JOIN Questions q ON eq.question_id = q.question_id
                    LEFT JOIN User_Answers ua 
                        ON eq.question_id = ua.question_id 
                        AND ua.summary_id = ?
                    WHERE eq.exam_id = (
                        SELECT exam_id FROM User_Exam_Summary WHERE summary_id = ?
                    )
                """
                cursor.execute(query, (summary_id, summary_id))
                results = cursor.fetchall()

                
                questions = []
                for row in results:
                    questions.append({
                        "question_id": row.question_id,
                        "question_content": row.question_content,
                        "correct_answer": row.correct_answer,
                        "user_answer": row.user_answer if row.user_answer else None,
                        "is_correct": bool(row.is_correct) if row.is_correct is not None else None
                    })

                return questions
    except Exception as e:
        print("Error fetching user answers and correct answers:", e)
        return []

def get_latest_summary_id(user_id, exam_id):
    """
    Truy vấn summary_id của lần làm bài gần nhất từ bảng User_Exam_Summary theo user_id và exam_id.
    Nếu không tìm thấy, trả về None.

    Args:
        user_id (int): ID của người dùng.
        exam_id (int): ID của bài thi.

    Returns:
        int or None: summary_id của lần làm bài gần nhất hoặc None nếu không tìm thấy.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT TOP 1 summary_id
                    FROM User_Exam_Summary
                    WHERE user_id = ? AND exam_id = ?
                    ORDER BY completion_time DESC
                """
                cursor.execute(query, (user_id, exam_id))
                result = cursor.fetchone()

                
                return result.summary_id if result else None
    except Exception as e:
        print(f"Lỗi khi truy vấn summary_id của user_id {user_id}, exam_id {exam_id}:", e)
        return None

def get_latest_exams(limit=10):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
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

def get_summary_details(summary_id):
    """
    Truy vấn thông tin user_id, exam_id, và score từ bảng User_Exam_Summary dựa trên summary_id.

    Args:
        summary_id (int): ID của bản ghi trong bảng User_Exam_Summary.

    Returns:
        dict: Thông tin gồm user_id, exam_id, và score nếu tìm thấy.
            Nếu không tìm thấy, trả về None cho các trường.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT user_id, exam_id, score, logs
                    FROM User_Exam_Summary
                    WHERE summary_id = ?
                """
                cursor.execute(query, (summary_id,))
                result = cursor.fetchone()

                
                if not result:
                    return {
                        "user_id": None,
                        "exam_id": None,
                        "score": None,
                        "logs": None
                    }

                
                return {
                    "user_id": result.user_id,
                    "exam_id": result.exam_id,
                    "score": float(result.score) if result.score is not None else None,
                    "logs": result.logs
                }
    except Exception as e:
        print(f"Lỗi khi truy vấn thông tin từ summary_id {summary_id}:", e)
        return {
            "user_id": None,
            "exam_id": None,
            "score": None,
            "logs":None
        }

def get_exam_by_id(exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exams WHERE exam_id = ?", (exam_id,))
            result = cursor.fetchone()
            
            if result:
                
                columns = [column[0] for column in cursor.description]  
                result_dict = dict(zip(columns, result))  
                return result_dict

            return None
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bài thi với ID {exam_id}: {e}")
        return None

def get_user_by_id(user_id):
    """
    Lấy thông tin người dùng từ bảng Users theo user_id.

    Args:
        user_id (int): ID của người dùng.

    Returns:
        dict: Thông tin người dùng dưới dạng dictionary nếu tồn tại.
        None: Nếu không tìm thấy người dùng hoặc xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                
                columns = [column[0] for column in cursor.description]  
                result_dict = dict(zip(columns, result))  
                return result_dict

            print(f"Không tìm thấy người dùng với ID {user_id}.")
            return None
    except Exception as e:
        print(f"Lỗi khi tìm kiếm người dùng với ID {user_id}: {e}")
        return None

def get_user_exam_history(user_id):
    """
    Truy vấn lịch sử làm bài của người dùng từ bảng User_Exam_Summary và thông tin từ bảng Exams.

    Args:
        user_id (int): ID của người dùng.

    Returns:
        list[dict]: Danh sách các bản ghi lịch sử làm bài gồm summary_id, exam_id, name, exam_type, class,
                    score, và completion_time. Nếu không có lịch sử, trả về danh sách rỗng.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                        SELECT 
                            ues.summary_id,
                            ues.exam_id,
                            e.name,
                            e.exam_type,
                            e.class AS class_name, -- Sử dụng bí danh để tránh xung đột từ khóa
                            ues.score,
                            ues.completion_time
                        FROM User_Exam_Summary ues
                        JOIN Exams e ON ues.exam_id = e.exam_id
                        WHERE ues.user_id = ?
                        ORDER BY ues.completion_time DESC
                        """
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()

                
                history = []
                for row in results:
                    history.append({
                        "summary_id": row.summary_id,
                        "exam_id": row.exam_id,
                        "name": row.name,
                        "exam_type": row.exam_type,
                        "class": row.class_name,  
                        "score": float(row.score) if row.score is not None else None,
                        "completion_time": row.completion_time.strftime('%Y-%m-%d %H:%M:%S') if row.completion_time else None
                    })

                return history
    except Exception as e:
        print(f"Lỗi khi truy vấn lịch sử làm bài của user_id {user_id}:", e)
        return []

def find_user_by_id(user_id):
    """
    Tìm user theo ID trong bảng Users.
    :param user_id: ID của user
    :return: Thông tin user (dict) hoặc None nếu không tìm thấy
    """
    user_id = int(user_id)
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT user_id, username, password, name, age, Class, school, avatar_path, type_user, coins
                    FROM Users
                    WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                print(result)
                if result:
                    
                    user = {
                        "user_id": result[0],
                        "username": result[1],
                        "password": result[2],
                        "name": result[3],
                        "age": result[4],
                        "class": result[5],
                        "school": result[6],
                        "avatar_path": result[7],
                        "type_user": result[8],
                        "coins": result[9],
                    }
                    return user
                else:
                    return None  
    except Exception as e:
        print("Error querying user by ID:", e)
        return None

def search_exams_by_types_class_and_chapter(exam_types=None, class_=None, chapters=None):
    """
    Tìm kiếm các bài thi dựa trên loại bài thi (exam_type), lớp (class), và chương (chapter).

    Args:
        exam_types (list, optional): Danh sách các loại bài thi.
        class_ (list, optional): Danh sách các lớp.
        chapters (list, optional): Danh sách các chương.

    Returns:
        list: Danh sách các bài thi dưới dạng dictionary.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "SELECT exam_id, name, upload_time, exam_type, Class, chapter FROM Exams"
                conditions = []
                params = []

                
                if exam_types:
                    placeholders = ', '.join(['?'] * len(exam_types))
                    conditions.append(f"exam_type IN ({placeholders})")
                    params.extend(exam_types)

                
                if class_:
                    placeholders = ', '.join(['?'] * len(class_))
                    conditions.append(f"Class IN ({placeholders})")
                    params.extend(class_)

                
                if chapters:
                    placeholders = ', '.join(['?'] * len(chapters))
                    conditions.append(f"chapter IN ({placeholders})")
                    params.extend(chapters)

                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                
                cursor.execute(query, params)
                exams = cursor.fetchall()

                
                exam_list = []
                for exam in exams:
                    exam_list.append({
                        "exam_id": exam.exam_id,
                        "name": exam.name,
                        "upload_time": exam.upload_time.strftime('%d/%m/%Y %H:%M:%S'),
                        "exam_type": exam.exam_type,
                        "Class": exam.Class,
                        "chapter": exam.chapter
                    })
                return exam_list
    except Exception as e:
        print("Lỗi khi tìm kiếm các bài thi:", e)
        return []

    
def search_exam_by_name_case_insensitive(search_term):
    """
    Tìm kiếm bài thi theo tên trong bảng Exams (không phân biệt viết hoa hay viết thường).

    Args:
        search_term (str): Tên hoặc một phần tên bài thi cần tìm.

    Returns:
        list: Danh sách các bài thi phù hợp (mỗi bài thi là một dictionary).
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                SELECT * 
                FROM Exams
                WHERE LOWER(name) LIKE LOWER(?)
                """
                
                cursor.execute(query, ('%' + search_term + '%',))
                results = cursor.fetchall()
                
                if results:
                    
                    columns = [column[0] for column in cursor.description]
                    exams = [dict(zip(columns, row)) for row in results]
                    return exams
                else:
                    print("Không tìm thấy bài thi nào phù hợp.")
                    return []
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bài thi theo tên: {e}")
        return []
    
def get_user_exam_statistics(user_id):
    """
    Lấy tổng số bài đã làm (completed = 1), điểm trung bình (từ score_lastest), và tổng số đề đã tạo (created_by_user = 1).

    Args:
        user_id (int): ID của người dùng.

    Returns:
        tuple: (total_completed_exams, average_score, total_created_exams) nếu thành công.
            None nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT 
                    COUNT(*) AS total_completed_exams,
                    AVG(score_lastest) AS average_score,
                    (SELECT COUNT(*)
                    FROM User_Exam
                    WHERE user_id = ? AND created_by_user = 1) AS total_created_exams
                FROM User_Exam
                WHERE user_id = ? AND completed = 1;
                """
                cursor.execute(query, (user_id, user_id))
                result = cursor.fetchone()
                total_completed_exams = result[0] if result else 0
                average_score = result[1] if result and result[1] is not None else 0.0
                total_created_exams = result[2] if result else 0
                return total_completed_exams, average_score, total_created_exams
    except Exception as e:
        print(f"Error fetching statistics for user {user_id}: {e}")
        return None

def get_exam_time_by_summary_id(summary_id):
    """
    Lấy thời gian bắt đầu (start_time) và thời gian kết thúc (end_time) từ bảng User_Exam_Summary theo summary_id.

    Args:
        summary_id (int): ID của bản ghi trong bảng User_Exam_Summary.

    Returns:
        dict: Một từ điển chứa 'start_time' và 'end_time' nếu tìm thấy.
        None: Nếu không tìm thấy hoặc có lỗi xảy ra.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT start_time, end_time
                    FROM User_Exam_Summary
                    WHERE summary_id = ?
                """
                cursor.execute(query, (summary_id,))
                result = cursor.fetchone()

                if result:
                    return {
                        "start_time": result.start_time,
                        "end_time": result.end_time
                    }
                else:
                    print(f"No record found for summary_id: {summary_id}")
                    return None
    except Exception as e:
        print(f"Error retrieving exam time for summary_id {summary_id}:", e)
        return None

def get_all_questions():
    """
    Lấy tất cả các câu hỏi từ bảng Questions.

    Returns:
        list: Danh sách các câu hỏi, mỗi câu hỏi là một dict chứa các trường thông tin.
        None: Nếu có lỗi xảy ra trong quá trình truy vấn.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "SELECT question_id, question_type, content, answer_options, correct_answer, difficulty, chapter, Class, image_path, solution FROM Questions"
                cursor.execute(query)
                rows = cursor.fetchall()

                
                questions = []
                for row in rows:
                    questions.append({
                        "question_id": row.question_id,
                        "question_type": row.question_type,
                        "content": row.content,
                        "answer_options": row.answer_options,
                        "correct_answer": row.correct_answer,
                        "difficulty": row.difficulty,
                        "chapter": row.chapter,
                        "Class": row.Class,
                        "image_path": row.image_path,
                        "solution": row.solution
                    })

                return questions
    except Exception as e:
        print("Lỗi khi truy vấn tất cả câu hỏi:", e)
        return None

def get_question_ids_by_exam(exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT question_id
                    FROM Exam_Question
                    WHERE exam_id = ?;
                """
                cursor.execute(query, (exam_id,))
                results = cursor.fetchall()
                return [row.question_id for row in results]  
    except Exception as e:
        print(f"Lỗi khi truy vấn câu hỏi cho exam_id {exam_id}: {e}")
        return []

def get_random_questions_by_chapter(chapter, difficulty, num_trac_nghiem=0, num_dung_sai=0, num_ngan=0):
    """
    Lấy ngẫu nhiên danh sách question_id từ bảng Questions theo chương, loại câu hỏi, và độ khó.

    Args:
        chapter (str): Chương để lọc câu hỏi.
        difficulty (str): Độ khó của câu hỏi (ví dụ: 'easy', 'medium', 'hard').
        num_trac_nghiem (int): Số lượng câu hỏi loại "Trắc nghiệm" cần lấy. Mặc định là 12.
        num_dung_sai (int): Số lượng câu hỏi loại "Đúng sai" cần lấy. Mặc định là 4.
        num_ngan (int): Số lượng câu hỏi loại "Trả lời ngắn" cần lấy. Mặc định là 6.

    Returns:
        list: Danh sách các question_id lấy ngẫu nhiên từ các loại câu hỏi.
        None: Nếu có lỗi xảy ra trong quá trình truy vấn.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                question_ids = []
                if num_trac_nghiem > 0:
                    cursor.execute("""
                        SELECT TOP (?) question_id
                        FROM Questions
                        WHERE chapter = ? AND question_type = 'Trac nghiem' AND difficulty = ?
                        ORDER BY NEWID()
                    """, (num_trac_nghiem, chapter, difficulty))
                    question_ids += [row.question_id for row in cursor.fetchall()]

                if num_dung_sai > 0:
                    cursor.execute("""
                        SELECT TOP (?) question_id
                        FROM Questions
                        WHERE chapter = ? AND question_type = 'Dung sai' AND difficulty = ?
                        ORDER BY NEWID()
                    """, (num_dung_sai, chapter, difficulty))
                    question_ids += [row.question_id for row in cursor.fetchall()]

                if num_ngan > 0:
                
                    cursor.execute("""
                        SELECT TOP (?) question_id
                        FROM Questions
                        WHERE chapter = ? AND question_type = 'Ngan' AND difficulty = ?
                        ORDER BY NEWID()
                    """, (num_ngan, chapter, difficulty))
                    ngan_ids = [row.question_id for row in cursor.fetchall()]
                
                print("Random question IDs fetched successfully:", question_ids)
                return question_ids

    except Exception as e:
        print("Error fetching random questions by chapter and difficulty:", e)
        return None

import json

def get_user_exam_summary_with_duration_by_exam_id(exam_id):
    """
    Lấy tất cả các bản ghi từ bảng User_Exam_Summary theo exam_id và thông tin người dùng,
    bao gồm thời gian làm bài (duration) được tính bằng số phút và giây.

    Args:
        exam_id (int): ID của bài thi.

    Returns:
        list: Danh sách các bản ghi dưới dạng dictionary bao gồm thời gian làm bài, thông tin người dùng, logs và số lượng logs.
        None: Nếu xảy ra lỗi hoặc không có bản ghi nào.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        UES.summary_id,
                        UES.user_id,
                        UES.exam_id,
                        UES.score,
                        DATEDIFF(SECOND, UES.start_time, UES.completion_time) AS duration_in_seconds,
                        UES.logs,
                        U.name,
                        U.avatar_path
                    FROM User_Exam_Summary AS UES
                    JOIN Users AS U ON UES.user_id = U.user_id
                    WHERE UES.exam_id = ?
                """
                cursor.execute(query, (exam_id,))
                rows = cursor.fetchall()

                # Nếu không có bản ghi nào, trả về danh sách rỗng
                if not rows:
                    print(f"Không có bản ghi nào trong User_Exam_Summary với exam_id = {exam_id}")
                    return []

                # Xử lý dữ liệu trả về
                summaries = []
                for row in rows:
                    try:
                        logs = json.loads(row[5]) if row[5] else []  # Chuyển đổi logs từ JSON string sang danh sách, nếu NULL thì gán []
                    except json.JSONDecodeError:
                        logs = []  # Nếu logs không phải là JSON hợp lệ, gán thành danh sách rỗng
                    count = 0
                    if logs != None:
                        count = len(logs)
                    summary = {
                        "summary_id": row[0],
                        "user_id": row[1],
                        "exam_id": row[2],
                        "score": row[3],
                        "duration": f"{row[4] // 60} phút {row[4] % 60} giây" if row[4] else "N/A",
                        "log_count": count,  # Đếm số lượng phần tử trong logs
                        "user_name": row[6],
                        "user_avatar": row[7],
                    }
                    summaries.append(summary)

                return summaries

    except Exception as e:
        print(f"Lỗi khi truy vấn User_Exam_Summary với exam_id = {exam_id}: {e}")
        return None

def get_all_reports():
    """
    Lấy tất cả các bản ghi từ bảng User_Report.

    Returns:
        list: Danh sách các báo cáo dưới dạng dictionary.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT 
                        report_id,
                        user_id,
                        error_type,
                        question_id,
                        description,
                        report_time
                    FROM User_Reports
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if not results:
                    print("Không có bản ghi nào trong bảng User_Report.")
                    return []

                
                reports = [
                    {
                        "report_id": row[0],
                        "user_id": row[1],
                        "error_type": row[2],
                        "question_id": row[3],
                        "description": row[4],
                        "report_time": row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None,
                    }
                    for row in results
                ]
                return reports

    except Exception as e:
        print(f"Lỗi khi truy vấn danh sách báo cáo: {e}")
        return []

def calculate_correct_incorrect_answers(user_id):
    """
    Tính số câu trả lời đúng và sai của một người dùng trong bảng User_Answers.

    Args:
        user_id (int): ID của người dùng.

    Returns:
        dict: Một dictionary chứa số câu đúng và sai, hoặc None nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query_correct = """
                    SELECT COUNT(*) AS correct_count
                    FROM User_Answers
                    WHERE user_id = ? AND is_correct = 1
                """
                cursor.execute(query_correct, (user_id,))
                correct_count = cursor.fetchone()[0]

                
                query_incorrect = """
                    SELECT COUNT(*) AS incorrect_count
                    FROM User_Answers
                    WHERE user_id = ? AND is_correct = 0
                """
                cursor.execute(query_incorrect, (user_id,))
                incorrect_count = cursor.fetchone()[0]

                return (correct_count, incorrect_count)
    except Exception as e:
        print(f"Lỗi khi tính số câu trả lời đúng và sai cho user_id {user_id}: {e}")
        return None

def calculate_average_score_by_exam_id(exam_id):
    """
    Tính điểm trung bình của các bản ghi trong bảng User_Exam_Summary dựa trên exam_id.

    Args:
        exam_id (int): ID của bài thi.

    Returns:
        float: Điểm trung bình của các bản ghi, hoặc None nếu không có bản ghi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT AVG(score)
                    FROM User_Exam_Summary
                    WHERE exam_id = ?
                """
                cursor.execute(query, (exam_id,))
                result = cursor.fetchone()

                if result and result[0] is not None:
                    return round(result[0], 2)  
                else:
                    print(f"Không có bản ghi nào cho exam_id {exam_id}.")
                    return None

    except Exception as e:
        print(f"Lỗi khi tính điểm trung bình cho exam_id {exam_id}: {e}")
        return None



"""
update_user_exam_score(summary_id, new_score)                                                                   Cập nhật giá trị score trong bảng User_Exam_Summary.   
Done_exam(user_id, exam_id, score)                                                                              Đánh dấu bài thi của một người dùng là đã hoàn thành và thêm bản ghi vào User_Exam_Summary.
update_question_content(question_id, new_content)                                                               hàm sửa lại câu hỏi cho question
reset_identity_all_tables()                                                                                     Hàm reset lại id của các bảng
update_question_chapter(question_id, new_chapter)                                                               Hàm upadte chapter cho câu hỏi
update_exam_attribute(exam_id, column_name, new_value)                                                          Hàm cập nhật lại thuộc tính của bảng Exams
"""

def Done_exam(user_id, exam_id, score):
    """
    Đánh dấu bài thi của một người dùng là đã hoàn thành và thêm bản ghi vào User_Exam_Summary.

    Args:
        user_id (int): ID của người dùng.
        exam_id (int): ID của bài thi.
        score (float): Điểm mới của người dùng.

    Returns:
        int: summary_id của bản ghi vừa thêm vào User_Exam_Summary, hoặc None nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT duration
                    FROM Exams
                    WHERE exam_id = ?
                """, (exam_id,))
                duration_row = cursor.fetchone()
                duration = duration_row[0] if duration_row else None

                
                start_time = datetime.now() if duration is not None else None
                end_time = (start_time + timedelta(minutes=duration)) if duration is not None else None

                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM User_Exam
                    WHERE user_id = ? AND exam_id = ?
                """, (user_id, exam_id))
                result = cursor.fetchone()

                if result[0] == 0:
                    
                    cursor.execute("""
                        INSERT INTO User_Exam (user_id, exam_id, completed)
                        VALUES (?, ?, ?)
                    """, (user_id, exam_id, 1))
                    print("Added new record to User_Exam table.")
                else:
                    
                    cursor.execute("""
                        UPDATE User_Exam
                        SET completed = 1
                        WHERE user_id = ? AND exam_id = ?
                    """, (user_id, exam_id))
                    print("Updated completed status in User_Exam table.")

                
                cursor.execute("""
                    INSERT INTO User_Exam_Summary (user_id, exam_id, score, start_time, end_time)
                    OUTPUT INSERTED.summary_id
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, exam_id, score, start_time, end_time))
                
                
                summary_id = cursor.fetchone()[0]
                print(f"Added new record to User_Exam_Summary table with summary_id: {summary_id}")

                
                conn.commit()

            return summary_id
    except Exception as e:
        print("Error in Done_exam:", e)
        return None
    
def update_user_exam_score(summary_id, new_score, logs):
    """
    Cập nhật giá trị score và completion_time trong bảng User_Exam_Summary.

    Args:
        summary_id (int): ID của bản ghi trong bảng User_Exam_Summary.
        new_score (float): Giá trị điểm mới để cập nhật.

    Returns:
        bool: True nếu cập nhật thành công, False nếu có lỗi.
    """
    try:
        
        completion_time = datetime.now()
        logs_json = json.dumps(logs)

        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    UPDATE User_Exam_Summary
                    SET score = ?, completion_time = ?, logs = ?
                    WHERE summary_id = ?
                """
                cursor.execute(query, (new_score, completion_time, logs_json, summary_id))

                
                conn.commit()
                print(f"Score và completion_time của summary_id {summary_id} đã được cập nhật.")
                return True
    except Exception as e:
        print(f"Lỗi khi cập nhật score và completion_time cho summary_id {summary_id}: {e}")
        return False

def update_question_content(question_id, new_content):
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    UPDATE questions
                    SET content = ?
                    WHERE id = ?
                """
                
                cursor.execute(query, (new_content, question_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"Đã cập nhật thành công nội dung câu hỏi với ID: {question_id}.")
                else:
                    print(f"Không tìm thấy câu hỏi với ID: {question_id}.")
                return cursor.rowcount
    except Exception as e:
        print("Lỗi khi cập nhật nội dung câu hỏi:", e)
        return 0

def reset_identity_all_tables():
    """
    Reset giá trị IDENTITY cho tất cả các bảng được chỉ định.
    - Nếu bảng trống: IDENTITY được đặt lại về 1.
    - Nếu không có khoảng trống: IDENTITY được đặt thành giá trị tiếp theo sau ID cuối cùng.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                tables = [
                    {"table_name": "Exams", "id_column": "exam_id"},
                    {"table_name": "Questions", "id_column": "question_id"},
                    {"table_name": "User_Exam_Summary", "id_column": "summary_id"},
                    {"table_name": "Users", "id_column": "user_id"}
                ]

                for table in tables:
                    table_name = table["table_name"]
                    id_column = table["id_column"]

                    
                    query_check_empty = f"SELECT COUNT(*) FROM {table_name};"
                    cursor.execute(query_check_empty)
                    is_empty = cursor.fetchone()[0] == 0

                    if is_empty:
                        print(f"Bảng {table_name} trống. Đặt lại IDENTITY về 1.")
                        query_reset_identity = f"DBCC CHECKIDENT ('{table_name}', RESEED, 0);"
                        cursor.execute(query_reset_identity)
                    else:
                        
                        query_find_gap = f"""
                            SELECT ISNULL(MIN([{id_column}]) + 1, 0) AS next_id
                            FROM {table_name}
                            WHERE [{id_column}] + 1 NOT IN (SELECT [{id_column}] FROM {table_name})
                        """
                        cursor.execute(query_find_gap)
                        result = cursor.fetchone()

                        if result and result[0] > 0:
                            
                            next_id = result[0]
                            print(f"Tìm thấy khoảng trống trong bảng {table_name}, đặt lại IDENTITY bắt đầu từ {next_id}.")
                            query_reset_identity = f"DBCC CHECKIDENT ('{table_name}', RESEED, {next_id - 1});"
                            cursor.execute(query_reset_identity)
                        else:
                            
                            query_max_id = f"SELECT ISNULL(MAX([{id_column}]), 0) + 1 AS next_id FROM {table_name};"
                            cursor.execute(query_max_id)
                            next_id = cursor.fetchone()[0]
                            print(f"Bảng {table_name} không có khoảng trống, đặt IDENTITY tiếp theo là {next_id}.")
                            query_reset_identity = f"DBCC CHECKIDENT ('{table_name}', RESEED, {next_id - 1});"
                            cursor.execute(query_reset_identity)

                    
                    conn.commit()
                    print(f"Đã reset giá trị IDENTITY cho bảng {table_name}.")

    except Exception as e:
        print("Error resetting identity for all tables:", e)

def update_is_favorite(user_id, exam_id, is_favorite):
    """
    Cập nhật thuộc tính is_favorite trong bảng User_Exam.
    Nếu không tồn tại bản ghi, thêm một bản ghi mới.

    Args:
        user_id (int): ID của người dùng.
        exam_id (int): ID của bài thi.
        is_favorite (bool): Giá trị mới của is_favorite (True hoặc False).

    Returns:
        bool: True nếu thao tác thành công, False nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                check_query = """
                    SELECT COUNT(*)
                    FROM User_Exam
                    WHERE user_id = ? AND exam_id = ?
                """
                cursor.execute(check_query, (user_id, exam_id))
                result = cursor.fetchone()

                if result[0] > 0:
                    
                    update_query = """
                        UPDATE User_Exam
                        SET is_favorite = ?
                        WHERE user_id = ? AND exam_id = ?
                    """
                    cursor.execute(update_query, (1 if is_favorite else 0, user_id, exam_id))
                else:
                    
                    insert_query = """
                        INSERT INTO User_Exam (user_id, exam_id, is_favorite)
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(insert_query, (user_id, exam_id, 1 if is_favorite else 0))
                
                
                conn.commit()

                print("Thao tác thành công!")
                return True

    except Exception as e:
        print("Error updating or inserting is_favorite:", e)
        return False

def update_question_chapter(question_id, new_chapter):
    
    
    
    
    
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    UPDATE Questions
                    SET chapter = ?
                    WHERE question_id = ?
                """
                
                cursor.execute(query, (new_chapter, question_id))
                conn.commit()
                
                
                if cursor.rowcount > 0:
                    print(f"Đã cập nhật thành công thuộc tính 'chapter' cho Question ID {question_id}.")
                else:
                    print(f"Không tìm thấy Question với ID {question_id}.")
                return cursor.rowcount > 0
    except Exception as e:
        print("Lỗi khi cập nhật thuộc tính 'chapter':", e)
        return False

def update_exam_attribute(exam_id, column_name, new_value):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = f"""
                    UPDATE Exams
                    SET {column_name} = ?
                    WHERE exam_id = ?
                """
                
                cursor.execute(query, (new_value, exam_id))
                conn.commit()
                
                
                if cursor.rowcount > 0:
                    print(f"Đã cập nhật thành công thuộc tính '{column_name}' cho Exam ID {exam_id}.")
                else:
                    print(f"Không tìm thấy Exam với ID {exam_id}.")
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Lỗi khi cập nhật thuộc tính '{column_name}' trong bảng Exams:", e)
        return False


def update_score_lastest(user_id, exam_id, score_lastest):
    """
    Cập nhật cột score_lastest cho một người dùng và một đề thi cụ thể.

    Args:
        user_id (int): ID người dùng.
        exam_id (int): ID đề thi.
        score_lastest (float): Điểm bài làm gần nhất cần cập nhật.

    Returns:
        bool: True nếu cập nhật thành công, False nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                UPDATE User_Exam
                SET score_lastest = ?
                WHERE user_id = ? AND exam_id = ?;
                """
                cursor.execute(query, (score_lastest, user_id, exam_id))
                conn.commit()
                print(f"Updated score_lastest to {score_lastest} for user_id {user_id}, exam_id {exam_id}.")
                return True
    except Exception as e:
        print(f"Error updating score_lastest: {e}")
        return False
    
def update_user_field(user_id, field, value):
    """
    Cập nhật một trường cụ thể trong bảng Users dựa trên user_id.
    
    Args:
        user_id (int): ID của người dùng cần cập nhật.
        field (str): Tên trường cần cập nhật.
        value: Giá trị mới cần cập nhật.
        
    Returns:
        bool: True nếu cập nhật thành công, False nếu có lỗi.
    """
    try:
        
        allowed_fields = ["username", "password", "name", "age", "Class", "school", "num_of_exams", "num_of_questions", 'avatar_path']

        if field not in allowed_fields:
            raise ValueError(f"Field '{field}' không được phép cập nhật.")

        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = f"UPDATE Users SET {field} = ? WHERE user_id = ?;"
                
                cursor.execute(query, (value, user_id))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Đã cập nhật thành công trường '{field}' của user_id = {user_id} với giá trị '{value}'.")
                    return True
                else:
                    print(f"Không tìm thấy user_id = {user_id}.")
                    return False
    except ValueError as ve:
        print(f"Lỗi: {ve}")
        return False
    except Exception as e:
        print(f"Lỗi khi cập nhật trường '{field}' cho user_id = {user_id}: {e}")
        return False
    

def update_question_by_id(question_id, question_type, content, answer_options, correct_answer, difficulty, chapter, Class, image_path):
    """
    Cập nhật thông tin câu hỏi trong bảng Questions theo question_id.
    
    Args:
        question_id (int): ID của câu hỏi cần cập nhật.
        question_type (str): Loại câu hỏi (VD: Trắc nghiệm, Tự luận, ...).
        content (str): Nội dung mới của câu hỏi.
        answer_options (str): Các lựa chọn đáp án.
        correct_answer (str): Đáp án đúng.
        difficulty (str): Độ khó của câu hỏi (VD: Dễ, Trung bình, Khó).
        chapter (str): Chương của câu hỏi.
        Class (str): Lớp tương ứng với câu hỏi.
        image_path (str): Đường dẫn hình ảnh liên quan đến câu hỏi.

    Returns:
        bool: True nếu cập nhật thành công, False nếu có lỗi hoặc không tìm thấy câu hỏi.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    UPDATE Questions
                    SET question_type = ?, content = ?, answer_options = ?, correct_answer = ?, 
                        difficulty = ?, chapter = ?, Class = ?, image_path = ?
                    WHERE question_id = ?
                """
                cursor.execute(query, (question_type, content, answer_options, correct_answer, difficulty, chapter, Class, image_path, question_id))
                conn.commit()

                
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Lỗi khi cập nhật câu hỏi với question_id {question_id}:", e)
        return False
    
def update_question(question_id, content, question_type, answer_options, correct_answer, difficulty, chapter, Class, solution):
    
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                    UPDATE Questions
                    SET content = ?, question_type = ?, answer_options = ?, correct_answer = ?, difficulty = ?, chapter = ?, Class = ?, solution = ?
                    WHERE question_id = ?;
                """
                cursor.execute(query, (content, question_type, answer_options, correct_answer, difficulty, chapter, Class, solution, question_id))
                conn.commit()
                return True
    except Exception as e:
        print(f"Error updating question {question_id}: {e}")
        return False
    

def update_Exam_Question(exam_id, question_ids):
    try:
        question_ids = ast.literal_eval(question_ids)
    except Exception as e:
        print(f"Lỗi khi cập nhật Exam_Question cho exam_id {exam_id}: {e}")
        return {
            "error": str(e)
        }
    """
    Cập nhật bảng Exam_Question:
    - Thêm các bản ghi (exam_id, question_id) nếu chưa tồn tại.
    - Xóa các bản ghi (exam_id, question_id) nếu không có trong danh sách question_ids.

    Args:
        exam_id (int): ID của đề thi.
        question_ids (list): Danh sách question_id cần cập nhật.

    Returns:
        dict: Thông tin về số bản ghi đã thêm và xóa.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query_select = """
                    SELECT question_id
                    FROM Exam_Question
                    WHERE exam_id = ?;
                """
                cursor.execute(query_select, (exam_id,))
                current_question_ids = {row.question_id for row in cursor.fetchall()}

                
                to_add = set(question_ids) - current_question_ids

                
                to_delete = current_question_ids - set(question_ids)

                
                for question_id in to_add:
                    query_insert = """
                        INSERT INTO Exam_Question (exam_id, question_id)
                        VALUES (?, ?);
                    """
                    cursor.execute(query_insert, (exam_id, question_id))

                
                for question_id in to_delete:
                    query_delete = """
                        DELETE FROM Exam_Question
                        WHERE exam_id = ? AND question_id = ?;
                    """
                    cursor.execute(query_delete, (exam_id, question_id))

                
                conn.commit()

                return {
                    "added": len(to_add),
                    "deleted": len(to_delete),
                }
    except Exception as e:
        print(f"Lỗi khi cập nhật Exam_Question cho exam_id {exam_id}: {e}")
        return {
            "error": str(e)
        }
    
def update_exam(exam_id, name=None, exam_type=None, Class=None, duration=None, chapter=None):
    """
    Cập nhật thông tin bài thi trong bảng Exams.

    Args:
        exam_id (int): ID của bài thi cần cập nhật.
        name (str, optional): Tên mới của bài thi.
        exam_type (str, optional): Loại bài thi mới.
        Class (int, optional): Lớp mới của bài thi.

    Returns:
        bool: True nếu cập nhật thành công, False nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                fields_to_update = []
                values = []

                if name:
                    fields_to_update.append("name = ?")
                    values.append(name)

                if exam_type:
                    fields_to_update.append("exam_type = ?")
                    values.append(exam_type)

                if Class:
                    fields_to_update.append("Class = ?")
                    values.append(Class)

                if duration != None:
                    fields_to_update.append("duration = ?")
                    values.append(duration)

                if chapter != None:
                    fields_to_update.append("chapter = ?")
                    values.append(chapter)

                
                if not fields_to_update:
                    print("Không có thông tin nào để cập nhật.")
                    return False

                
                query = f"""
                    UPDATE Exams
                    SET {', '.join(fields_to_update)}
                    WHERE exam_id = ?;
                """
                values.append(exam_id)  

                
                cursor.execute(query, values)
                conn.commit()

                print(f"Đã cập nhật bài thi với exam_id: {exam_id}")
                return True

    except Exception as e:
        print(f"Lỗi khi cập nhật bài thi với exam_id {exam_id}: {e}")
        return False
    

def update_user(user_id, username=None, password=None, name=None, age=None, Class=None, school=None, coins=None, type_user=None, avatar_path=None):
    """
    Cập nhật thông tin người dùng trong bảng Users.

    Args:
        user_id (int): ID của người dùng cần cập nhật.
        username (str, optional): Tên đăng nhập mới.
        password (str, optional): Mật khẩu mới.
        name (str, optional): Họ và tên mới.
        age (int, optional): Tuổi mới.
        Class (int, optional): Lớp mới.
        school (str, optional): Trường mới.
        coins (int, optional): Số coins mới.

    Returns:
        bool: True nếu cập nhật thành công, False nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                fields_to_update = []
                values = []

                if username:
                    fields_to_update.append("username = ?")
                    values.append(username)

                if password:
                    fields_to_update.append("password = ?")
                    values.append(password)

                if name:
                    fields_to_update.append("name = ?")
                    values.append(name)

                if age:
                    fields_to_update.append("age = ?")
                    values.append(age)

                if Class:
                    fields_to_update.append("Class = ?")
                    values.append(Class)

                if school:
                    fields_to_update.append("school = ?")
                    values.append(school)

                if coins is not None:
                    fields_to_update.append("coins = ?")
                    values.append(coins)
                
                if type_user is not None:
                    fields_to_update.append("type_user = ?")
                    values.append(type_user)

                if type_user is not None:
                    fields_to_update.append("avatar_path = ?")
                    values.append(avatar_path)
                
                if not fields_to_update:
                    print("Không có thông tin nào để cập nhật.")
                    return False

                
                query = f"""
                    UPDATE Users
                    SET {', '.join(fields_to_update)}
                    WHERE user_id = ?;
                """
                values.append(user_id)  

                
                cursor.execute(query, values)
                conn.commit()

                print(f"Đã cập nhật thông tin người dùng với user_id: {user_id}")
                return True

    except Exception as e:
        print(f"Lỗi khi cập nhật thông tin người dùng với user_id {user_id}: {e}")
        return False
    
def update_user_coins(user_id):
    """
    Giảm số coins của người dùng hiện tại đi 10.

    Args:
        user_id (int): ID của người dùng cần cập nhật.

    Returns:
        bool: True nếu cập nhật thành công, False nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("SELECT coins FROM Users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()

                if not result:
                    print(f"Người dùng với user_id {user_id} không tồn tại.")
                    return False

                current_coins = result[0]

                
                if current_coins < 10:
                    print(f"Người dùng với user_id {user_id} không đủ coins.")
                    return False

                
                new_coins = current_coins - 10
                cursor.execute("UPDATE Users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
                conn.commit()

                print(f"Đã cập nhật coins cho user_id {user_id}. Coins mới: {new_coins}")
                return True

    except Exception as e:
        print(f"Lỗi khi cập nhật coins cho user_id {user_id}: {e}")
        return False

"""
check(username)                                                                                                 Kiểm tra xem usernam đã tồn tại trong bảng chưa
check_login_credentials(username, password)                                                                     Kiểm tra thông tin đăng nhập và trả về user_id nếu hợp lệ.
check_user_exam_exists(user_id, exam_id)                                                                        Kiểm tra xem user_id và exam_id đã tồn tại trong bảng User_Exam hay chưa.
check_exam_status(user_id, exam_id)                                                                             Kiểm tra xem người dùng đã làm bài thi này chưa
"""

def check(username):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", (username,))
                result = cursor.fetchone()

                
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
    """
    Kiểm tra thông tin đăng nhập và trả về user_id nếu hợp lệ.
    :param username: Tên đăng nhập
    :param password: Mật khẩu
    :return: user_id nếu thông tin hợp lệ, None nếu không hợp lệ
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT user_id FROM Users
                    WHERE username = ? AND password = ?
                """, (username, password))
                
                result = cursor.fetchone()

                
                if result:
                    print(f"Thông tin đăng nhập hợp lệ. User ID: {result[0]}")
                    return result[0]  
                else:
                    print("Tên đăng nhập hoặc mật khẩu không đúng.")
                    return None  
    except Exception as e:
        print("Lỗi khi kiểm tra thông tin đăng nhập:", e)
        return None

def check_user_exam_is_favorite(user_id, exam_id):
    """
    Kiểm tra xem user_id và exam_id đã tồn tại trong bảng User_Exam với is_favorite = 1 hay chưa.

    Args:
        user_id (int): ID của người dùng.
        exam_id (int): ID của bài thi.

    Returns:
        bool: True nếu tồn tại với is_favorite = 1, False nếu không.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    SELECT COUNT(*)
                    FROM User_Exam
                    WHERE user_id = ? AND exam_id = ? AND is_favorite = 1
                """
                cursor.execute(query, (user_id, exam_id))
                result = cursor.fetchone()

                
                return result[0] > 0
    except Exception as e:
        print("Error checking user_exam is_favorite:", e)
        return False

def check_exam_status(user_id, exam_id):
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT completed
                    FROM User_Exam
                    WHERE user_id = ? AND exam_id = ?
                """
                cursor.execute(query, (user_id, exam_id))
                result = cursor.fetchone()
                return result[0] == 1 if result else False
    except Exception as e:
        print("Error checking exam status:", e)
        return False


"""
delete_exam_by_id(exam_id)                                                                                          Xóa một bài thi khỏi bảng Exams dựa trên exam_id.
delete_questions_by_ids(ids)                                                                                        Xóa các câu hỏi từ 1 list id
delete_exam_question(exam_id, question_id)                                                                          Truy vấn xóa bản ghi từ bảng Exam_Question

"""

def delete_exam_by_id(exam_id):
    """
    Xóa một bài thi khỏi bảng Exams dựa trên exam_id.

    Args:
        exam_id (int): ID của bài thi cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi xảy ra.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                check_query = "SELECT COUNT(*) FROM Exams WHERE exam_id = ?"
                cursor.execute(check_query, (exam_id,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    print(f"Bài thi với ID {exam_id} không tồn tại.")
                    return False
                
                
                delete_query = "DELETE FROM Exams WHERE exam_id = ?"
                cursor.execute(delete_query, (exam_id,))
                conn.commit()  
                print(f"Bài thi với ID {exam_id} đã được xóa thành công.")
                return True
    except Exception as e:
        print(f"Lỗi khi xóa bài thi: {e}")
        return False
    
def delete_questions_by_ids(ids):
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = """
                    DELETE FROM Questions
                    WHERE question_id IN ({})
                """.format(', '.join('?' for _ in ids))
                
                
                cursor.execute(query, ids)
                conn.commit()
                
                print(f"{cursor.rowcount} câu hỏi đã bị xóa.")
                return cursor.rowcount
    except Exception as e:
        print("Error deleting questions:", e)
        return 0
    
def delete_exam_question(exam_id=None, question_id=None):
    """
    Xóa các bản ghi trong bảng Exam_Question dựa trên exam_id, question_id, hoặc cả hai.
    
    Args:
        exam_id (int, optional): ID đề thi cần xóa. Mặc định là None.
        question_id (int, optional): ID câu hỏi cần xóa. Mặc định là None.
        
    Returns:
        int: Số lượng bản ghi đã xóa. Trả về 0 nếu không xóa được bản ghi nào.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "DELETE FROM Exam_Question WHERE 1=1"
                params = []

                if exam_id is not None:
                    query += " AND exam_id = ?"
                    params.append(exam_id)

                if question_id is not None:
                    query += " AND question_id = ?"
                    params.append(question_id)

                
                cursor.execute(query, params)
                conn.commit()

                
                if cursor.rowcount > 0:
                    print(f"Đã xóa thành công {cursor.rowcount} bản ghi từ Exam_Question.")
                else:
                    print("Không tìm thấy bản ghi nào để xóa.")
                return cursor.rowcount
    except Exception as e:
        
        print(f"Lỗi khi xóa bản ghi Exam_Question: {e}")
        return 0

def delete_user_exam_summary(user_id=None, exam_id=None):
    """
    Xóa các bản ghi trong bảng User_Exam_Summary theo user_id, exam_id hoặc cả hai.
    
    Args:
        user_id (int): ID người dùng (tùy chọn).
        exam_id (int): ID đề thi (tùy chọn).
        
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "DELETE FROM User_Exam_Summary WHERE 1=1"
                params = []

                if user_id is not None:
                    query += " AND user_id = ?"
                    params.append(user_id)

                if exam_id is not None:
                    query += " AND exam_id = ?"
                    params.append(exam_id)

                
                cursor.execute(query, params)
                conn.commit()
                print(f"Deleted records from User_Exam_Summary where user_id={user_id} and exam_id={exam_id}")
                return True

    except Exception as e:
        print(f"Error deleting records from User_Exam_Summary: {e}")
        return False

def delete_question_by_id(question_id):
    """
    Xóa câu hỏi khỏi bảng Questions theo question_id.
    
    Args:
        question_id (int): ID của câu hỏi cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi hoặc không tìm thấy câu hỏi.
    """
    try:
        
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "DELETE FROM Questions WHERE question_id = ?"
                cursor.execute(query, (question_id,))
                conn.commit()

                
                return cursor.rowcount > 0
    except Exception as e:
        print(f"Lỗi khi xóa câu hỏi với question_id {question_id}:", e)
        return False

def delete_user_by_id(user_id):
    """
    Xóa người dùng khỏi bảng Users dựa trên user_id.

    Args:
        user_id (int): ID của người dùng cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu xảy ra lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    print(f"Người dùng với user_id {user_id} không tồn tại.")
                    return False

                
                cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
                conn.commit()

                print(f"Đã xóa người dùng với user_id: {user_id}")
                return True

    except Exception as e:
        print(f"Lỗi khi xóa người dùng với user_id {user_id}: {e}")
        return False

def delete_report_by_id(report_id):
    """
    Xóa một báo cáo từ bảng User_Report dựa vào report_id.

    Args:
        report_id (int): ID của báo cáo cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi.
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "DELETE FROM User_Reports WHERE report_id = ?"
                cursor.execute(query, (report_id,))

                
                conn.commit()

                print(f"Đã xóa báo cáo với report_id: {report_id}")
                return True
    except Exception as e:
        print(f"Lỗi khi xóa báo cáo với report_id {report_id}: {e}")
        return False

def validate_and_process_data(data):
    """
    Xử lý và kiểm tra dữ liệu từ yêu cầu frontend, sau đó lưu trữ vào cơ sở dữ liệu.

    Args:
        data (dict): Dữ liệu JSON từ frontend.

    Returns:
        tuple: (Processed data hoặc thông báo lỗi, HTTP status code)
    """
    try:
        
        exam_info = data.get("examInfo", {})
        questions = data.get("questions", {})

        if not exam_info or not questions:
            return {"error": "Dữ liệu không hợp lệ hoặc bị thiếu!"}, 400

        name = exam_info.get("name", "Không tên")
        exam_type = exam_info.get("typeExam", "Khác")
        Class = exam_info.get("class", "10")
        chapter = exam_info.get("chapter", None)
        duration = exam_info.get("duration", None)

        exam_id = add_exam1(name=name, exam_type=exam_type, Class=Class, chapter=chapter, duration=duration)
        if not exam_id:
            return {"error": "Lỗi khi thêm đề thi vào cơ sở dữ liệu!"}, 500

        ids = []
        for question_type, question_list in questions.items():
            for question in question_list:
                question_keys = [key for key in question.keys()]
                content_key = next((key for key in question_keys if "question_" in key), None)
                chapter_key = next((key for key in question_keys if "chapter" in key), None)
                type_question_key = next((key for key in question_keys if "type_question" in key), None)
                class_key = next((key for key in question_keys if "class" in key), None)
                difficulty_key = next((key for key in question_keys if "difficulty" in key), None)
                solution = ""  
                print(question_keys, content_key, chapter_key, type_question_key, class_key, difficulty_key)
                
                content = question.get(content_key, "")
                chapter = question.get(chapter_key, "Chưa rõ")
                type_question = question.get(type_question_key, question_type)
                Class = question.get(class_key, "10")
                difficulty = question.get(difficulty_key, "NB")

                correct_answer = question.get(f"{content_key}_answer", "")
                if question_type == "multipleChoiceQuestions":
                    answer_options = " -- ".join(
                        question.get(f"{content_key}_choice_{opt}", "").replace(f"{opt}.", "").strip()
                        for opt in ["A", "B", "C", "D"]
                        if question.get(f"{content_key}_choice_{opt}")
                    )
                    

                    question_id = add_question1(
                        question_type=type_question,
                        content=content,
                        answer_options=answer_options,
                        correct_answer=correct_answer,
                        difficulty=difficulty,
                        chapter=chapter,
                        Class=Class,
                        solution=solution,
                    )
                    ids.append(question_id)

                elif question_type == "trueFalseQuestions":
                    propositions = " -- ".join(
                        question.get(f"{content_key}_proposition_{opt}", "").replace(f"{opt})", "").strip()
                        for opt in ["a", "b", "c", "d"]
                        if question.get(f"{content_key}_proposition_{opt}")
                    )
                    question_id = add_question1(
                        question_type=type_question,
                        content=content,
                        answer_options=propositions,
                        correct_answer=correct_answer,
                        difficulty=difficulty,
                        chapter=chapter,
                        Class=Class,
                        solution=solution,
                    )
                    ids.append(question_id)
                else:
                    question_id = add_question1(
                        question_type=type_question,
                        content=content,
                        answer_options=propositions,
                        correct_answer=correct_answer,
                        difficulty=difficulty,
                        chapter=chapter,
                        Class=Class,
                        solution=solution,
                    )
                    ids.append(question_id)

                if not question_id:
                    return {"error": f"Lỗi khi thêm câu hỏi: {content}"}, 500
        add_questions_to_exam(exam_id, ids)
        
        return {"status": "success", "message": "Dữ liệu đã được xử lý và lưu trữ thành công!"}, 200

    except Exception as e:
        print("Lỗi trong quá trình xử lý dữ liệu:", e)
        return {"error": f"Đã xảy ra lỗi: {str(e)}"}, 500

































