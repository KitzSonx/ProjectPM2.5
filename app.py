import streamlit as st
import pandas as pd
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Smart PM2.5 CRMS6 (Live)", layout="wide")

# 2. หัวข้อและสถานที่
st.title("📡 Smart PM2.5 CRMS6 (Live MQTT)")
st.info("📍 โรงเรียนเทศบาล 6 นครเชียงราย - ข้อมูลแสดงผลแบบ Real-time จาก MQTT Broker")

# 3. เตรียมที่เก็บข้อมูลใน Session (ป้องกันข้อมูลหายเวลา Script รันใหม่)
if 'mqtt_data' not in st.session_state:
    st.session_state.mqtt_data = []

# 4. ฟังก์ชันเมื่อได้รับข้อความจาก MQTT
def on_message(client, userdata, message):
    try:
        # แปลง JSON ที่ได้รับเป็น Dictionary
        payload = json.loads(message.payload.decode("utf-8"))
        # เพิ่มข้อมูลเข้าไปใน session_state
        st.session_state.mqtt_data.append(payload)
        # รักษาขนาดข้อมูล (เช่น เก็บแค่ 50 จุดล่าสุด)
        if len(st.session_state.mqtt_data) > 50:
            st.session_state.mqtt_data.pop(0)
    except Exception as e:
        print(f"Error parsing: {e}")

# 5. ตั้งค่าการเชื่อมต่อ MQTT
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "leantech/tesaban6/pm1"

# ใช้ปุ่มกดเพื่อเริ่มการเชื่อมต่อ (Streamlit ทำงานแบบ Loop)
if st.button("เริ่มดึงข้อมูลสด (Connect MQTT)"):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    client.loop_start()
    st.success(f"เชื่อมต่อกับ Topic: {TOPIC} เรียบร้อยแล้ว! กรุณารอข้อมูลจากเซ็นเซอร์...")

# 6. ส่วนการแสดงผล
if st.session_state.mqtt_data:
    df = pd.DataFrame(st.session_state.mqtt_data)
    
    # แสดงค่าล่าสุดใน Card
    latest = df.iloc[-1]
    cols = st.columns(3)
    cols[0].metric("PM2.5", f"{latest['pm2.5']} µg/m³")
    cols[1].metric("อุณหภูมิ", f"{latest['temperature']} °C")
    cols[2].metric("ความชื้น", f"{latest['humidity']} %")

    # พล็อตกราฟ
    st.subheader("📈 กราฟข้อมูลสดล่าสุด (50 จุด)")
    st.line_chart(df.set_index('timestamp')[['pm2.5', 'temperature', 'humidity']])
    
    # แสดงตารางข้อมูล JSON
    with st.expander("ดูข้อมูลดิบ (Raw JSON)"):
        st.write(df)
else:
    st.warning("⏳ ยังไม่มีข้อมูลส่งเข้ามา... (เครื่องเซ็นเซอร์ต้องส่งข้อมูลมาที่ Topic นี้ก่อน)")

# 7. ปุ่มรีเฟรชหน้าจอ (Streamlit ต้องการการสั่งรันใหม่เพื่ออัปเดตค่าบนหน้าจอ)
if st.button("อัปเดตหน้าจอ (Refresh)"):
    st.rerun()
