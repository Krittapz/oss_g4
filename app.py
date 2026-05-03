import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจ (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="Dashboard สรุปข้อมูลงานบริการกลุ่ม 4", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS เพื่อตกแต่ง Card และตั้งค่าฟอนต์ Prompt (โดยไม่กระทบไอคอน)
st.markdown("""
<style>
    /* นำเข้าฟอนต์ Prompt */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    /* บังคับใช้ฟอนต์ Prompt กับทุกส่วน */
    * {
        font-family: 'Prompt', sans-serif;
    }

    /* *สำคัญ*: คืนค่าฟอนต์พื้นฐานให้กลุ่มไอคอน (เพื่อแก้ปัญหาจุด 3 จุด และไอคอนระบบเพี้ยน) */
    .material-icons, 
    .material-symbols-rounded, 
    [class*="material"], 
    [data-testid*="stIcon"], 
    svg, 
    svg * {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    /* ตกแต่ง Metric Card */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1f2937;
        margin-top: 10px;
    }
    .metric-label {
        font-size: 1rem;
        font-weight: 500;
        color: #6b7280;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ฟังก์ชันโหลดข้อมูล (Data Loading)
# ==========================================
@st.cache_data
def load_data():
    file_path = 'test_group4_cut.xlsx'
    try:
        df = pd.read_excel(file_path)
        df = df.fillna('') # เติมค่าว่างด้วย string ว่างเพื่อป้องกัน Error ตอนค้นหา
        return df
    except FileNotFoundError:
        st.error(f"❌ ไม่พบไฟล์ '{file_path}' กรุณาอัปโหลดไฟล์นี้ไว้ในโฟลเดอร์เดียวกับโค้ด")
        st.stop()

df = load_data()

# ==========================================
# 3. กำหนดคอลัมน์ (อิงตามลำดับ A, B, C... ของ Excel)
# ==========================================
# A = index 0, B = index 1, C = index 2, ..., G = index 6
try:
    COL_MINISTRY = df.columns[1]  # คอลัมน์ B: กระทรวง
    COL_AGENCY = df.columns[2]    # คอลัมน์ C: หน่วยงาน
    COL_TYPE = df.columns[3]      # คอลัมน์ D: ประเภทหน่วยงาน
    COL_REASON = df.columns[6]    # คอลัมน์ G: เหตุผลที่ไม่เชื่อมโยง
except IndexError:
    st.error("❌ จำนวนคอลัมน์ในไฟล์ Excel ไม่ครบถ้วน (ต้องมีถึงคอลัมน์ G)")
    st.stop()

# ==========================================
# 4. สร้าง Sidebar สำหรับตั้งค่าและกรองข้อมูล
# ==========================================
st.sidebar.title("🔍 ตัวกรองข้อมูล")
st.sidebar.markdown("---")

# ช่องค้นหา (Search)
search_text = st.sidebar.text_input("ค้นหาข้อความทั่วไป", placeholder="พิมพ์คำที่ต้องการค้นหา...")

st.sidebar.markdown("**เลือกกรองตามหมวดหมู่:**")

# ดึงข้อมูลมาทำเป็นตัวเลือก (โดยตัดค่าว่างออก เพื่อไม่ให้มีตัวเลือกว่างใน dropdown)
min_opts = sorted([str(x) for x in df[COL_MINISTRY].unique() if str(x).strip() != ''])
agency_opts = sorted([str(x) for x in df[COL_AGENCY].unique() if str(x).strip() != ''])
type_opts = sorted([str(x) for x in df[COL_TYPE].unique() if str(x).strip() != ''])
reason_opts = sorted([str(x) for x in df[COL_REASON].unique() if str(x).strip() != ''])

# ช่องตัวกรอง (Filters)
ministries = st.sidebar.multiselect("กระทรวง", options=min_opts)
agencies = st.sidebar.multiselect("หน่วยงาน", options=agency_opts)
agency_types = st.sidebar.multiselect("ประเภทหน่วยงาน", options=type_opts)
reasons = st.sidebar.multiselect("เหตุผลที่ไม่เชื่อมโยง", options=reason_opts)

# ==========================================
# 5. ประมวลผลการกรองข้อมูล (Apply Filters)
# ==========================================
filtered_df = df.copy()

if search_text:
    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False)).any(axis=1)
    filtered_df = filtered_df[mask]

if ministries:
    filtered_df = filtered_df[filtered_df[COL_MINISTRY].isin(ministries)]
if agencies:
    filtered_df = filtered_df[filtered_df[COL_AGENCY].isin(agencies)]
if agency_types:
    filtered_df = filtered_df[filtered_df[COL_TYPE].isin(agency_types)]
if reasons:
    filtered_df = filtered_df[filtered_df[COL_REASON].isin(reasons)]

# ==========================================
# 6. แสดงผลหน้าหลัก (Main Content & Summary Cards)
# ==========================================
st.title("📊 Dashboard สรุปข้อมูลงานบริการกลุ่ม 4 (ที่จะไม่พัฒนา e-Service)")
st.markdown("---")

# คำนวณจำนวนสำหรับ Card (นับแบบ Unique และไม่นับค่าว่าง)
count_all = len(filtered_df)
count_ministry = filtered_df[filtered_df[COL_MINISTRY] != ''][COL_MINISTRY].nunique()
count_agency = filtered_df[filtered_df[COL_AGENCY] != ''][COL_AGENCY].nunique()
count_reason = filtered_df[filtered_df[COL_REASON] != ''][COL_REASON].nunique()

# วาด Summary Cards 4 ช่อง
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📝 จำนวนรายการทั้งหมด</div>
            <div class="metric-value">{count_all:,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🏛️ จำนวนกระทรวง</div>
            <div class="metric-value">{count_ministry:,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🏢 จำนวนหน่วยงาน</div>
            <div class="metric-value">{count_agency:,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col4:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">⚠️ เหตุผลที่ไม่เชื่อมโยง</div>
            <div class="metric-value">{count_reason:,}</div>
        </div>
    ''', unsafe_allow_html=True)

st.write("") # เว้นบรรทัด
st.write("") 

# แสดงตารางข้อมูล
st.subheader(f"📄 รายละเอียดข้อมูล ({count_all} รายการ)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)