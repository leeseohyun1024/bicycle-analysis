import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="자전거 대여 데이터 분석", layout="wide")

st.title("🚲 자전거 대여 데이터 분석 리포트")

# --- 데이터 로드 (사용자의 환경에 맞게 수정 필요) ---
# @st.cache_data
# def load_data():
#     df = pd.read_csv('your_data.csv') # 데이터 파일 경로
#     # 날짜 데이터 변환 (주말/평일 구분을 위해)
#     df['대여일자'] = pd.to_datetime(df['대여일자'])
#     return df

# df = load_data()

# 임시 예시 데이터 생성 (작동 확인용 - 실제 데이터가 있다면 위 로드 부분을 사용하세요)
# 실제 파일이 있으시다면 이 부분은 삭제하고 기존 로직을 쓰시면 됩니다.
if 'df' not in locals():
    data = {
        '연령대': ['20대', '20대', '30대', '30대', '40대', '40대'] * 10,
        '성별': ['남', '여', '남', '여', '남', '여'] * 10,
        '대여구분': ['정기권', '일일권', '정기권', '일일권', '가족권', '정기권'] * 10,
        '이용시간': [15, 20, 25, 30, 40, 10] * 10,
        '대여일자': pd.to_datetime(['2024-05-01', '2024-05-04', '2024-05-02', '2024-05-05', '2024-05-03', '2024-05-04'] * 10)
    }
    df = pd.DataFrame(data)

# 1. 가장 많이 대여하는 연령대와 성별
st.header("1. 가장 많이 대여하는 연령대와 성별")

# 데이터 가공
age_gender_df = df.groupby(['연령대', '성별']).size().reset_index(name='대여건수')
fig1 = px.bar(age_gender_df, x='연령대', y='대여건수', color='성별', barmode='group', title="연령대별/성별 대여 건수")
st.plotly_chart(fig1, use_container_width=True)

# 인사이트 수정
st.info("""
**💡 인사이트**
- 30대의 남성이 가장 많은 대여를 했으며, 대부분의 연령대에서 남성의 이용건수가 여성의 이용건보다 높게 나타난다.
""")


# 2. 대여구분별 평균 이용시간 차이
st.header("2. 대여구분별 평균 이용시간 차이")

# 데이터 가공
usage_type_df = df.groupby('대여구분')['이용시간'].mean().reset_index()
fig2 = px.bar(usage_type_df, x='대여구분', y='이용시간', color='대여구분', title="대여구분별 평균 이용시간")
st.plotly_chart(fig2, use_container_width=True)

# 인사이트 수정
st.info("""
**💡 인사이트**
1. **정기권 사용자의 압도적 비중** : 정기권이 전체의 절반에 가까운 비중을 차지하고 있으며 이는 해당 서비스가 일회성보다는 반복적이고 일상적인 출퇴근 등에 사용되고 있다는 것을 시사한다.
2. **개별적인 일일권 사용자들의 총 이용시간 합계**도 무시할 수 없다. 이는 주말 나들이객이나 비정기적 이용자의 수요도 탄탄함을 보여준다.
3. **가족권은 비중이 낮은 것**으로 보아, 단체나 가족 단위의 이용보다는 개인 중심의 이용이 주를 이루고 있다고 판단할 수 있다.
4. 따라서 정기권 사용자가 많으므로 이들을 위한 **혜택을 강화해 '락인 효과'를 지속**해야 하며 비중이 낮은 가족권에 대한 홍보가 필요하다.
""")


# 3. 주말 vs 평일 이용 패턴 분석
st.header("3. 주말 vs 평일 이용 패턴 분석")

# 평일/주말 구분 컬럼 생성 (월~목: 0~4, 금~일: 5~6)
# dt.dayofweek: 0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일
df['요일'] = df['대여일자'].dt.dayofweek
df['날짜구분'] = df['요일'].apply(lambda x: '주말' if x >= 5 else '평일')

# 데이터 가공 (날짜구분별 대여 건수)
period_df = df.groupby('날짜구분').size().reset_index(name='대여건수')

# [수정 포인트] 주말과 평일이 모두 나타나도록 가로 막대 그래프 설정
fig3 = px.bar(period_df, 
             x='대여건수', 
             y='날짜구분', 
             color='날짜구분',
             orientation='h', # 가로 막대
             title="평일 vs 주말 대여 비중 비교",
             color_discrete_map={'평일': '#636EFA', '주말': '#EF553B'}) # 색상 지정

st.plotly_chart(fig3, use_container_width=True)

st.write("주말과 평일의 데이터를 비교하여 분석한 결과입니다.")
