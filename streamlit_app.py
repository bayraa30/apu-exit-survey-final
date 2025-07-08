import streamlit as st
from snowflake.snowpark import Session
from datetime import datetime

# ---- CONFIG ----
COMPANY_NAME = "АПУ ХХК"
SCHEMA_NAME = "APU"
EMPLOYEE_TABLE = "APU_EMP_DATA"
ANSWER_TABLE = f"{SCHEMA_NAME}_SURVEY_ANSWERS"
DATABASE_NAME = "CDNA_HR_DATA"
LOGO_URL = "https://i.imgur.com/DgCfZ9B.png"

# ---- Secure session ----
def get_session():
    return Session.builder.configs(st.secrets["connections.snowflake"]).create()

# ---- Answer storing ----
def submit_answers():
    emp_code = st.session_state.get("confirmed_empcode")
    first_name = st.session_state.get("confirmed_firstname")
    survey_type = st.session_state.get("survey_type", "")
    schema = SCHEMA_NAME
    table = f"{schema}_SURVEY_ANSWERS"
    submitted_at = datetime.utcnow()
    a = st.session_state.answers

    values = [
        emp_code, first_name, survey_type, submitted_at,
        a.get("Reason_for_Leaving", ""), a.get("Alignment_with_Daily_Tasks", ""),
        a.get("Unexpected_Responsibilities", ""), a.get("Onboarding_Effectiveness", ""),
        a.get("Company_Culture", ""), a.get("Atmosphere", ""), a.get("Conflict_Resolution", ""),
        a.get("Feedback", ""), a.get("Leadership_Style", ""), a.get("Team_Collaboration", ""),
        a.get("Team_Support", ""), a.get("Motivation", ""), a.get("Motivation_Other", ""),
        a.get("Engagement", ""), a.get("Engagement_Other", ""), a.get("Well_being", ""),
        a.get("Performance_Compensation", ""), a.get("Value_of_Benefits", ""), a.get("KPI_Accuracy", ""),
        a.get("Career_Growth", ""), a.get("Traning_Quality", ""), a.get("Loyalty1", ""),
        a.get("Loyalty1_Other", ""), a.get("Loyalty2", ""), a.get("Loyalty2_Other", "")
    ]

    try:
        session = get_session()
        escaped_values = ["'{}'".format(str(v).replace("'", "''")) if v is not None else "''" for v in values]
        insert_query = f"""
            INSERT INTO {table} (
                EMPCODE, FIRSTNAME, SURVEY_TYPE, SUBMITTED_AT,
                Reason_for_Leaving, Alignment_with_Daily_Tasks, Unexpected_Responsibilities,
                Onboarding_Effectiveness, Company_Culture, Atmosphere, Conflict_Resolution,
                Feedback, Leadership_Style, Team_Collaboration, Team_Support,
                Motivation, Motivation_Other, Engagement, Engagement_Other, Well_being,
                Performance_Compensation, Value_of_Benefits, KPI_Accuracy, Career_Growth,
                Traning_Quality, Loyalty1, Loyalty1_Other, Loyalty2, Loyalty2_Other
            ) VALUES ({','.join(escaped_values)})
        """
        session.sql(insert_query).collect()
        return True
    except Exception as e:
        st.error(f"❌ Failed to submit answers: {e}")
        return False

# ---- Survey types per category ----
survey_types = {
    "Компанийн санаачилгаар": ["1 жил хүртэл", "1-ээс дээш"],
    "Ажилтны санаачлагаар": [
        "6 сар дотор гарч байгаа", "7 сараас 3 жил ",
        "4-10 жил", "11 болон түүнээс дээш"
    ],
}

# ---- PAGE SETUP ----
st.set_page_config(page_title=f"{COMPANY_NAME} Судалгаа", layout="wide")

# ---- UTILS ----
def logo():
    st.image(LOGO_URL, width=210)

def progress_chart():
    total_questions_by_type = {
        "1 жил хүртэл": 17,
        "1-ээс дээш": 16,
        "6 сар дотор гарч байгаа": 20,
        "7 сараас 3 жил ": 19,
        "4-10 жил": 19,
        "11 болон түүнээс дээш": 19
    }
    if st.session_state.page < 3:
        return
    current_page = st.session_state.page
    total = total_questions_by_type.get(st.session_state.survey_type, 19)
    question_index = max(1, current_page - 3 + 1)
    progress = min(100, max(0, int((question_index / total) * 100)))
    st.markdown(f"#### Асуулт {question_index} / {total}")
    st.progress(progress)

