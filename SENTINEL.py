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
sender_email = "gyudol99@naver.com"
receiver_email = "gyudol99@naver.com"
password = "dkaghdkagh1."
subject = "취약점 진단 및 조치 결과"

# 파일 경로 설정
csv_file_path = '/home/ubuntu/SENTINEL/result.csv'

# 점검 섹션 정보 설정
sections = [
    {
        "name": "Apache",
        "ansible_playbooks": ['apache.yml', 'apache_action.yml'],
        "json_path": '/home/ubuntu/SENTINEL/apache/apache.json',
        "action_json_path": '/home/ubuntu/SENTINEL/apache/apache_action.json'
    },
    {
        "name": "Linux",
        "ansible_playbooks": ['linux.yml', 'linux_action.yml'],
        "json_path": '/home/ubuntu/SENTINEL/linux/linux.json',
        "action_json_path": '/home/ubuntu/SENTINEL/linux/linux_action.json'
    }
    # {
    #     "name": "DB",
    #     "ansible_playbooks": ['db.yml', 'db_action.yml'],
    #     "json_path": '/home/ubuntu/SENTINEL/db/db.json',
    #     "action_json_path": '/home/ubuntu/SENTINEL/db/db_action.json'
    # }
]

# CSV 초기화
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile:
    pass

# 각 섹션 점검 및 CSV에 기록
for section in sections:
    section_name = section["name"]
    json_path = section["json_path"]
    action_json_path = section["action_json_path"]
    
    # Ansible 플레이북 실행
    for playbook in section["ansible_playbooks"]:
        if os.path.exists(os.path.join(os.path.dirname(json_path), playbook)):
            print(f"{section_name} {playbook} 실행 중...")
            subprocess.run(['ansible-playbook', playbook], cwd=os.path.dirname(json_path), check=True)
        else:
            print(f"{section_name}의 {playbook} 파일이 존재하지 않아 실행을 건너뜁니다.")
    
    # JSON 파일 읽기
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    # action.yml 파일이 존재하는 경우에만 action.json 읽기
    if os.path.exists(action_json_path):
        try:
            with open(action_json_path, 'r') as action_file:
                content = action_file.read().strip()
                if content:
                    action_data = json.loads(content)
                else:
                    action_data = []  # 비어있을 경우 빈 리스트로 처리
        except json.JSONDecodeError:
            action_data = []
    else:
        print(f"{section_name}의 action.json 파일이 존재하지 않아 '조치 후 취약여부'를 빈 값으로 설정합니다.")
        action_data = []  # action.json이 없으면 빈 리스트로 처리

    # CSV에 데이터를 추가하는 부분을 mode='a'로 열기
    with open(csv_file_path, mode='a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # 섹션 제목 및 열 제목 추가
        writer.writerow([section_name])
        fieldnames = list(data[0].keys()) + ["조치 후 취약여부"]
        writer.writerow(fieldnames)

        # JSON 데이터 추가
        rows = []
        for item in data:
            rows.append(list(item.values()) + [""])  # "조치 후 취약여부"는 빈칸으로 두기

        # 조치 후 취약여부 열 업데이트
        for i, row in enumerate(rows):
            if action_data:  # action 데이터가 있을 경우
                for action_item in action_data:
                    if str(data[i]['id']) == str(action_item['id']):
                        row[-1] = action_item.get("취약", "")
                        break
            else:
                row[-1] = ""  # 비어있을 경우 빈 값 유지

        writer.writerows(rows)

    print(f"{section_name} 결과가 {csv_file_path}에 추가되었습니다.")

print(f"모든 점검 결과가 {csv_file_path}에 저장되었습니다.")

# 이메일 전송
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
body = "각 점검 항목의 진단 및 조치 결과가 포함된 CSV 파일을 첨부합니다."
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
