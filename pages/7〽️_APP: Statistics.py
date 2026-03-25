import streamlit as st
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Easy T-test Analyzer", layout="centered")

st.title("📊 Google Sheets T-test Analyzer")
st.markdown("""
구글 시트의 공유 URL을 입력하면 데이터를 분석합니다.  
데이터는 **첫 번째 열에 집단 구분(Group), 두 번째 열에 수치(Score)**가 있어야 합니다.
""")

# --- 2. 구글 시트 URL 입력 및 데이터 로드 ---
sheet_url = st.text_input("구글 시트 주소를 붙여넣으세요:", 
                         placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing")

def get_google_sheet(url):
    try:
        # 구글 시트 URL을 CSV 다운로드 형식으로 변환
        file_id = url.split('/')[-2]
        raw_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
        return pd.read_csv(raw_url)
    except:
        return None

if sheet_url:
    df = get_google_sheet(sheet_url)
    
    if df is not None:
        st.success("데이터를 성공적으로 불러왔습니다!")
        st.write("### 📋 데이터 미리보기")
        st.dataframe(df.head())

        # --- 3. 분석 변수 선택 ---
        st.divider()
        cols = df.columns.tolist()
        group_col = st.selectbox("집단을 구분하는 열(독립변수)을 선택하세요:", cols)
        value_col = st.selectbox("분석할 수치 열(종속변수)을 선택하세요:", cols)

        groups = df[group_col].unique()

        if len(groups) == 2:
            st.write(f"**분석 대상 집단:** {groups[0]} vs {groups[1]}")
            
            # 데이터 분리
            g1 = df[df[group_col] == groups[0]][value_col]
            g2 = df[df[group_col] == groups[1]][value_col]

            # --- 4. T-test 수행 ---
            t_stat, p_val = stats.ttest_ind(g1, g2, nan_policy='omit')

            # --- 5. 결과 보고 및 시각화 ---
            st.subheader("📝 분석 결과 보고")
            
            col1, col2 = st.columns(2)
            col1.metric("T-value", f"{t_stat:.4f}")
            col2.metric("P-value", f"{p_val:.4f}")

            # 해석 (APA 스타일 서술 예시)
            st.info("#### 💡 통계적 해석")
            is_significant = "유의미한 차이가 있음" if p_val < 0.05 else "유의미한 차이가 없음"
            st.write(f"""
            독립표본 t-검정 결과, 두 집단({groups[0]}, {groups[1]}) 간의 평균 차이는 
            통계적으로 **{is_significant}** (p = {p_val:.4f}).
            """)

            # 시각화 (Boxplot)
            st.write("### 📈 데이터 분포 시각화")
            fig, ax = plt.subplots()
            sns.boxplot(x=group_col, y=value_col, data=df, ax=ax)
            sns.stripplot(x=group_col, y=value_col, data=df, color="black", alpha=0.3, ax=ax)
            st.pyplot(fig)
            
        else:
            st.warning("T-test를 위해서는 집단(Group)이 정확히 2개여야 합니다. 현재 감지된 집단 수: " + str(len(groups)))
    else:
        st.error("URL이 올바르지 않거나 시트가 '공유 가능' 상태가 아닙니다.")
