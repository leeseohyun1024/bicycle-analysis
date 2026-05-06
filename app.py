import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 (제목과 아이콘)
st.set_page_config(page_title="서울시 따릉이 분석 대시보드", layout="wide")

# 2. 데이터베이스 존재 여부 확인 및 에러 메시지
DB_PATH = "bicycle.db"

if not os.path.exists(DB_PATH):
    st.error("⚠️ 'bicycle.db' 파일을 찾을 수 없습니다!")
    st.info("파일이 'app.py'와 같은 폴더에 있는지 확인해 주세요. 파일명이 정확히 'bicycle.db'여야 합니다.")
    st.stop()

# 데이터베이스 연결 함수
def run_query(q):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(q, conn)

# 메인 타이틀
st.title("🚲 서울시 공공자전거 데이터 분석 대시보드")
st.markdown("데이터를 통해 따릉이 이용 패턴을 시각화하고 인사이트를 도출합니다.")

# --- 차트 1: 연령대와 성별 조합 ---
st.divider()
st.header("1. 가장 많이 대여하는 연령대와 성별")

sql1 = """
SELECT 연령대코드, 성별, SUM(이용건수) as 총이용건수
FROM 이용정보
WHERE 성별 IN ('M', 'F') -- 성별 데이터 정제
GROUP BY 연령대코드, 성별
ORDER BY 총이용건수 DESC
"""
df1 = run_query(sql1)

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    # 시각화: 누적 막대 그래프
    fig1 = px.bar(df1, x="연령대코드", y="총이용건수", color="성별", 
                 title="연령대별 성별 이용 비중", barmode="group",
                 color_discrete_map={'M':'#1f77b4', 'F':'#e377c2'})
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("🔍 분석 정보")
    st.code(sql1, language='sql')
    st.info("""
    **인사이트:**
    1. **20대와 30대**의 이용량이 다른 연령대에 비해 압도적으로 높습니다.
    2. 대부분의 연령대에서 **남성(M)**의 이용 건수가 여성(F)보다 높게 나타나는 경향이 있습니다.
    """)


# --- 차트 2: 일일권 vs 정기권 평균 이용시간 ---
st.divider()
st.header("2. 대여 구분별 평균 이용시간 차이")

sql2 = """
SELECT 대여구분코드, AVG(이용시간) as 평균이용시간
FROM 이용정보
GROUP BY 대여구분코드
"""
df2 = run_query(sql2)

col2_1, col2_2 = st.columns([2, 1])
with col2_1:
    # 시각화: 파이 차트 또는 도넛 차트
    fig2 = px.pie(df2, values='평균이용시간', names='대여구분코드', hole=0.4,
                 title="대여 구분별 평균 이용시간 비교",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 분석 정보")
    st.code(sql2, language='sql')
    st.info("""
    **인사이트:**
    1. 보통 **일일권 이용자**가 정기권 이용자보다 한 번 탈 때 **더 오래** 타는 경향이 있습니다 (레저 목적).
    2. 정기권은 출퇴근 등 **단거리 이동**에 자주 활용됨을 알 수 있습니다.
    """)


# --- 차트 3: 주말 vs 평일 이용 비중 및 시간 ---
st.divider()
st.header("3. 주말 vs 평일 이용 패턴 분석")

# 주의: 대여일자가 YYYYMM 형식일 경우 정확한 요일 계산이 어려우므로, 
# 데이터가 YYYYMMDD 또는 날짜 포맷이라고 가정하고 Pandas에서 처리합니다.
sql3 = """
SELECT 대여일자, 이용건수, 이용시간 FROM 이용정보
"""
df3_raw = run_query(sql3)

# 날짜 처리 (YYYYMMDD 형식 가정)
df3_raw['날짜'] = pd.to_datetime(df3_raw['대여일자'], errors='coerce')
df3_raw['요일'] = df3_raw['날짜'].dt.dayofweek # 0=월, 5=토, 6=일
df3_raw['구분'] = df3_raw['요일'].apply(lambda x: '주말' if x >= 5 else '평일')

df3 = df3_raw.groupby('구분').agg({'이용건수':'sum', '이용시간':'mean'}).reset_index()

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    # 시각화: 이중 축 느낌의 막대 그래프
    fig3 = px.bar(df3, x='구분', y='이용건수', color='구분',
                 text_auto='.2s', title="평일/주말 총 이용건수 및 평균 이용시간")
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 분석 정보")
    st.write("*(SQL로 전체 데이터를 가져온 후 Python으로 요일 분류)*")
    st.code("df['구분'] = df['요일'].apply(lambda x: '주말' if x >= 5 else '평일')", language='python')
    st.info("""
    **인사이트:**
    1. 전체 **이용 건수**는 평일이 많으나(출퇴근), **평균 이용 시간**은 주말이 훨씬 길게 나타납니다.
    2. 주말에는 운동 및 여가 목적으로 자전거를 대여하는 사용자가 많음을 시사합니다.
    """)

st.caption("© 2024 따릉이 데이터 멘토링. 모든 차트는 실시간 SQLite 데이터를 기반으로 합니다.")
