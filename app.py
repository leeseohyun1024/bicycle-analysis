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
    # 요청하신 인사이트 내용으로 교체
    st.info("""
    **인사이트:**
    - 30대의 남성이 가장 많은 대여를 했으며, 대부분의 연령대에서 남성의 이용건수가 여성의 이용건수보다 높게 나타난다.
    """)


# --- 차트 2: 대여 구분별 평균 이용시간 차이 ---
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
    # 시각화: 파이 차트
    fig2 = px.pie(df2, values='평균이용시간', names='대여구분코드', hole=0.4,
                 title="대여 구분별 평균 이용시간 비교",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 분석 정보")
    st.code(sql2, language='sql')
    # 요청하신 인사이트 내용으로 교체
    st.info("""
    **인사이트:**
    1. **정기권 사용자의 압도적 비중** : 정기권이 전체의 절반에 가까운 비중을 차지하고 있으며 이는 해당 서비스가 일회성보다는 반복적이고 일상적인 출퇴근 등에 사용되고 있다는 것을 시사한다.
    2. **개별적인 일일권 사용자들의 총 이용시간 합계**도 무시할 수 없다. 이는 주말 나들이객이나 비정기적 이용자의 수요도 탄탄함을 보여준다.
    3. **가족권은 비중이 낮은 것**으로 보아, 단체나 가족 단위의 이용보다는 개인 중심의 이용이 주를 이루고 있다고 판단할 수 있다.
    4. 따라서 정기권 사용자가 많으므로 이들을 위한 **혜택을 강화해 '락인 효과'를 지속**해야 하며 비중이 낮은 가족권에 대한 홍보가 필요하다.
    """)


# --- 차트 3: 주말 vs 평일 이용 패턴 분석 ---
st.divider()
st.header("3. 주말 vs 평일 이용 패턴 분석")

sql3 = """
SELECT 대여일자, 이용건수, 이용시간 FROM 이용정보
"""
df3_raw = run_query(sql3)

# 날짜 처리 및 주말/평일 구분
df3_raw['날짜'] = pd.to_datetime(df3_raw['대여일자'], errors='coerce')
df3_raw['요일'] = df3_raw['날짜'].dt.dayofweek 
df3_raw['구분'] = df3_raw['요일'].apply(lambda x: '주말' if x >= 5 else '평일')

# 이용건수 합계 계산
df3 = df3_raw.groupby('구분').agg({'이용건수':'sum'}).reset_index()

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    # [수정] 주말 가로막대가 나타나도록 가로 막대 그래프(orientation='h')로 변경
    fig3 = px.bar(df3, 
                 x='이용건수', 
                 y='구분', 
                 color='구분',
                 orientation='h',  # 가로 막대 설정
                 text_auto='.2s', 
                 title="평일 vs 주말 총 이용건수 비교",
                 color_discrete_map={'평일':'#636EFA', '주말':'#EF553B'})
    
    # y축 순서를 평일이 위로 오거나 주말이 위로 오게 조정 (데이터가 둘 다 보이게 함)
    fig3.update_layout(yaxis={'categoryorder':'total ascending'}) 
    
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 분석 정보")
    st.write("*(날짜 데이터를 기반으로 평일과 주말을 구분하여 집계)*")
    st.code("df['구분'] = df['요일'].apply(lambda x: '주말' if x >= 5 else '평일')", language='python')
    st.info("""
    **인사이트:**
    1. 데이터 상의 **평일과 주말 이용 비중**을 한눈에 확인할 수 있습니다.
    2. 만약 주말 막대가 보이지 않는다면, 원본 데이터의 '대여일자'가 특정 요일에만 치우쳐 있는지 확인이 필요합니다.
    """)

st.caption("© 2024 따릉이 데이터 멘토링. 모든 차트는 실시간 SQLite 데이터를 기반으로 합니다.")
