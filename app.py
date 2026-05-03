import streamlit as st
import pandas as pd
import altair as alt  # เพิ่มไลบรารีสำหรับวาดกราฟขั้นสูง

# ==========================================
# 1. ตั้งค่าหน้าเพจ (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="Dashboard สรุปข้อมูลงานบริการกลุ่ม 4 (ไม่พัฒนาเป็น e-Service)", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS เพื่อตกแต่ง Card และตั้งค่าฟอนต์ Prompt
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
    [data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ฟังก์ชันโหลดข้อมูล (Data Loading)
# ==========================================
@st.cache_data(ttl=300)
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
VIBRANT_COLORS = [
    '#60A5FA', '#4ADE80', '#FACC15', '#F87171', 
    '#C084FC', '#FB923C', '#2DD4BF', '#F472B6', '#9CA3AF'
]
unique_reasons_all = sorted([str(x) for x in df[COL_REASON].unique() if str(x).strip() != ''])
color_map = {reason: VIBRANT_COLORS[i % len(VIBRANT_COLORS)] for i, reason in enumerate(unique_reasons_all)}

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
    st.markdown(f'<div class="metric-card"><div class="metric-label">📝 จำนวนรายการทั้งหมด</div><div class="metric-value">{count_all:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">🏛️ จำนวนกระทรวง</div><div class="metric-value">{count_ministry:,}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">🏢 จำนวนหน่วยงาน</div><div class="metric-value">{count_agency:,}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">⚠️ เหตุผลที่ไม่พัฒนา e-Service</div><div class="metric-value">{count_reason:,}</div></div>', unsafe_allow_html=True)

st.write("") 

# ==========================================
# 8. ส่วนแสดงกราฟแบบแนวนอน (Custom Horizontal Bar Chart)
# ==========================================
st.markdown("### 📈 กราฟสรุปข้อมูล (คลิกเพื่อกางดูรายละเอียด)")

# ฟังก์ชันช่วยสร้างกราฟแนวนอน
def create_horizontal_bar(data_series, color_hex):
    if data_series.empty:
        return None
    df_chart = data_series.reset_index()
    df_chart.columns = ['Name', 'Count']
    
    dynamic_height = max(150, len(df_chart) * 35)
    
    bars = alt.Chart(df_chart).mark_bar(color=color_hex, cornerRadiusEnd=4).encode(
        x=alt.X('Count:Q', title='จำนวน (รายการ)', axis=alt.Axis(tickMinStep=1)),
        y=alt.Y('Name:N', sort='-x', title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=['Name', 'Count']
    )
    
    # ใส่ตัวเลขสีขาว ขยับเข้ามาอยู่ด้านในปลายแท่งกราฟ และตั้งฟอนต์
    text = bars.mark_text(
        align='right',    # ชิดขวาของจุดสิ้นสุด
        baseline='middle',
        dx=-5,            # ขยับเข้ามาในแท่งกราฟ 5px
        color='#ffffff',  # อักษรสีขาว
        fontSize=13,
        fontWeight=600,   # หนาขึ้นเพื่อให้สีขาวอ่านชัด
        font='Prompt'     # กำหนดฟอนต์ Prompt
    ).encode(
        text='Count:Q'
    )
    
    # รวมกราฟและตั้งค่าฟอนต์ Prompt ให้แกน X, Y
    chart = (bars + text).properties(height=dynamic_height).configure_axis(
        labelFont='Prompt',
        titleFont='Prompt'
    ).configure_text(
        font='Prompt'
    )
    return chart

# เตรียมข้อมูล
chart_ministry = filtered_df[filtered_df[COL_MINISTRY] != ''][COL_MINISTRY].value_counts()
chart_agency = filtered_df[filtered_df[COL_AGENCY] != ''][COL_AGENCY].value_counts()
chart_reason = filtered_df[filtered_df[COL_REASON] != ''][COL_REASON].value_counts()

with st.expander("📊 ดูกราฟสรุปจำนวนรายการแยกตาม 'กระทรวง'"):
    chart = create_horizontal_bar(chart_ministry, '#60A5FA') 
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับแสดงกราฟ")

with st.expander("📊 ดูกราฟสรุปจำนวนรายการแยกตาม 'หน่วยงาน'"):
    chart = create_horizontal_bar(chart_agency, '#4ADE80') 
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับแสดงกราฟ")

with st.expander("📊 ดูกราฟสรุปแยกตาม 'เหตุผลที่ไม่พัฒนา e-Service'"):
    chart = create_horizontal_bar(chart_reason, '#F87171') 
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับแสดงกราฟ")

st.write("---")

# ==========================================
# 9. ส่วนแสดงตาราง
# ==========================================
st.subheader(f"📄 รายละเอียดข้อมูล ({count_all} รายการ)")

def apply_color(val):
    color = color_map.get(str(val), '')
    if color:
        return f'background-color: {color}; color: #1f2937;'
    return ''

if not filtered_df.empty:
    if hasattr(filtered_df.style, 'map'):
        styled_df = filtered_df.style.map(apply_color, subset=[COL_REASON])
    else:
        styled_df = filtered_df.style.applymap(apply_color, subset=[COL_REASON])
        
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")

# ==========================================
# 10. ส่วนแสดง Legend เม็ดสี (ด้านล่างตาราง)
# ==========================================
current_reasons = sorted([str(x) for x in filtered_df[COL_REASON].unique() if str(x).strip() != ''])

if current_reasons:
    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px; padding: 10px; background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">'
    legend_html += '<span style="font-weight: 500; color: #374151; margin-right: 5px;">📌 สัญลักษณ์สี:</span>'
    for reason in current_reasons:
        color = color_map.get(reason, '#ffffff')
        legend_html += f'<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 14px; height: 14px; border-radius: 50%; background-color: {color}; border: 1px solid #d1d5db;"></div><span style="font-size: 0.95rem; color: #4b5563;">{reason}</span></div>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

    # ==========================================
# 11. ส่วนแสดงผล Tableau Public (Embed)
# ==========================================
st.markdown("---")
st.markdown("### 📊 แดชบอร์ดวิเคราะห์ข้อมูลเชิงลึก (Tableau)")

# คำแนะนำ: ให้นำโค้ด Embed จาก Tableau Public มาวางแทนที่ในตัวแปร tableau_embed_code ด้านล่างนี้
tableau_embed_code = tableau_embed_code = """
<div class='tableauPlaceholder' id='viz1777794725088' style='position: relative'><noscript><a href='#'><img alt=' Dashboard รายละเอียดงานบริการของหน่วยงานภาครัฐที่ขับเคลื่อนในปีงบฯ 2569 ' src='https://public.tableau.com/static/images/Da/Dashboarde-Service69_17658966855680/DashboardDetaile-Service69/1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='Dashboarde-Service69_17658966855680/DashboardDetaile-Service69' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https://public.tableau.com/static/images/...' /></object></div>
<script type='text/javascript'>
    var divElement = document.getElementById('viz1777794725088');
    var vizElement = divElement.getElementsByTagName('object')[0];
    vizElement.style.width='100%';
    vizElement.style.height='850px'; 
    var scriptElement = document.createElement('script');
    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
    vizElement.parentNode.insertBefore(scriptElement, vizElement);
</script>
"""

st.components.v1.html(tableau_embed_code, height=850, scrolling=True)

# ใช้ st.components.v1.html เพื่อเรนเดอร์โค้ด Tableau บน Streamlit
# ปรับ height ให้เหมาะสมกับความสูงของแดชบอร์ดคุณ (เช่น 800-1000px)
st.components.v1.html(tableau_embed_code, height=850, scrolling=True)