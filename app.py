import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจ (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="Dashboard สรุปข้อมูลงานบริการกลุ่ม 4 (ไม่พัฒนาเป็น e-Service)", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS เพื่อตกแต่ง Card และตั้งค่าฟอนต์ Prompt (โดยไม่กระทบไอคอน)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Prompt', sans-serif;
    }

    .material-icons, 
    .material-symbols-rounded, 
    [class*="material"], 
    [data-testid*="stIcon"], 
    svg, 
    svg * {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

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
        df = df.fillna('') 
        return df
    except FileNotFoundError:
        st.error(f"❌ ไม่พบไฟล์ '{file_path}' กรุณาอัปโหลดไฟล์นี้ไว้ในโฟลเดอร์เดียวกับโค้ด")
        st.stop()

df = load_data()

# ==========================================
# 3. กำหนดคอลัมน์ (A=0, B=1, C=2, D=3, E=4, F=5)
# ==========================================
try:
    COL_MINISTRY = df.columns[1]  # คอลัมน์ B: กระทรวง
    COL_AGENCY = df.columns[2]    # คอลัมน์ C: หน่วยงาน
    COL_TYPE = df.columns[3]      # คอลัมน์ D: ประเภทหน่วยงาน
    COL_REASON = df.columns[5]    # คอลัมน์ F: เหตุผลที่ไม่พัฒนา e-Service
except IndexError:
    st.error("❌ จำนวนคอลัมน์ในไฟล์ Excel ไม่ครบถ้วน (ต้องมีอย่างน้อยถึงคอลัมน์ F)")
    st.stop()

# ==========================================
# 4. กำหนดชุดสี (Color Mapping) สำหรับเหตุผลฯ
# ==========================================
# ชุดสีพาสเทลแบบคลีนๆ สบายตา
PASTEL_COLORS = [
    '#dbeafe', '#d1fae5', '#fef3c7', '#fee2e2', 
    '#f3e8ff', '#ffedd5', '#e0e7ff', '#fce7f3', '#f3f4f6'
]

# ดึงเหตุผลที่ไม่ซ้ำกันทั้งหมด (ไม่นับค่าว่าง) มาจับคู่กับสี
unique_reasons_all = sorted([str(x) for x in df[COL_REASON].unique() if str(x).strip() != ''])
color_map = {reason: PASTEL_COLORS[i % len(PASTEL_COLORS)] for i, reason in enumerate(unique_reasons_all)}

# ==========================================
# 5. สร้าง Sidebar สำหรับตั้งค่าและกรองข้อมูล
# ==========================================
st.sidebar.title("🔍 ตัวกรองข้อมูล")
st.sidebar.markdown("---")

search_text = st.sidebar.text_input("ค้นหาข้อความทั่วไป", placeholder="พิมพ์คำที่ต้องการค้นหา...")

st.sidebar.markdown("**เลือกกรองตามหมวดหมู่:**")

min_opts = sorted([str(x) for x in df[COL_MINISTRY].unique() if str(x).strip() != ''])
agency_opts = sorted([str(x) for x in df[COL_AGENCY].unique() if str(x).strip() != ''])
type_opts = sorted([str(x) for x in df[COL_TYPE].unique() if str(x).strip() != ''])

ministries = st.sidebar.multiselect("กระทรวง", options=min_opts)
agencies = st.sidebar.multiselect("หน่วยงาน", options=agency_opts)
agency_types = st.sidebar.multiselect("ประเภทหน่วยงาน", options=type_opts)
reasons = st.sidebar.multiselect("เหตุผลที่ไม่พัฒนา e-Service", options=unique_reasons_all)

# ==========================================
# 6. ประมวลผลการกรองข้อมูล
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
# 7. แสดงผลหน้าหลัก (Main Content & Summary Cards)
# ==========================================
st.title("📊 Dashboard สรุปข้อมูลงานบริการกลุ่ม 4 (ที่จะไม่พัฒนา e-Service)")
st.markdown("---")

count_all = len(filtered_df)
count_ministry = filtered_df[filtered_df[COL_MINISTRY] != ''][COL_MINISTRY].nunique()
count_agency = filtered_df[filtered_df[COL_AGENCY] != ''][COL_AGENCY].nunique()
count_reason = filtered_df[filtered_df[COL_REASON] != ''][COL_REASON].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">📝 จำนวนรายการทั้งหมด</div><div class="metric-value">{count_all:,}</div></div>''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">🏛️ จำนวนกระทรวง</div><div class="metric-value">{count_ministry:,}</div></div>''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">🏢 จำนวนหน่วยงาน</div><div class="metric-value">{count_agency:,}</div></div>''', unsafe_allow_html=True)
with col4:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">⚠️ เหตุผลที่ไม่พัฒนา e-Service</div><div class="metric-value">{count_reason:,}</div></div>''', unsafe_allow_html=True)

st.write("") 
st.write("") 

# ==========================================
# 8. ส่วนแสดง Legend เม็ดสี และตาราง
# ==========================================
st.subheader(f"📄 รายละเอียดข้อมูล ({count_all} รายการ)")

# สร้าง Legend อธิบายสี (แสดงเฉพาะสีที่มีในข้อมูลที่ถูก Filter แล้ว เพื่อความสะอาดตา)
current_reasons = sorted([str(x) for x in filtered_df[COL_REASON].unique() if str(x).strip() != ''])

if current_reasons:
    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px; padding: 10px; background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">'
    legend_html += '<span style="font-weight: 500; color: #374151; margin-right: 5px;">📌 สัญลักษณ์สี:</span>'
    for reason in current_reasons:
        color = color_map.get(reason, '#ffffff')
        legend_html += f'''
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background-color: {color}; border: 1px solid #d1d5db;"></div>
                <span style="font-size: 0.95rem; color: #4b5563;">{reason}</span>
            </div>
        '''
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

# ฟังก์ชันสำหรับระบายสีใน DataFrame
def apply_color(val):
    color = color_map.get(str(val), '')
    if color:
        # ระบายสีพื้นหลังเซลล์ และให้ข้อความสีเข้มเพื่อให้อ่านง่าย
        return f'background-color: {color}; color: #1f2937;'
    return ''

# แสดงผลตารางพร้อม Styler ไฮไลต์สีลงในคอลัมน์ F
if not filtered_df.empty:
    # ตรวจสอบเวอร์ชัน pandas (ใช้ map ถ้าเวอร์ชันใหม่, applymap ถ้าเวอร์ชันเก่า)
    if hasattr(filtered_df.style, 'map'):
        styled_df = filtered_df.style.map(apply_color, subset=[COL_REASON])
    else:
        styled_df = filtered_df.style.applymap(apply_color, subset=[COL_REASON])
        
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")