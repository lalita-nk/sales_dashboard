# Sales Dashboard — Streamlit
# วิธีรัน:  streamlit run app.py

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ให้ matplotlib วาดภาพได้โดยไม่ต้องเปิดหน้าต่าง

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# ---------- 0. ตั้งค่าหน้าเว็บ ----------
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

DATA_FILE = Path(__file__).parent / "sale_mini_clean.csv"
DATA_URL = "https://drive.google.com/uc?id=1fWdzPF6BdlMxKquUrD_KYnRbih2rLXgS"
REQUIRED_COLS = ["date", "branch", "product", "category", "quantity", "unit_price", "customer_id"]

# สีประจำหมวด ใช้ชุดเดียวกันทุกกราฟ
BASE_CAT_COLORS = {"Beverage": "#4C72B0", "Snack": "#DD8452", "Stationery": "#55A868"}
MAIN_COLOR = "#4C72B0"

sns.set_theme(style="white")


# ---------- 1. เตรียมข้อมูล ----------
@st.cache_data
def read_csv(source):
    return pd.read_csv(source)


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df = df.dropna(subset=["date", "quantity", "unit_price"])
    df["total"] = df["quantity"] * df["unit_price"]
    df["customer_id"] = df["customer_id"].fillna("Unknown").astype(str)
    for col in ["branch", "product", "category"]:
        df[col] = df[col].astype(str)
    return df


def load_data():
    """ลำดับการโหลด: ไฟล์ที่อัปโหลด → ไฟล์ข้างๆ app.py → ลิงก์ Google Drive"""
    uploaded = st.sidebar.file_uploader("อัปโหลดไฟล์ CSV (ไม่บังคับ)", type="csv")
    if uploaded is not None:
        return read_csv(uploaded), f"ไฟล์ที่อัปโหลด: {uploaded.name}"
    if DATA_FILE.exists():
        return read_csv(DATA_FILE), f"ไฟล์ในเครื่อง: {DATA_FILE.name}"
    try:
        return read_csv(DATA_URL), "Google Drive"
    except Exception:
        return None, None


raw, source_name = load_data()

if raw is None:
    st.error(
        "ไม่พบข้อมูล: วางไฟล์ `sale_mini_clean.csv` ไว้โฟลเดอร์เดียวกับ `app.py` "
        "หรืออัปโหลดไฟล์ CSV จากแถบด้านซ้าย"
    )
    st.stop()

missing = [c for c in REQUIRED_COLS if c not in raw.columns]
if missing:
    st.error(f"ไฟล์ขาดคอลัมน์ที่จำเป็น: {', '.join(missing)}")
    st.stop()

df_all = prepare(raw)
if df_all.empty:
    st.error("ไม่มีข้อมูลที่ใช้ได้ (ตรวจสอบคอลัมน์ date, quantity, unit_price)")
    st.stop()

# สีประจำหมวด: หมวดที่ไม่อยู่ในชุดหลักจะได้สีจาก palette เพิ่มอัตโนมัติ
extra_cats = [c for c in sorted(df_all["category"].unique()) if c not in BASE_CAT_COLORS]
extra_colors = sns.color_palette("deep", len(BASE_CAT_COLORS) + len(extra_cats)).as_hex()
CAT_COLORS = {**BASE_CAT_COLORS, **dict(zip(extra_cats, extra_colors[len(BASE_CAT_COLORS):]))}

# ---------- 2. ตัวกรอง (sidebar) ----------
st.sidebar.header("ตัวกรอง")

drop_outlier_date = st.sidebar.checkbox("ตัดรายการที่วันที่เกิน 31 ต.ค. 2026", value=True)
if drop_outlier_date:
    df_all = df_all[df_all["date"] <= "2026-10-31"]
    if df_all.empty:
        st.warning("ไม่มีข้อมูลก่อนวันที่ 31 ต.ค. 2026 ลองเอาเครื่องหมายถูกในตัวกรองนี้ออก")
        st.stop()

