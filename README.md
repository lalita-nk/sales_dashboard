# Sales Dashboard (Streamlit)

Dashboard ยอดขายแบบ interactive แปลงมาจากโค้ด matplotlib/seaborn เดิม เพิ่มตัวกรองช่วงวันที่ สาขา และหมวดสินค้า ทุกกราฟและตัวเลข KPI เปลี่ยนตามตัวกรองทันที
ข้อมูลนี้ใช้กับไฟล์ตัวอย่าง sale_mini_clean.csv

ตัวอย่างผลลัพธ์ เมื่อนำไปทดลองรันบน local --> https://salesdashboardds.streamlit.app/

หมายเหตุ: หากไม่ทำงาน ให้คลิก "Yes, get this app back up!" เพื่อกระตุ้นให้หน้าแอปทำงาน

## ไฟล์ในโฟลเดอร์

```
sales_dashboard/
├── app.py                 # โค้ด dashboard
├── requirements.txt       # รายชื่อ library ที่ต้องติดตั้ง
├── sale_mini_clean.csv    # ข้อมูลยอดขาย
└── README.md              # ไฟล์นี้
```

ต้องวางทุกไฟล์ไว้ในโฟลเดอร์เดียวกัน

## ขั้นตอนการติดตั้งและรัน

ต้องมี **Python 3.9 ขึ้นไป** ตรวจสอบได้ด้วยคำสั่ง `python --version` (บน Mac/Linux อาจต้องใช้ `python3`)

**1. เปิด Terminal แล้วเข้าไปที่โฟลเดอร์**

```bash
cd path/to/sales_dashboard
```

**2. สร้าง virtual environment** (แนะนำ เพื่อไม่ให้ชนกับ library อื่นในเครื่อง)

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

เมื่อสำเร็จจะเห็น `(.venv)` นำหน้าบรรทัดคำสั่ง

**3. ติดตั้ง library**

```bash
pip install -r requirements.txt
```

**4. รัน dashboard**

```bash
streamlit run app.py
```

เบราว์เซอร์จะเปิดหน้า `http://localhost:8501` ให้อัตโนมัติ ถ้าไม่เปิดเอง ให้คัดลอกลิงก์นี้ไปวางในเบราว์เซอร์

**5. ปิด dashboard** กด `Ctrl + C` ใน Terminal

ครั้งต่อไปที่จะรัน ทำแค่ขั้นที่ 1, activate virtual environment ในขั้นที่ 2 และขั้นที่ 4

## การใช้งาน

- **แถบด้านซ้าย** ใช้กรองช่วงวันที่ สาขา และหมวดสินค้า
- **ตัดรายการที่วันที่เกิน 31 ต.ค. 2026** เปิดไว้เป็นค่าเริ่มต้น (ตรงกับโค้ดเดิมที่ตัด INV022)
- **อัปโหลดไฟล์ CSV** ใช้แทนไฟล์ในโฟลเดอร์ได้ ไฟล์ต้องมีคอลัมน์ `date, branch, product, category, quantity, unit_price, customer_id`
- **แท็บ "ข้อมูล"** แสดงตารางตามตัวกรอง และดาวน์โหลดเป็น CSV ได้

## ลำดับที่แอปค้นหาข้อมูล

1. ไฟล์ที่อัปโหลดจากแถบด้านซ้าย
2. ไฟล์ `sale_mini_clean.csv` ที่อยู่โฟลเดอร์เดียวกับ `app.py`
3. ลิงก์ Google Drive ในโค้ด (ต้องต่ออินเทอร์เน็ต)

## ปัญหาที่อาจพบ

| อาการ | วิธีแก้ |
|---|---|
| `'streamlit' is not recognized` / `command not found` | ยังไม่ได้ activate virtual environment (ขั้นที่ 2) หรือใช้ `python -m streamlit run app.py` แทน |
| `ModuleNotFoundError` | ติดตั้ง library ไม่ครบ ให้รัน `pip install -r requirements.txt` อีกครั้ง |
| หน้าเว็บขึ้น "ไม่พบข้อมูล" | ไม่มีไฟล์ CSV ในโฟลเดอร์และเชื่อมต่อ Google Drive ไม่ได้ ให้วาง `sale_mini_clean.csv` ไว้ข้างๆ `app.py` |
| `Port 8501 is already in use` | มี dashboard อีกตัวเปิดอยู่ ปิดตัวเดิม หรือรัน `streamlit run app.py --server.port 8502` |
