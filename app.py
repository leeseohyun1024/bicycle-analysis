import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="서울시 따릉이 분석 대시보드", layout="wide")

# 2. 데이터베이스 존재 여부 확인
DB_PATH = "bicycle.db"

if not os.path.exists(DB_PATH):
    st.error("⚠️ 'bicycle.db' 파일을 찾을 수 없습니다!")
    st.stop()

def run_query(q):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(q, conn)

# 메인 타이틀
st.title("🚲 서울시 공공자전거 데이터 분석 대시보드")

# --- 1. 연령대와 성별 조합 ---
st.divider()
st.header("1. 가장 많이 대여하는 연령대와 성별")

sql1 = """
SELECT 연령대코드, 성별, SUM(이용건수) as 총이용건수
FROM 이용정보
WHERE 성별 IN ('M', 'F')
GROUP BY 연령대코드, 성별
ORDER BY 총이용건수 DESC
"""
df1 = run_query(sql1)

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    fig1 = px.bar(df1, x="연령대코드", y="총이용건수", color="성별", 
                 title="연령대별 성별 이용 비중", barmode="group",
                 color_discrete_map={'M':'#1f77b4', 'F':'#e377c2'})
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("🔍 분석 정보")
    st.info("""
    **인사이트:**
    - 30대의 남성이 가장 많은 대여를 했으며, 대부분의 연령대에서 남성의 이용건수가 여성의 이용건수보다 높게 나타난다.
    """)


# --- 2. 대여 구분별 평균 이용시간 차이 ---
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
    fig2 = px.bar(df2, x='대여구분코드', y='평균이용시간', color='대여구분코드', 
                 title="대여구분별 평균 이용시간")
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 분석 정보")
    st.info("""
    **인사이트:**
    1. **정기권 사용자의 압도적 비중** : 정기권이 전체의 절반에 가까운 비중을 차지하고 있으며 이는 해당 서비스가 일회성보다는 반복적이고 일상적인 출퇴근 등에 사용되고 있다는 것을 시사한다.
    2. **개별적인 일일권 사용자들의 총 이용시간 합계**도 무시할 수 없다. 이는 주말 나들이객이나 비정기적 이용자의 수요도 탄탄함을 보여준다.
    3. **가족권은 비중이 낮은 것**으로 보아, 단체나 가족 단위의 이용보다는 개인 중심의 이용이 주를 이루고 있다고 판단할 수 있다.
    4. 따라서 정기권 사용자가 많으므로 이들을 위한 **혜택을 강화해 '락인 효과'를 지속**해야 하며 비중이 낮은 가족권에 대한 홍보가 필요하다.
    """)


# --- 3. 주말 vs 평일 이용 패턴 분석 (첫 번째 코드 방식 적용) ---
st.divider()
st.header("3. 주말 vs 평일 이용 패턴 분석")

sql3 = "SELECT 대여일자, 이용건수 FROM 이용정보"
df3_raw = run_query(sql3)

# 날짜 데이터 처리
df3_raw['날짜'] = pd.to_datetime(df3_raw['대여일자'], errors='coerce')
df3_raw['요일'] = df3_raw['날짜'].dt.dayofweek
# 요일 컬럼을 기반으로 '평일'과 '주말'을 확실히 구분
df3_raw['날짜구분'] = df3_raw['요일'].apply(lambda x: '주말' if x >= 5 else '평일')

# 데이터 그룹화 (첫 번째 답변 방식)
period_df = df3_raw.groupby('날짜구분').size().reset_index(name='대여건수')

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    # [첫 번째 답변에서 제시한 차트 코드 적용]
    fig3 = px.bar(period_df, 
                 x='대여건수', 
                 y='날짜구분', 
                 color='날짜구분',
                 orientation='h', # 가로 막대
                 title="평일 vs 주말 대여 비중 비교",
                 color_discrete_map={'평일': '#636EFA', '주말': '#EF553B'})
    
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 분석 정보")
    st.write("주말과 평일의 데이터를 비교하여 분석한 결과입니다.")
    st.info("""
    **분석 포인트:**
    - 위 차트에서 평일과 주말의 막대 그래프가 모두 표시되는지 확인하십시오. 
    - 만약 주말 막대가 여전히 보이지 않는다면, 데이터베이스 내의 '대여일자' 값이 모두 평일 날짜로만 구성되어 있을 가능성이 높습니다.
    """)

st.caption("© 2024 따릉이 데이터 멘토링. 모든 차트는 실시간 SQLite 데이터를 기반으로 합니다.")