# ---- SESSION INIT ----
for key, value in [
    ("category_selected", None), ("survey_type", None), ("page", -1),
    ("emp_confirmed", None), ("answers", {}), ("logged_in", False)
]:
    if key not in st.session_state:
        st.session_state[key] = value

# ---- LOGIN PAGE ----
def login_page():
    logo()
    st.title("👨‍💼 Нэвтрэх 👩‍💼")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "hr" and password == "demo123":
            st.session_state.logged_in = True
            st.session_state.page = -0.5
            st.rerun()
        else:
            st.error("❌ Invalid credentials.")

# ---- DIRECTORY PAGE ----
def directory_page():
    logo()
    st.title("Судалгааны сонголт")
    option = st.radio("Асуулгын төрлөө сонгоно уу:", ["📋 Exit Survey", "🎤 Exit Interview"], index=None)
    if st.button("Continue"):
        if option == "📋 Exit Survey":
            st.session_state.page = 0
            st.rerun()
        elif option == "🎤 Exit Interview":
            st.warning("Interview flow coming soon!")
        else:
            st.error("Та сонголт хийнэ үү.")

# ---- PAGE 0: CATEGORY + SURVEY TYPE ----
def page_0():
    logo()
    st.header("Ерөнхий мэдээлэл")
    st.markdown("**Судалгааны ангилал болон төрлөө сонгоно уу.**")
    category = st.selectbox(
        "Судалгааны ангилал:",
        ["-- Сонгох --"] + list(survey_types.keys()),
        index=0 if not st.session_state.category_selected else list(survey_types.keys()).index(st.session_state.category_selected) + 1,
        key="category_select"
    )
    if category != "-- Сонгох --":
        st.session_state.category_selected = category
    if st.session_state.category_selected:
        st.markdown("**Судалгааны төрөл:**")
        types = survey_types[st.session_state.category_selected]
        cols = st.columns(len(types))
        for i, survey in enumerate(types):
            with cols[i]:
                if st.button(survey, key=f"survey_{i}"):
                    st.session_state.survey_type = survey
                    st.session_state.page = 1
                    st.rerun()

# ---- PAGE 1: EMPLOYEE CONFIRMATION ----
def page_1():
    logo()
    st.title("Ажилтны баталгаажуулалт")
    st.text_input("Ажилтны код", key="empcode")
    st.text_input("Нэр", key="firstname")
    if st.button("Баталгаажуулах", key="btn_confirm"):
        empcode = st.session_state.get("empcode", "").strip()
        firstname = st.session_state.get("firstname", "").strip()
        if empcode and firstname:
            try:
                session = get_session()
                df = session.sql(f"""
                    SELECT LASTNAME, FIRSTNAME, POSNAME, HEADDEPNAME, COMPANYNAME
                    FROM {DATABASE_NAME}.{SCHEMA_NAME}.{EMPLOYEE_TABLE}
                    WHERE EMPCODE = '{empcode}' AND FIRSTNAME = '{firstname}'
                """).to_pandas()
                if not df.empty:
                    emp = df.iloc[0]
                    st.session_state.emp_confirmed = True
                    st.session_state.confirmed_empcode = empcode
                    st.session_state.confirmed_firstname = firstname
                    st.session_state.emp_info = {
                        "Компани": emp["COMPANYNAME"],
                        "Алба хэлтэс": emp["HEADDEPNAME"],
                        "Албан тушаал": emp["POSNAME"],
                        "Овог": emp["LASTNAME"],
                        "Нэр": emp["FIRSTNAME"],
                    }
                else:
                    st.session_state.emp_confirmed = False
            except Exception as e:
                st.error(f"❌ Snowflake холболтын алдаа: {e}")
    if st.session_state.emp_confirmed is True:
        st.success("✅ Амжилттай баталгаажлаа!")
        emp = st.session_state.emp_info
        st.markdown("### 🧾 Таны мэдээлэл")
        st.markdown(f"""
            **Компани:** {emp['Компани']}  
            **Алба хэлтэс:** {emp['Алба хэлтэс']}  
            **Албан тушаал:** {emp['Албан тушаал']}  
            **Овог:** {emp['Овог']}  
            **Нэр:** {emp['Нэр']}
        """)
        if st.button("Үргэлжлүүлэх", key="btn_intro"):
            st.session_state.page = 2
            st.rerun()
    elif st.session_state.emp_confirmed is False:
        st.error("❌ Ажилтны мэдээлэл буруу байна. Код болон нэрийг шалгана уу.")

