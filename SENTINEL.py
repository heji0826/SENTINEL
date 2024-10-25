import json
import csv
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# 이메일 설정
sender_email = "gyudol99@naver.com"  # 보내는 사람 네이버 이메일 주소
receiver_email = "gyudol99@naver.com"  # 받는 사람 이메일 주소
password = "dkaghdkagh1."  # 네이버 이메일 계정 비밀번호
subject = "취약점 진단 및 조치 결과"  # 이메일 제목

# 파일 경로 설정
apache_json_path = '/home/ubuntu/SENTINEL/apache/apache.json'
apache_action_json_path = '/home/ubuntu/SENTINEL/apache/apache_action.json'
csv_file_path = '/home/ubuntu/SENTINEL/result.csv'

# 1. Ansible 플레이북 실행 (apache.yml)
print("Ansible apache.yml 실행 중...")
subprocess.run(['ansible-playbook', 'apache.yml'], cwd='/home/ubuntu/SENTINEL/apache', check=True)

# 2. Ansible 플레이북 실행 (apache_action.yml)
print("Ansible apache_action.yml 실행 중...")
subprocess.run(['ansible-playbook', 'apache_action.yml'], cwd='/home/ubuntu/SENTINEL/apache', check=True)

# 3. apache.json 파일 읽기
with open(apache_json_path, 'r') as apache_file:
    apache_data = json.load(apache_file)

# 4. apache_action.json 파일 읽기
with open(apache_action_json_path, 'r') as apache_action_file:
    apache_action_data = json.load(apache_action_file)

# 5. CSV 파일 초기화 및 "Apache" 소제목 추가
with open(csv_file_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # "Apache"라는 소제목 추가
    writer.writerow(["Apache"])
    
    # 열 제목 추가 (취약여부 포함)
    fieldnames = list(apache_data[0].keys()) + ["조치 후 취약여부"]
    writer.writerow(fieldnames)

    # 6. apache.json 데이터 작성
    for item in apache_data:
        writer.writerow(list(item.values()) + [""])  # "조치 후 취약여부"는 일단 빈칸으로 두기

# 7. apache_action.json 데이터를 "조치 후 취약여부"로 추가
# 7. apache_action.json 데이터가 비어있는 경우 예외 처리
if not apache_action_data:  # apache_action.json 파일이 [] (빈 배열)일 경우
    print("apache_action.json 파일이 비어 있습니다. '조치 후 취약여부'를 빈 값으로 설정합니다.")

# 8. 해당 id와 맞는 행 찾아서 업데이트
with open(csv_file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
    reader = list(csv.reader(csvfile))  # 기존 csv 데이터 읽기
    header = reader[0]  # 첫 번째 행을 헤더로 저장
    rows = reader[1:]  # 나머지는 데이터로 저장

    # apache.json 데이터는 무조건 CSV에 기록됨
    for row in rows:
        # apache_action.json 데이터가 비어있으면 "조치 후 취약여부" 열을 빈칸으로 유지
        if apache_action_data:  # apache_action.json이 비어있지 않은 경우에만 처리
            for action_item in apache_action_data:
                if row[0] == str(action_item['id']):  # ID가 일치하는지 확인
                    row[-1] = action_item.get('취약', '')  # "조치 후 취약여부" 값을 업데이트
                    break
        else:
            # apache_action.json이 비어있을 때는 "조치 후 취약여부"를 빈 값으로 유지
            row[-1] = ""  # 빈칸으로 유지

# 9. 수정된 데이터를 다시 파일에 쓰기
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)  # 첫 번째 행을 다시 씀
    writer.writerows(rows)  # 수정된 데이터 다시 쓰기

print(f"CSV 파일이 {csv_file_path}에 저장되었습니다.")


# 10. CSV 파일 인코딩 변경 (utf-8-sig로 다시 저장)
with open(csv_file_path, "r", encoding="utf-8-sig") as file:
    content = file.read()  # 파일 내용을 읽음

# utf-8-sig 인코딩으로 다시 저장 (파일 내용을 변경하지 않고 인코딩만 변경)
with open(csv_file_path, "w", encoding="utf-8-sig") as file:
    file.write(content)

# 이메일 전송

# MIME 객체 생성
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# 이메일 본문
body = "CSV 파일을 첨부합니다."
message.attach(MIMEText(body, "plain"))

# 파일 첨부
with open(csv_file_path, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(csv_file_path)}")
    message.attach(part)

# SMTP 서버 설정 및 이메일 전송
try:
    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("이메일 전송 성공")
except Exception as e:
    print(f"이메일 전송 실패: {e}")