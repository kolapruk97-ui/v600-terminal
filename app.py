import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import pytz

# ตั้งค่าหน้าจอแอป
st.set_page_config(page_title="V.600.18 TERMINAL", page_icon="🦅", layout="centered")

st.title("🦅 THE ULTIMATE MATRIX")
st.markdown("### 💻 V.600.18 (Classic Covered Call Edition)")

# ==========================================
# 🎮 INPUT ZONE
# ==========================================
st.sidebar.header("💰 กระแสเงินสด (Cash Flow)")
budget_usd = st.sidebar.number_input("1. งบ DCA เดือนนี้ (USD)", min_value=0.0, value=100.0, step=10.0)
cash_reserve = st.sidebar.number_input("2. เงินสดสำรอง (Reserve)", min_value=0.0, value=50.0, step=10.0)

st.sidebar.markdown("---")
st.sidebar.markdown("กดปุ่มด้านล่างเพื่อรันระบบ 👇")

if st.sidebar.button("🚀 สแกนตลาดและออกใบสั่งรบ", use_container_width=True):
    with st.spinner('⏳ กำลังเชื่อมต่อดาวเทียมสแกนตลาด...'):
        try:
            # ดึงข้อมูล
            spy_df = yf.Ticker("SPY").history(period="1y")
            spy_df['SMA50'] = spy_df['Close'].rolling(window=50).mean()
            spy_df['SMA200'] = spy_df['Close'].rolling(window=200).mean()
            
            spy_price = float(spy_df['Close'].iloc[-1])
            sma50 = float(spy_df['SMA50'].iloc[-1])
            sma200 = float(spy_df['SMA200'].iloc[-1])
            
            vix_price = float(yf.Ticker("^VIX").history(period="5d")['Close'].iloc[-1])
            
            # ลอจิก V.600.18
            sniper_threshold = sma200 * 0.95
            is_sniper = spy_price < sniper_threshold
            is_bull = spy_price > sma50
            gap_percent = ((spy_price - sma200) / sma200) * 100
            
            if is_sniper:
                status = "🔴 SNIPER (ทุ่มซื้อก้นเหว)"
                auth_budget = budget_usd + cash_reserve
                final_reserve = 0.0
                desc = f"หลุด ${sniper_threshold:.2f} (-5%) -> งัดเงินสำรองทุบซื้อ 100%"
                color = "error"
            elif is_bull:
                status = "🟢 BULL (ขาขึ้นปกติ)"
                auth_budget = budget_usd
                final_reserve = cash_reserve
                desc = "SPY > SMA 50 -> ตลาดแข็งแกร่ง ลุยเต็มงบ 100%"
                color = "success"
            else:
                status = "🟡 DEFENSE (ตลาดซึม)"
                auth_budget = budget_usd * 0.5
                final_reserve = cash_reserve + (budget_usd * 0.5)
                desc = "ไม่เข้าเงื่อนไข -> ซื้อ 50% ดอง 50%"
                color = "warning"
                
            # โควตา V.600.18 (สายปันผลล้วน)
            alloc = {'XDTE': 0.30, 'QQQI': 0.30, 'SPYI': 0.20, 'SVOL': 0.20}
            vix_msg = "🛡️ SVOL ACTIVE (เก็บปันผลปกติ)"
            
            if vix_price > 20:
                alloc['SPYI'] += alloc['SVOL']
                alloc['SVOL'] = 0.0
                vix_msg = "⚡ DANGER! VIX>20 -> ระงับ SVOL โยกเงินไป SPYI"
                
            # แสดงผลหน้าเว็บ
            st.subheader("📡 1. MACRO RADAR (สภาวะตลาด)")
            col1, col2, col3 = st.columns(3)
            col1.metric("SPY Price", f"${spy_price:.2f}", f"{gap_percent:+.2f}% จาก SMA200")
            col2.metric("SMA 50 (Speed)", f"${sma50:.2f}")
            col3.metric("SMA 200 (Core)", f"${sma200:.2f}")
            
            if color == "success": st.success(f"**สถานะ:** {status} | **คำสั่ง:** {desc}")
            elif color == "warning": st.warning(f"**สถานะ:** {status} | **คำสั่ง:** {desc}")
            else: st.error(f"**สถานะ:** {status} | **คำสั่ง:** {desc}")
                
            st.subheader("🛡️ 2. VIX SHIELD (เกราะป้องกัน)")
            vix_col1, vix_col2 = st.columns([1, 2])
            vix_col1.metric("VIX Index", f"{vix_price:.2f}")
            if vix_price > 20:
                vix_col2.error(f"**{vix_msg}**")
            else:
                vix_col2.success(f"**{vix_msg}**")
                
            st.subheader("💰 3. EXECUTION ORDERS (ใบสั่งรบ)")
            st.info(f"อนุมัติเงินเทรดรอบนี้: **${auth_budget:,.2f}** | เงินสดเก็บไว้เดือนหน้า: **${final_reserve:,.2f}**")
            
            # สร้างตารางคำสั่งซื้อ
            order_data = []
            for asset, weight in alloc.items():
                amt = auth_budget * weight
                action = "BUY 🟢" if amt > 0 else "HOLD ⏸️"
                order_data.append({"Asset": asset, "Target %": f"{weight*100:.0f}%", "Action": action, "Amount (USD)": f"${amt:,.2f}"})
                
            st.table(pd.DataFrame(order_data))
            
            tz_th = pytz.timezone('Asia/Bangkok')
            st.caption(f"อัปเดตข้อมูลล่าสุด: {datetime.datetime.now(tz_th).strftime('%d/%m/%Y %H:%M:%S')} (เวลาไทย)")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")