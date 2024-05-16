import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib import request
from bs4 import BeautifulSoup
from urllib.parse import quote
import sqlite3

# CSV 파일 경로를 지정(현재 디렉토리)
csv_path = "player.csv"

# CSV 파일을 읽어와 DataFrame으로 저장(encoding방식:euc-kr)
data = pd.read_csv(csv_path, encoding='euc-kr')

#csv에서 선수 정보 찾기
def find_info(name):
    while True:
        # 이름이 포함된 모든 행 찾기
        matching_rows = data[data['이름'] == name]
        #이름이 없으면 다시 입력
        if len(matching_rows) == 0:
            print(f"{name}에 대한 정보를 찾을 수 없어요. 다시 입력해주세요.")
            name = input("선수 이름을 입력해주세요: ")
        else:
            break

    # 동명이인이 있는 경우
    if len(matching_rows) > 1:
        info_list = []
        for i, (_, row) in enumerate(matching_rows.iterrows()):
            info_list.append(f"{i + 1}. 팀: {row['팀']}, 생년월일: {row['생년월일']}")
        names_list = "\n".join(info_list)
        input_index = int(input(f"{name}에 대한 동명이인 목록:\n{names_list}\n선수의 번호를 입력하세요: ")) - 1

        if 0 <= input_index < len(matching_rows):
            selected_player = matching_rows.iloc[input_index]
            team = selected_player['팀']
            birthdate = selected_player['생년월일']
            return f"{name}의 정보 - 팀: {team}, 생년월일: {birthdate}", team, birthdate, name
        else:
            return "유효하지 않은 번호를 입력했어요.", None, None, None

    # 동명이인이 없는 경우
    team = matching_rows.iloc[0]['팀']
    birthdate = matching_rows.iloc[0]['생년월일']
    return f"{name}의 정보 - 팀: {team}, 생년월일: {birthdate}", team, birthdate, name

# 사용자에게 이름 입력 받기
input_name1 = input("선수 1의 이름을 입력해주세요: ")
result1, team_value1, birthdate_value1, input_name1 = find_info(input_name1)
print(result1)
input_name2 = input("선수 2의 이름을 입력해주세요 : ")
result2, team_value2, birthdate_value2, input_name2 = find_info(input_name2)
print(result2)


# 첫번째 선수의 구종 데이터 크롤링(이름과 생년월일 이용)
co_player1=quote(input_name1, 'utf-8')
birth1=quote(birthdate_value1,'utf-8')
site1 = request.urlopen('http://www.statiz.co.kr/player.php?opt=10&sopt=0&name='+co_player1+'&birth='+birth1+'&re=2&da=1&lg=&year=2023')
byte_data1 = site1.read()
text_data1 = byte_data1.decode()

# BeautifulSoup을 사용하여 HTML 파싱
soup1 = BeautifulSoup(text_data1, 'html.parser')

# 필요한 데이터가 들어 있는 특정 태그를 찾기
data_tags1 = soup1.select('tr.oddrow_stz td b')

data_li_1 = []
# 추출한 데이터 출력
for data in data_tags1[1:]:
    data_li_1.append(float(data.text))
#기타 데이터(기타=싱커+너클+기타)
data_li_1[5] = data_li_1[5] + data_li_1[6] + data_li_1[7]
del(data_li_1[6:])

# 그래프 그리기
categories = ['직구', '슬라이더', '커브', '체인지업', '스플리터', '기타']
value1 = data_li_1

#SQLite 연결
con=sqlite3.connect(r"C:\Users\boo\데이터분석을위한파이썬/프로젝트/baseball_pitcher.db")
cur=con.cursor()

#SQLite에서 player라는 테이블이 있는지 확인
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player'")
existing_table = cur.fetchone()

if not existing_table:
    cur.execute("""CREATE TABLE player(name char(15), team char(10), birth char(10), FF REAL, SL REAL,
                 CU REAL, CH REAL, SF REAL, ETC REAL) """)

cur.execute("INSERT INTO player VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (input_name1, team_value1, birthdate_value1,
             value1[0], value1[1], value1[2], value1[3], value1[4], value1[5]))
con.commit()

