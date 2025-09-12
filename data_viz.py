import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ========================
# 多语言支持
# ========================
def get_text(language):
    texts = {
        "zh": {
            "title": "📊 分拣业务运营可视化面板",
            "date_note": "以下数据为{}的数据",
            "kpi1": "总集包票数",
            "kpi2": "错分率(%)",
            "kpi3": "总工时",
            "kpi4": "人效(票/小时)",
            "kpi5": "机器分拣量",
            "note": "💡 说明：人效(票/小时) = 总集包票数 ÷ 总工时；总工时包含 JOY、DELIN、RAPID、MB 的早、中、晚班工时（不含 PR 工时）。",
            "chart_title": "分拣业务可视化面板",
            "chart1": "每日分拣总量 & 错分率(%)",
            "chart2": "每日工时 & 人效趋势",
            "chart3": "人工 vs 机器分拣量",
            "data_title": "📄 详细数据",
            "filter_title": "筛选条件",
            "date_range": "选择日期范围"
        },
        "en": {
            "title": "📊 Sorting Operation Dashboard",
            "date_note": "Data as of {}",
            "kpi1": "Total Packages",
            "kpi2": "Error Rate(%)",
            "kpi3": "Total Hours",
            "kpi4": "Efficiency(pcs/hour)",
            "kpi5": "Machine Sorting Volume",
            "note": "💡 Note: Efficiency = Total Packages ÷ Total Hours; Total hours include JOY, DELIN, RAPID, MB shifts (excluding PR hours).",
            "chart_title": "Sorting Operation Dashboard",
            "chart1": "Daily Sorting Volume & Error Rate",
            "chart2": "Daily Hours & Efficiency Trend",
            "chart3": "Manual vs Machine Sorting",
            "data_title": "📄 Detailed Data",
            "filter_title": "Filters",
            "date_range": "Select Date Range"
        }
    }
    return texts.get(language, texts["zh"])

# 初始化语言设置
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# ========================
# 读取数据
# ========================
df = pd.read_csv("data.csv", encoding="utf-8")

# 计算错分率、人效、人工分拣量
df['错分率(%)'] = df['错分票数'] / df['总集包票数']*100
df['总工时'] = df['JOY工时'] + df['DELIN工时'] + df['RAPID工时'] + df['MB工时']
df['人效(票/小时)'] = df['总集包票数'] / df['总工时']
df['人工分拣量'] = df['总集包票数'] - df['分拣机分拣量']

df['日期'] = pd.to_datetime(df['日期'], format="%m月%d日")
df['日期'] = df['日期'].apply(lambda d: d.replace(year=2025))

# 获取当前筛选范围的最后一天数据
latest_date = df['日期'].max()
latest_row = df[df['日期'] == latest_date].iloc[0]

# ========================
# 页面配置
# ========================
st.set_page_config(page_title="分拣业务可视化面板", layout="wide")

# ========================
# 侧边栏筛选和语言切换
# ========================
st.sidebar.header(get_text(st.session_state.language)["filter_title"])

# 语言切换按钮
if st.sidebar.button("English/中文"):
    st.session_state.language = "en" if st.session_state.language == "zh" else "zh"

date_range = st.sidebar.date_input(
    get_text(st.session_state.language)["date_range"], 
    []
)
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df['日期'] >= pd.to_datetime(start_date)) & (df['日期'] <= pd.to_datetime(end_date))]

# ========================
# KPI 指标卡片
# ========================
text = get_text(st.session_state.language)
st.title(text["title"])

# 在 KPI 卡片前加提示
st.markdown(f"**{text['date_note'].format(latest_date.strftime('%Y-%m-%d'))}**")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(text["kpi1"], f"{latest_row['总集包票数']:,}")
col2.metric(text["kpi2"], f"{latest_row['错分率(%)']:.3f}")
col3.metric(text["kpi3"], f"{latest_row['总工时']:.2f}")
col4.metric(text["kpi4"], f"{latest_row['人效(票/小时)']:.2f}")
col5.metric(text["kpi5"], f"{latest_row['分拣机分拣量']:,}")

# 备注说明
st.caption(text["note"])

# ========================
# 创建 subplot 面板（3 行 1 列）
# ========================
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=(text["chart1"], text["chart2"], text["chart3"]),
    specs=[[{"secondary_y": True}],
           [{"secondary_y": True}],
           [{"secondary_y": False}]]
)

# ==== 图1 ====
fig.add_trace(
    go.Bar(x=df['日期'], y=df['总集包票数'], name='总集包票数', marker_color='skyblue'),
    row=1, col=1, secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df['日期'], y=df['错分率(%)'], name='错分率(%)', mode='lines+markers', line=dict(color='red')),
    row=1, col=1, secondary_y=True
)

# ==== 图2 ====
fig.add_trace(
    go.Bar(x=df['日期'], y=df['JOY工时'], name='JOY工时', marker_color='orange'),
    row=2, col=1, secondary_y=False
)
fig.add_trace(
    go.Bar(x=df['日期'], y=df['DELIN工时'], name='DELIN工时', marker_color='green'),
    row=2, col=1, secondary_y=False
)
fig.add_trace(
    go.Bar(x=df['日期'], y=df['RAPID工时'], name='RAPID工时', marker_color='purple'),
    row=2, col=1, secondary_y=False
)
fig.add_trace(
    go.Bar(x=df['日期'], y=df['MB工时'], name='MB工时', marker_color='brown'),
    row=2, col=1, secondary_y=False
)

fig.add_trace(
    go.Scatter(x=df['日期'], y=df['人效(票/小时)'], name='人效(票/小时)', mode='lines+markers', line=dict(color='blue')),
    row=2, col=1, secondary_y=True
)

# ==== 图3 ====
fig.add_trace(
    go.Bar(x=df['日期'], y=df['人工分拣量'], name='人工分拣量', marker_color='coral'),
    row=3, col=1
)
fig.add_trace(
    go.Bar(x=df['日期'], y=df['分拣机分拣量'], name='分拣机分拣量', marker_color='skyblue'),
    row=3, col=1
)

# 布局设置
fig.update_layout(
    title_text=text["chart_title"],
    barmode='stack',
    height=900,
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)
fig.update_yaxes(title_text="票数", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="错分率(%)", row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="工时", row=2, col=1, secondary_y=False)
fig.update_yaxes(title_text="人效(票/小时)", row=2, col=1, secondary_y=True)
fig.update_yaxes(title_text="票数", row=3, col=1)

# ========================
# 显示图表
# ========================
st.plotly_chart(fig, use_container_width=True)

# ========================
# 详细数据表
# ========================
st.subheader(text["data_title"])
st.dataframe(df)