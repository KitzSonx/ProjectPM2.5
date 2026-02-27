import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(
    page_title="Air Quality & Weather Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 ปรับแต่ง CSS ลับ (ซ่อนองค์ประกอบที่ไม่จำเป็น และทำ UI ให้คลีน)
# ==========================================
st.markdown("""
<style>
    /* ปรับแต่งฟอนต์โดยรวมและการเว้นช่องว่าง */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ปรับแต่งตัวเลขของ st.metric ให้ดูแพงขึ้น */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* รองรับ Dark Mode สำหรับตัวเลข */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetricValue"] {
            color: #f8fafc;
        }
    }
</style>
""", unsafe_allow_html=True)

# 2. ส่วนหัวของเว็บไซต์ (ใช้ Material Icons แทนอิโมจิ)
st.markdown("## :material/dashboard: ระบบรายงานคุณภาพอากาศและสภาพอากาศ")
st.markdown("<p style='color: #64748b; margin-top: -10px;'>แดชบอร์ดติดตามข้อมูลแบบเรียลไทม์ พร้อมการวิเคราะห์แนวโน้มย้อนหลัง</p>", unsafe_allow_html=True)
st.divider()

# 3. เมนูด้านข้าง (สร้างกรอบครอบการตั้งค่า)
with st.sidebar:
    st.markdown("### :material/tune: การตั้งค่า")
    
    # ใช้กรอบ (Card) เพื่อจัดกลุ่มเมนู
    with st.container(border=True):
        start_date = st.date_input("วันที่เริ่มต้น", date.today() - timedelta(days=7))
        end_date = st.date_input("วันที่สิ้นสุด", date.today())
        
    st.markdown("""
        <div style='background-color: #f1f5f9; padding: 15px; border-radius: 8px; margin-top: 20px;'>
            <p style='color: #475569; font-size: 14px; margin: 0;'>
                <b>:material/info: คำแนะนำ:</b><br>
                เลือกช่วงเวลาที่ต้องการ ระบบจะทำการปรับกราฟและค่าสถิติโดยอัตโนมัติ
            </p>
        </div>
    """, unsafe_allow_html=True)

# 4. ฟังก์ชันดึงข้อมูล (จำลอง)
@st.cache_data
def fetch_data_from_api(start, end):
    date_range = pd.date_range(start=start, end=end, freq='H')
    
    pm25 = np.random.uniform(10, 150, size=len(date_range))
    temp = np.random.uniform(22, 38, size=len(date_range))
    humid = np.random.uniform(40, 90, size=len(date_range))
    
    data = pd.DataFrame({
        'เวลา': date_range,
        'PM2.5': pd.Series(pm25).rolling(3, min_periods=1).mean(),
        'อุณหภูมิ': pd.Series(temp).rolling(3, min_periods=1).mean(),
        'ความชื้น': pd.Series(humid).rolling(3, min_periods=1).mean()
    })
    return data

# ฟังก์ชันสำหรับสร้างป้ายสถานะ (Badge) สีสันสวยงามแบบ Minimal
def get_aqi_badge(pm25_val):
    if pm25_val <= 37.5:
        return "<div style='background-color: #dcfce7; color: #166534; padding: 6px 12px; border-radius: 20px; font-weight: 600; display: inline-block; font-size: 14px;'>ดีมาก (Good)</div>"
    elif pm25_val <= 75:
        return "<div style='background-color: #fef08a; color: #854d0e; padding: 6px 12px; border-radius: 20px; font-weight: 600; display: inline-block; font-size: 14px;'>ปานกลาง (Moderate)</div>"
    else:
        return "<div style='background-color: #fee2e2; color: #991b1b; padding: 6px 12px; border-radius: 20px; font-weight: 600; display: inline-block; font-size: 14px;'>มีผลกระทบ (Unhealthy)</div>"

# 5. ตรวจสอบเงื่อนไขและแสดงผล
if start_date > end_date:
    st.error(":material/warning: กรุณาเลือกวันที่เริ่มต้น ให้ก่อนหรือเท่ากับวันที่สิ้นสุด")
else:
    df = fetch_data_from_api(start_date, end_date)
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest
    
    st.markdown("#### :material/location_on: สถานการณ์ปัจจุบัน")
    
    # --- 5.1 สร้าง Cards แบบเรียบหรูโดยใช้ st.container(border=True) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(border=True):
            st.markdown("<p style='color:#64748b; font-size:14px; margin-bottom:5px;'>:material/air: ปริมาณฝุ่น PM2.5</p>", unsafe_allow_html=True)
            st.metric(
                label="PM2.5", 
                value=f"{latest['PM2.5']:.1f} µg/m³",
                delta=f"{(latest['PM2.5'] - previous['PM2.5']):.1f} (1 ชม.)",
                delta_color="inverse",
                label_visibility="collapsed" # ซ่อน Label เดิมของ Streamlit เพื่อใช้ของเราเองที่สวยกว่า
            )
            
    with col2:
        with st.container(border=True):
            st.markdown("<p style='color:#64748b; font-size:14px; margin-bottom:15px;'>:material/health_and_safety: ระดับคุณภาพอากาศ</p>", unsafe_allow_html=True)
            # แสดง Badge สีแทนการใช้ st.metric แบบเดิม
            st.markdown(get_aqi_badge(latest['PM2.5']), unsafe_allow_html=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # ดันให้ช่องไฟเท่ากับ card อื่น

    with col3:
        with st.container(border=True):
            st.markdown("<p style='color:#64748b; font-size:14px; margin-bottom:5px;'>:material/thermostat: อุณหภูมิ</p>", unsafe_allow_html=True)
            st.metric(
                label="อุณหภูมิ", 
                value=f"{latest['อุณหภูมิ']:.1f} °C",
                delta=f"{(latest['อุณหภูมิ'] - previous['อุณหภูมิ']):.1f} °C",
                delta_color="normal",
                label_visibility="collapsed"
            )

    with col4:
        with st.container(border=True):
            st.markdown("<p style='color:#64748b; font-size:14px; margin-bottom:5px;'>:material/water_drop: ความชื้น</p>", unsafe_allow_html=True)
            st.metric(
                label="ความชื้น", 
                value=f"{latest['ความชื้น']:.1f} %",
                delta=f"{(latest['ความชื้น'] - previous['ความชื้น']):.1f} %",
                delta_color="off",
                label_visibility="collapsed"
            )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 5.2 กราฟข้อมูลย้อนหลัง (คุมโทนสี สไตล์ Minimal) ---
    st.markdown("#### :material/analytics: ข้อมูลและแนวโน้มย้อนหลัง")
    
    # ใช้ Tabs แบบไม่มีอิโมจิ
    tab1, tab2 = st.tabs(["ข้อมูลฝุ่น PM2.5", "ข้อมูลอุณหภูมิและความชื้น"])
    
    with tab1:
        with st.container(border=True):
            fig_pm = px.area(
                df, x='เวลา', y='PM2.5', 
                color_discrete_sequence=['#14b8a6'], # สี Teal (เขียวอมฟ้า) คลีนๆ
            )
            # ปรับแต่งให้ Plotly ดูคลีน ไร้เส้นขอบและตารางที่รกตา
            fig_pm.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=20, b=0),
                height=350,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(fig_pm, use_container_width=True)
        
    with tab2:
        with st.container(border=True):
            fig_weather = px.line(
                df, x='เวลา', y=['อุณหภูมิ', 'ความชื้น'],
                color_discrete_sequence=['#f97316', '#3b82f6'], # สีส้มพาสเทล (อุณหภูมิ) และสีฟ้า (ความชื้น)
            )
            fig_weather.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend_title_text="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(fig_weather, use_container_width=True)