# 두번째 선수
co_player2=quote(input_name2, 'utf-8')
birth2=quote(birthdate_value2,'utf-8')
site2 = request.urlopen('http://www.statiz.co.kr/player.php?opt=10&sopt=0&name='+co_player2+
                        '&birth='+birth2+'&re=2&da=1&lg=&year=2023')
byte_data2 = site2.read()
text_data2 = byte_data2.decode()

# BeautifulSoup을 사용하여 HTML 파싱
soup2 = BeautifulSoup(text_data2, 'html.parser')

# 필요한 데이터가 들어 있는 특정 태그를 찾기
data_tags2 = soup2.select('tr.oddrow_stz td b')

data_li_2 = []
# 추출한 데이터 출력
for data in data_tags2[1:]:
    data_li_2.append(float(data.text))
data_li_2[5] = data_li_2[5] + data_li_2[6] + data_li_2[7]
del(data_li_2[6:])

# 그래프 그리기
value2 = data_li_2

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player'")
existing_table = cur.fetchone()
if not existing_table:
    cur.execute("""CREATE TABLE player(name char(15), team char(10), birth char(10), FF REAL, 
                SL REAL, CU REAL, CH REAL, SF REAL, ETC REAL) """)
cur.execute("INSERT INTO player VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (input_name2, team_value2, birthdate_value2,
             value2[0], value2[1], value2[2], value2[3], value2[4], value2[5]))
con.commit()

# 첫번째 선수 데이터 가져오기
cur.execute("SELECT * FROM player WHERE name=? AND birth=?", (input_name1,birthdate_value1))
row1 = cur.fetchone()
values1 = [row1[3], row1[4], row1[5], row1[6], row1[7], row1[8]]

# 두번째 선수 데이터 가져오기
cur.execute("SELECT * FROM player WHERE name=? AND birth=?", (input_name2,birthdate_value2))
row2 = cur.fetchone()
values2 = [row2[3], row2[4], row2[5], row2[6], row2[7], row2[8]]

# SQLite 연결 종료
con.close()

# 방사형 그래프의 데이터 포인트 갯수
num_points = len(categories)

# 각 데이터 포인트에 대해 파이조각으로 표시(0부터~2파이까지 num_points개의 점으로 나눔, endoint=False로 마지막 각도값포함x)
theta = np.linspace(0.0, 2*np.pi, num_points, endpoint=False)
radii1 = values1
radii2 = values2

# 데이터 포인트의 이름을 정렬된 순서대로 표시
sorted_categories = [categories[i] for i in np.argsort(theta)]

#글씨체 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 그래프 그리기
fig, ax = plt.subplots(subplot_kw=dict(polar=True))

# 간격 조절
width = 2*np.pi / num_points

# 데이터1에 대한 막대 그래프 그리기
bars1 = ax.bar(theta, radii1, width=width, alpha=0.7, align='center',
               color='lightcoral', label=f"{input_name1} ({team_value1})")

# 데이터2에 대한 막대 그래프 그리기
bars2 = ax.bar(theta, radii2, width=width, alpha=0.7, align='center',
               color='lightblue', label=f"{input_name2} ({team_value2})")

# 데이터 포인트의 이름을 각 파이조각 중앙에 표시
ax.set_xticks(theta)
ax.set_xticklabels(sorted_categories)

# 구분선 추가 (각 값 사이에)
angle_between_lines = 2*np.pi / num_points

for i in range(num_points):
    current_angle = i * angle_between_lines
    next_angle = (i + 1) * angle_between_lines
    middle_angle = (current_angle + next_angle) / 2

    ax.plot([middle_angle, middle_angle], [0, max(values1 + values2) + 5], linestyle='-', color='gray', alpha=0.4)

    # 데이터에 대한 수치를 부채꼴 위에 표시
    label_position = (current_angle + next_angle) / 2 - np.radians(30)
    label_radius = max(radii1[i], radii2[i]) + 2
    ax.text(label_position, label_radius + 20, str(values1[i]), ha='center', va='center', color='hotpink')
    ax.text(label_position, label_radius + 2, str(values2[i]), ha='center', va='center', color='skyblue')

# 레이디얼 라인 삭제
ax.spines['polar'].set_visible(False)

# 그리드 라인 제거
ax.xaxis.grid(False)

# 겉의 육각형 유지
ax.set_facecolor('none')

# 축 숨기기
ax.set_yticklabels([])

# 범례 추가
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))

#그래프 보여주기
plt.show()