# ---- PAGE 2: UNIVERSAL INTRO ----
def page_2():
    logo()
    st.title(st.session_state.survey_type)
    st.markdown("""
    Сайн байна уу!  
    Таны өгч буй үнэлгээ, санал хүсэлт нь бидний цаашдын хөгжлийг тодорхойлоход чухал үүрэгтэй тул дараах асуултад үнэн зөв, чин сэтгэлээсээ хариулна уу.
    """)
    if st.button("Асуулга эхлэх", key="btn_begin"):
        st.session_state.page = 3
        st.rerun()

# ---- ROUTING ----
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page == -0.5:
    directory_page()
elif st.session_state.page == 0:
    page_0()
elif st.session_state.page == 1:
    page_1()
elif st.session_state.page == 2:
    page_2()
elif st.session_state.page == 3:
    page_3()
elif st.session_state.page == 999:
    page_999()
else:
    page_3_and_beyond()




# ---- PAGE 3: FIRST QUESTION (per survey type) ----
def page_3():
    logo()
    progress_chart()
    survey_type = st.session_state.survey_type

    if survey_type == "1 жил хүртэл":
        st.header("1. Ажлын байрны тодорхойлолт болон өдөр тутмын ажил үүрэг таны **хүлээлтэд** нийцсэн үү?")
        q1 = st.radio(
            "Таны үнэлгээ (1–5 од):",
            ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
            key="q1_1jil",
            index=None
        )
        answer_key = "Alignment_with_Daily_Tasks"

    elif survey_type == "1-ээс дээш":
        st.header("1. Ажлын байрны тодорхойлолт таны өдөр тутмын ажил үүрэгтэй нийцэж байсан уу?")
        q1 = st.radio(
            "Таны үнэлгээ (1–5 од):",
            ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
            key="q1_1deesh",
            index=None
        )
        answer_key = "Unexpected_Responsibilities"

    elif survey_type == "6 сар дотор гарч байгаа":
        st.header("1. Танд ажлаас гарахад нөлөөлсөн хүчин зүйл, шалтгааны талаар дэлгэрэнгүй хэлж өгнө үү?")
        q1_choices = [
            "🚀 Career Advancement",
            "💰 Compensation",
            "⚖️ Work-Life Balance",
            "🧑‍💼 Management",
            "😊 Job Satisfaction",
            "🏢 Company Culture",
            "📦 Relocation",
            "🧘 Personal Reasons",
            "📨 Better Opportunity, offer",
            "🏗️ Work Conditions"
        ]
        q1 = st.radio("Үндсэн шалтгаанууд:", q1_choices, key="q1_6sar", index=None)
        answer_key = "Reason_for_Leaving"

    elif survey_type in ["7 сараас 3 жил ", "4-10 жил", "11 болон түүнээс дээш"]:
        st.header("1. Танд ажлаас гарахад нөлөөлсөн хүчин зүйл, шалтгааны талаар дэлгэрэнгүй хэлж өгнө үү?")
        q1_choices = [
            "🚀 Career Advancement",
            "💰 Compensation",
            "⚖️ Work-Life Balance",
            "🧑‍💼 Management",
            "😊 Job Satisfaction",
            "🏢 Company Culture",
            "📦 Relocation",
            "🧘 Хувийн шалтгаан / Personal Reasons",
            "📨 Илүү боломжийн өөр ажлын байрны санал авсан / Better Opportunity, offer",
            "🏗️ Ажлын нөхцөл / Work Conditions"
        ]
        q1 = st.radio("Үндсэн шалтгаанууд:", q1_choices, key="q1_busad", index=None)
        answer_key = "Reason_for_Leaving"

    # Save answer and move to next page
    if q1 is not None and st.button("Дараагийн асуулт", key="btn_next_q1"):
        st.session_state.answers[answer_key] = q1
        st.session_state.page = 4
        st.rerun()























