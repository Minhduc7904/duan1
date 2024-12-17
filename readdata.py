import re
from database_operations import *

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Phân loại câu hỏi
def classify_questions(type_exam, class_name, name, correct_multiple_choice, correct_true_false, correct_short_answer, exam_content):
    content = exam_content

    cau_hoi_trac_nghiem = []
    dap_an_trac_nghiem = []
    cau_hoi_dung_sai = []
    dap_an_dung_sai = []
    cau_hoi_ngan = []
    name_exam = name

    content = content.split("\n")
    x = 0

    Class = class_name

    dapan1 = correct_multiple_choice.split(" ")

    dapan2 = correct_true_false.split(" - ")

    dapan3 = correct_short_answer.split(" ")

    cau = False
    while (True):
        if (x == len(content)): break
        if content[x] == "":
            x+=1 
            continue
        if content[x].startswith("Câu"):
            question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
            cau_hoi_trac_nghiem.append(question)
            x += 1
            cau = True
            dap_an_trac_nghiem.append("")
            continue
        if content[x].startswith("A."):
            dap_an_trac_nghiem[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("B."):
            dap_an_trac_nghiem[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("C."):
            dap_an_trac_nghiem[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("D."):
            dap_an_trac_nghiem[-1] += "--" + content[x][2:]
            cau = False
        if (cau): cau_hoi_trac_nghiem[-1] += " " + content[x]
        x += 1

    cau = False
    while (True):
        if (x == len(content)): break
        if content[x].startswith("PHẦN III"):
            x += 1
            break
        if content[x].startswith("Câu"):
            question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
            cau_hoi_dung_sai.append(question)
            x += 1
            dap_an_dung_sai.append("")
            cau = True
            continue
        if content[x].startswith("a)"):
            dap_an_dung_sai[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("b)"):
            dap_an_dung_sai[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("c)"):
            dap_an_dung_sai[-1] += "--" + content[x][2:]
            cau = False
        elif content[x].startswith("d)"):
            dap_an_dung_sai[-1] += "--" + content[x][2:]
            cau = False
        if cau: cau_hoi_dung_sai[-1] += " " + content[x]
        x += 1
    
    cau = False
    while (x != len(content)):
        if (x == len(content)): break
        if content[x].startswith("Câu"):
            question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
            cau_hoi_ngan.append(question)
            x += 1
            cau = True
            continue
        if cau: cau_hoi_ngan[-1] += " " + content[x]
        x += 1
    for x in cau_hoi_trac_nghiem: print(x)
    question = [cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3]
    return add_exam(name_exam, type_exam, int(Class), question)

def read_exam(Question_input):
    """
    Hàm phân tích nội dung đề thi thành các danh sách câu hỏi và đáp án.

    Args:
        Question_input (str): Nội dung đề thi dưới dạng chuỗi.

    Returns:
        list: Gồm các danh sách câu hỏi và đáp án [trắc nghiệm, đúng/sai, câu hỏi ngắn].
    """
    try:
        content = Question_input

        cau_hoi_trac_nghiem = []
        dap_an_trac_nghiem = []
        cau_hoi_dung_sai = []
        dap_an_dung_sai = []
        cau_hoi_ngan = []

        content = content.split("\n")
        x = 0

        # Xử lý câu hỏi trắc nghiệm
        cau = False
        while True:
            if content[x] == "":
                x += 1
                continue
            if content[x].startswith("PHẦN II."):
                x += 1
                break

            if content[x].startswith("Câu"):
                question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
                cau_hoi_trac_nghiem.append(question)
                x += 1
                cau = True
                dap_an_trac_nghiem.append("")
                continue
            if content[x].startswith("A."):
                dap_an_trac_nghiem[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("B."):
                dap_an_trac_nghiem[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("C."):
                dap_an_trac_nghiem[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("D."):
                dap_an_trac_nghiem[-1] += "--" + content[x][2:]
                cau = False
            if cau:
                cau_hoi_trac_nghiem[-1] += " " + content[x]
            x += 1
        # Xử lý câu hỏi đúng/sai
        cau = False
        while True:
            
            if content[x].startswith("PHẦN III"):
                x += 1
                break

            if content[x].startswith("Câu"):
                question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
                cau_hoi_dung_sai.append(question)
                x += 1
                dap_an_dung_sai.append("")
                cau = True
                continue
            if content[x].startswith("a)"):
                dap_an_dung_sai[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("b)"):
                dap_an_dung_sai[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("c)"):
                dap_an_dung_sai[-1] += "--" + content[x][2:]
                cau = False
            elif content[x].startswith("d)"):
                dap_an_dung_sai[-1] += "--" + content[x][2:]
                cau = False
            if cau:
                cau_hoi_dung_sai[-1] += " " + content[x]
            x += 1

        # Xử lý câu hỏi ngắn
        cau = False
        while x < len(content):
            if content[x].startswith("Câu"):
                question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
                cau_hoi_ngan.append(question)
                x += 1
                cau = True
                continue
            if cau:
                cau_hoi_ngan[-1] += " " + content[x]
            x += 1

        # Trả về kết quả
        question = [cau_hoi_trac_nghiem, dap_an_trac_nghiem, cau_hoi_dung_sai, dap_an_dung_sai, cau_hoi_ngan]
        print(12323312341324)
        print(question, 1231234324)
        return question

    except IndexError as e:
        print(f"Error: Out of bounds while parsing content. {e}")
        return None
    except re.error as e:
        print(f"Error: Regex failed to parse content. {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# filepath = "input.txt"
# classify_questions(filepath)