min_date, max_date = df_all["date"].min().date(), df_all["date"].max().date()
date_range = st.sidebar.date_input(
    "ช่วงวันที่", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
# ระหว่างที่ผู้ใช้เลือกวันแรกแล้วยังไม่เลือกวันสุดท้าย จะได้ค่ามาแค่วันเดียว
if isinstance(date_range, (list, tuple)):
    start, end = (date_range[0], date_range[-1]) if date_range else (min_date, max_date)
else:
    start = end = date_range

branches = sorted(df_all["branch"].unique())
sel_branches = st.sidebar.multiselect("สาขา", branches, default=branches)

categories = sorted(df_all["category"].unique())
sel_categories = st.sidebar.multiselect("หมวดสินค้า", categories, default=categories)

df = df_all[
    (df_all["date"].dt.date >= start)
    & (df_all["date"].dt.date <= end)
    & (df_all["branch"].isin(sel_branches))
    & (df_all["category"].isin(sel_categories))
]

st.sidebar.caption(f"แหล่งข้อมูล: {source_name}")
st.sidebar.caption(f"แสดง {len(df):,} จาก {len(df_all):,} รายการ")

# ---------- 3. หัวเรื่อง ----------
st.title("📊 Sales Dashboard")
st.caption(f"ช่วงวันที่ {start:%d %b %Y} – {end:%d %b %Y}")

if df.empty:
    st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก ลองเลือกสาขา หมวดสินค้า หรือช่วงวันที่เพิ่ม")
    st.stop()

# ---------- 4. ตัวเลขสรุป (KPI) ----------
total_sales = df["total"].sum()
transactions = len(df)
avg_sale = df["total"].mean()
members = df.loc[df["customer_id"] != "Unknown", "customer_id"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total sales", f"{total_sales:,.0f} ฿", border=True)
k2.metric("Transactions", f"{transactions:,}", border=True)
k3.metric("Avg per transaction", f"{avg_sale:,.0f} ฿", border=True)
k4.metric("Members", f"{members:,}", border=True)

# ---------- 5. ตารางสรุปสำหรับแต่ละกราฟ ----------
daily_sales = df.groupby("date", as_index=False)["total"].sum()
branch_sales = df.groupby("branch", as_index=False)["total"].sum().sort_values("total", ascending=False)
product_sales = df.groupby("product", as_index=False)["total"].sum().sort_values("total", ascending=False)
sales_table = df.groupby(["branch", "category"])["total"].sum().unstack(fill_value=0)


def show(fig):
    """แสดงกราฟใน Streamlit แล้วปิด figure เพื่อไม่ให้กินหน่วยความจำ"""
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


tab_charts, tab_data = st.tabs(["กราฟ", "ข้อมูล"])

with tab_charts:
    # แถวที่ 1: Line (ยอดขายรายวัน) + Bar (ยอดขายตามสาขา)
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Daily Sales")
        fig, ax = plt.subplots(figsize=(10, 4.2))
        sns.lineplot(data=daily_sales, x="date", y="total", marker="o", color=MAIN_COLOR, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Total sales (baht)")
        ax.set_ylim(0, daily_sales["total"].max() * 1.15)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        show(fig)

    with c2:
        st.subheader("Sales by Branch")
        fig, ax = plt.subplots(figsize=(5, 4.2))
        sns.barplot(data=branch_sales, x="branch", y="total", color=MAIN_COLOR, ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt="{:,.0f}", padding=3)
        ax.set_xlabel("")
        ax.set_ylabel("Total sales (baht)")
        ax.margins(y=0.15)
        show(fig)

    # แถวที่ 2: Barh (อันดับสินค้า) + Histogram + Boxplot
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Product Ranking")
        fig, ax = plt.subplots(figsize=(5, 4.5))
        sns.barplot(data=product_sales, x="total", y="product", color=MAIN_COLOR, ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt="{:,.0f}", padding=3)
        ax.set_xlabel("Total sales (baht)")
        ax.set_ylabel("")
        ax.margins(x=0.25)
        show(fig)

    with c2:
        st.subheader("Sales per Transaction")
        fig, ax = plt.subplots(figsize=(5, 4.5))
        max_total = df["total"].max()
        bins = range(0, int(max_total) + 200, 100) if max_total <= 2000 else 20
        sns.histplot(data=df, x="total", bins=bins, color=MAIN_COLOR, edgecolor="white", ax=ax)
        ax.set_xlabel("Total (baht)")
        ax.set_ylabel("Number of transactions")
        show(fig)

    with c3:
        st.subheader("Spread by Category")
        fig, ax = plt.subplots(figsize=(5, 4.5))
        sns.boxplot(
            data=df, x="category", y="total", hue="category",
            palette=CAT_COLORS, legend=False, ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel("Total (baht)")
        show(fig)

    # แถวที่ 3: Heatmap + Scatter
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Sales by Branch and Category")
        fig, ax = plt.subplots(figsize=(10, 4.2))
        sns.heatmap(
            sales_table, annot=True, fmt=",.0f", cmap="Blues",
            linewidths=2, linecolor="white", ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="y", rotation=0)
        show(fig)

    with c2:
        st.subheader("Quantity vs. Unit Price")
        fig, ax = plt.subplots(figsize=(5, 4.2))
        sns.scatterplot(
            data=df, x="unit_price", y="quantity", hue="category",
            palette=CAT_COLORS, s=90, ax=ax,
        )
        ax.set_xlabel("Unit price (baht)")
        ax.set_ylabel("Quantity")
        if ax.get_legend() is not None:
            ax.legend(title="", fontsize=9)
        show(fig)

with tab_data:
    st.subheader("ข้อมูลตามตัวกรอง")
    show_df = df.sort_values("date").assign(date=lambda d: d["date"].dt.date)
    st.dataframe(show_df, hide_index=True)
    st.download_button(
        "ดาวน์โหลดเป็น CSV",
        data=show_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="sales_filtered.csv",
        mime="text/csv",
    )
