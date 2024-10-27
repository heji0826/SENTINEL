# SENTINEL

# 리눅스, 아파치, DB 보안 점검 자동화 서비스

## 개요

이 프로젝트는 [KISA](https://isms.kisa.or.kr/main/csap/notice/)에서 제공하는 가이드라인을 기반으로 리눅스, 아파치, 데이터베이스 시스템의 보안 점검을 자동화합니다. 시스템의 취약점을 점검하고, 취약하지 않도록 조치한 후 엑셀 리포트를 생성하는 서비스를 제공합니다.

## 주요 기능

- **자동화된 점검**: 리눅스, 아파치, 데이터베이스 시스템에 대한 종합적인 보안 점검을 자동으로 수행합니다.
- **KISA 가이드라인 준수**: KISA의 보안 가이드라인에 따라 시스템의 취약점을 분석하고 조치합니다.
- **엑셀 리포트 생성**: 점검 결과를 바탕으로 취약점 상태를 엑셀 파일로 출력합니다.

## 사용 방법

### 1. 프로젝트 클론

다음 명령어를 사용하여 이 리포지토리를 클론합니다:

```bash
git clone https://github.com/heji0826/SENTINEL.git
cd SENTINEL

### 2. 사용자 이름 설정

아래 경로에 위치한 `ansible.cfg` 파일에서 `[defaults]` 섹션의 `remote_user` 항목을 점검 대상 Linux 서버의 사용자 이름으로 변경합니다.

- `SENTINEL/DB/ansible.cfg`
- `SENTINEL/apache/ansible.cfg`
- `SENTINEL/linux/ansible.cfg`

**예시:**

\`\`\`ini
[defaults]
remote_user = <점검 대상 Linux 사용자 이름>
\`\`\`

### 3. IP 주소 설정

아래 `inventory` 파일에서 `intranetweb`과 `internetweb`의 IP 주소를 점검 대상 Linux 서버의 IP 주소로 변경합니다.

- `SENTINEL/DB/inventory`
- `SENTINEL/apache/inventory`
- `SENTINEL/linux/inventory`

**예시:**

\`\`\`ini
[intranetweb]
<점검 대상 Linux 서버 IP 주소>

[internetweb]
<점검 대상 Linux 서버 IP 주소>
\`\`\`

### 4. 이메일 설정

`SENTINEL/SENTINEL.py` 파일에서 아래 변수들을 설정해 결과를 수신할 이메일과 인증 정보를 입력합니다.

- `sender_email`: 발신자 이메일 주소
- `receiver_email`: 수신자 이메일 주소
- `password`: 발신자 이메일 계정의 비밀번호

**예시:**

\`\`\`python
sender_email = "<발신 이메일 주소>"
receiver_email = "<수신 이메일 주소>"
password = "<발신 이메일 계정 비밀번호>"
\`\`\`

## 스크립트 실행

모든 설정을 완료한 후, `SENTINEL/` 디렉토리에서 다음 명령어로 스크립트를 실행합니다.

\`\`\`bash
cd SENTINEL/
python3 SENTINEL.py
\`\`\`

스크립트가 실행되면 `result.csv` 파일이 생성되고, 지정한 수신 이메일 주소로 결과 파일이 전송됩니다.

