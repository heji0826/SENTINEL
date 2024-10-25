import json
import csv
import os
import subprocess

# 파일 경로 설정
apache_json_path = '/home/ubuntu/SENTINEL/apache/apache.json'
apache_action_json_path = '/home/ubuntu/SENTINEL/apache/apache_action.json'
csv_file_path = '/home/ubuntu/share/result.csv'

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
# 8. 해당 id와 맞는 행 찾아서 업데이트
with open(csv_file_path, mode='r+', newline='') as csvfile:
    reader = list(csv.reader(csvfile))  # 기존 csv 데이터 읽기
    writer = csv.writer(csvfile)
    
    # apache_action.json의 데이터를 각 id에 맞게 추가
    for action_item in apache_action_data:
        for row in reader:
            if row[0] == str(action_item['id']):  # ID가 일치하는지 확인 (csv의 id는 문자열 형태일 수 있음)
                # '조치 후 취약여부' 컬럼에 true/false 값을 넣고 나머지는 빈칸으로 유지
                row[-1] = action_item['취약']  # 마지막 열에 true/false 값 추가
                break
    
    # 파일 다시 쓰기
    csvfile.seek(0)
    writer.writerows(reader)

print(f"CSV 파일이 {csv_file_path}에 저장되었습니다.")
