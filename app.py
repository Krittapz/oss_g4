import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจ (Page Configuration)
# ==========================================
st.set_page_config(page_title="Dashboard สรุปข้อมูล", layout="wide", page_icon="📊")

# Custom CSS เพื่อตกแต่ง Card ให้ดู Minimal และสะอาดตา
st.markdown("""
<style>
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
    /* ปรับแต่งส่วน Header ของตาราง */
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
    # อ้างอิงไฟล์ตามที่ระบุ
    file_path = 'test_group4_cut.xlsx'
    try:
        df = pd.read_excel(file_path)
        df = df.fillna('') # เติมค่าว่างด้วย string ว่างเพื่อป้องกัน Error ตอนค้นหา
        return df
    except FileNotFoundError:
        st.error(f"❌ ไม่พบไฟล์ '{file_path}' กรุณาอัปโหลดไฟล์นี้ไว้ในโฟลเดอร์เดียวกับโค้ด")
        st.stop()

df = load_data()

# ตรวจสอบชื่อคอลัมน์ (หากในไฟล์ Excel ชื่อคอลัมน์ต่างจากนี้ สามารถแก้ไขค่าใน String ด้านล่างได้เลย)
COL_MINISTRY = 'กระทรวง' if 'กระทรวง' in df.columns else df.columns[0]
COL_AGENCY = 'หน่วยงาน' if 'หน่วยงาน' in df.columns else df.columns[1]
COL_TYPE = 'ประเภทหน่วยงาน' if 'ประเภทหน่วยงาน' in df.columns else df.columns[2]
COL_REASON = 'เหตุผลที่ไม่เชื่อมโยง' if 'เหตุผลที่ไม่เชื่อมโยง' in df.columns else df.columns[3]

# ==========================================
# 3. สร้าง Sidebar สำหรับตั้งค่าและกรองข้อมูล
# ==========================================
st.sidebar.title("🔍 ตัวกรองข้อมูล")
st.sidebar.markdown("---")

# ช่องค้นหา (Search)
search_text = st.sidebar.text_input("ค้นหาข้อความทั่วไป", placeholder="พิมพ์คำที่ต้องการค้นหา...")

st.sidebar.markdown("**เลือกกรองตามหมวดหมู่:**")
# ช่องตัวกรอง (Filters)
ministries = st.sidebar.multiselect("กระทรวง", options=sorted(df[COL_MINISTRY].astype(str).unique()))
agencies = st.sidebar.multiselect("หน่วยงาน", options=sorted(df[COL_AGENCY].astype(str).unique()))
agency_types = st.sidebar.multiselect("ประเภทหน่วยงาน", options=sorted(df[COL_TYPE].astype(str).unique()))
reasons = st.sidebar.multiselect("เหตุผลที่ไม่เชื่อมโยง", options=sorted(df[COL_REASON].astype(str).unique()))

# ==========================================
# 4. ประมวลผลการกรองข้อมูล (Apply Filters)
# ==========================================
filtered_df = df.copy()

# กรองด้วยช่องค้นหา (ค้นหาจากทุกคอลัมน์ที่เป็นข้อความ)
if search_text:
    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False)).any(axis=1)
    filtered_df = filtered_df[mask]

# กรองด้วย Dropdown
if ministries:
    filtered_df = filtered_df[filtered_df[COL_MINISTRY].isin(ministries)]
if agencies:
    filtered_df = filtered_df[filtered_df[COL_AGENCY].isin(agencies)]
if agency_types:
    filtered_df = filtered_df[filtered_df[COL_TYPE].isin(agency_types)]
if reasons:
    filtered_df = filtered_df[filtered_df[COL_REASON].isin(reasons)]

# ==========================================
# 5. แสดงผลหน้าหลัก (Main Content & Summary Cards)
# ==========================================
st.title("📊 แดชบอร์ดสรุปข้อมูล")
st.markdown("ระบบติดตามและตรวจสอบการเชื่อมโยงข้อมูล")
st.markdown("---")

# วาด Summary Cards 4 ช่อง
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📝 จำนวนรายการทั้งหมด</div>
            <div class="metric-value">{len(filtered_df):,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🏛️ กระทรวงที่เกี่ยวข้อง</div>
            <div class="metric-value">{filtered_df[COL_MINISTRY].nunique():,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🏢 หน่วยงานทั้งหมด</div>
            <div class="metric-value">{filtered_df[COL_AGENCY].nunique():,}</div>
        </div>
    ''', unsafe_allow_html=True)
with col4:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">⚠️ เหตุผลที่ไม่เชื่อมโยง</div>
            <div class="metric-value">{filtered_df[COL_REASON].nunique():,}</div>
        </div>
    ''', unsafe_allow_html=True)

st.write("") # เว้นบรรทัด
st.write("") 

# แสดงตารางข้อมูล
st.subheader(f"📄 รายละเอียดข้อมูล ({len(filtered_df)} รายการ)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)