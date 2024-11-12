import re
from database_operations import *

# Đọc file
def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Phân loại câu hỏi
def classify_questions(filepath):
    content = read_file(filepath)

    cau_hoi_trac_nghiem = []
    dap_an_trac_nghiem = []
    cau_hoi_dung_sai = []
    dap_an_dung_sai = []
    cau_hoi_ngan = []
    # Tách câu hỏi theo các phần PHẦN I, II, III

    content = content.split("\n")
    x = 0
    dapan1 = content[x].split(" ")
    x += 1
    dapan2 = content[x].split(" - ")
    x += 1
    dapan3 = content[x].split(" ")
    x += 1

    cau = False
    while (True):
        if content[x] == "":
            x+=1 
            continue
        if content[x].startswith("PHÀN II."):
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
        if (cau): cau_hoi_trac_nghiem[-1] += " " + content[x]
        x += 1

    cau = False
    while (True):
        if content[x].startswith("PHÀN III"):
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
        if content[x].startswith("Câu"):
            question = re.sub(r'^Câu\s*\d+[:.\s]*', '', content[x])
            cau_hoi_ngan.append(question)
            x += 1
            cau = True
            continue
        if cau: cau_hoi_ngan[-1] += " " + content[x]
        x += 1
    question = [cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3]
    add_exam("Đề thi Toán tốt nghiệp THPT từ năm 2025 (đề tham khảo)", "graduateExam", 12, question)

# Hiển thị câu hỏi
def display_questions(cau_hoi_trac_nghiem ,dap_an_trac_nghiem ,cau_hoi_dung_sai ,dap_an_dung_sai ,cau_hoi_ngan, dapan1, dapan2, dapan3):
    for i in range(len(cau_hoi_trac_nghiem)):
        print(dapan1[i])
        print(f"Câu {i + 1}: {cau_hoi_trac_nghiem[i]}")
        dap_an = dap_an_trac_nghiem[i].split("--")
        for x in dap_an:
            print(x)
    for i in range(len(cau_hoi_dung_sai)):
        print(dapan2[i])
        print(f"Câu {i + 1}: {cau_hoi_dung_sai[i]}")
        dap_an = dap_an_dung_sai[i].split("--")
        for x in dap_an:
            print(x)
    for i in range(len(cau_hoi_ngan)):
        print(dapan3[i])
        print(f"Câu {i + 1}: {cau_hoi_ngan[i]}")

# Đường dẫn đến file

filepath = "input.txt"
classify_questions(filepath)
# Hiển thị các câu hỏi
