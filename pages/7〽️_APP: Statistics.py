import streamlit as st
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Easy T-test Analyzer", layout="centered")
st.title("📊 Google Sheets T-test Analyzer")

sheet_url = st.text_input("구글 시트 주소를 붙여넣으세요:", 
                         placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing")

def get_google_sheet(url):
    try:
        file_id = url.split('/')[-2]
        raw_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
        return pd.read_csv(raw_url)
    except:
        return None

if sheet_url:
    df = get_google_sheet(sheet_url)
    
    if df is not None:
        st.write("### 📋 데이터 미리보기")
        st.dataframe(df.head())

        st.divider()
        cols = df.columns.tolist()
        group_col = st.selectbox("집단 구분 열(독립변수):", cols)
        value_col = st.selectbox("수치 열(종속변수):", cols)

        # --- [핵심 수정 부분: 데이터 전처리] ---
        # 1. 수치 데이터 열에서 숫자가 아닌 값은 NaN으로 변환 후 삭제
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        clean_df = df.dropna(subset=[value_col])
        
        # 2. 집단 열도 비어있지 않은 데이터만 필터링
        clean_df = clean_df.dropna(subset=[group_col])

        groups = clean_df[group_col].unique()

        if len(groups) == 2:
            # 데이터 분리
            g1 = clean_df[clean_df[group_col] == groups[0]][value_col]
            g2 = clean_df[clean_df[group_col] == groups[1]][value_col]

            # 데이터가 충분한지 확인
            if len(g1) > 1 and len(g2) > 1:
                try:
                    # t-test 수행 (nan_policy는 이미 위에서 처리했으므로 생략 가능)
                    t_stat, p_val = stats.ttest_ind(g1, g2)

                    st.subheader("📝 분석 결과 보고")
                    c1, c2 = st.columns(2)
                    c1.metric("T-value", f"{t_stat:.4f}")
                    c2.metric("P-value", f"{p_val:.4f}")

                    st.info("#### 💡 통계적 해석")
                    sig = "유의미한 차이가 있음" if p_val < 0.05 else "유의미한 차이가 없음"
                    st.write(f"두 집단 간 평균 차이는 **{sig}** (p = {p_val:.4f}).")

                    # 시각화
                    fig, ax = plt.subplots()
                    sns.boxplot(x=group_col, y=value_col, data=clean_df, ax=ax)
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"계산 중 오류가 발생했습니다: {e}")
            else:
                st.warning("분석에 필요한 데이터 수가 부족합니다.")
        else:
            st.warning(f"집단이 2개여야 합니다. (현재 감지된 집단: {list(groups)})")
    else:
        st.error("데이터를 가져오지 못했습니다. URL과 시트 권한을 확인하세요.")
