import os
import sys
from datetime import datetime

def main():

    print("Hello from project!")
    print(sys.version)
    # 시스템 로그 파일
    system_log = datetime.now().strftime("logs/system_%y%m%d.log")
    # Streamlit 실행
    command = rf'streamlit run 💫main_page.py >> {system_log} 2>&1 '
    os.system(command)
    # import test
    # test.run()
    


if __name__ == "__main__":
    main()
