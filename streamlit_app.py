import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
from datetime import timezone, timedelta
import tempfile

# 使用临时文件
import tempfile

# 获取或创建用户临时文件
if 'temp_file' not in st.session_state:
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w+', encoding='utf-8')
    temp_file.close()
    st.session_state.temp_file = temp_file.name

# 创建东八区时区
tz = timezone(timedelta(hours=8))

# 初始化数据
if 'records' not in st.session_state:
    st.session_state.records = []

# 每次运行时都重新加载数据
try:
    if os.path.exists(st.session_state.temp_file):
        with open(st.session_state.temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():  # 检查文件内容是否为空
                # 将字符串时间转换为datetime对象
                st.session_state.records = [
                    {**record, 'time': datetime.datetime.fromisoformat(record['time']).astimezone(tz)}
                    for record in json.loads(content)
                ]
            else:
                st.session_state.records = []  # 如果文件为空，初始化空列表
except json.JSONDecodeError as e:
    st.error(f'JSON格式错误：{str(e)}')
    st.session_state.records = []
except Exception as e:
    st.error(f'数据加载失败：{str(e)}')
    st.session_state.records = []

# 页面标题
st.title('InfectionAlert')
st.caption('身边人的患病计数器')

# 使用tabs来组织文件操作
tab1, tab2, tab3 = st.tabs(["上传数据", "下载数据", "管理数据"])

with tab1:
    # 文件上传组件
    uploaded_file = st.file_uploader("上传JSON文件", type=['json'], help="请选择要上传的JSON文件")
    if uploaded_file is not None:
        try:
            # 读取上传的文件
            data = json.load(uploaded_file)
            # 转换时间格式
            st.session_state.records = [
                {**record, 'time': datetime.datetime.fromisoformat(record['time']).astimezone(tz)}
                for record in data
            ]
            # 保存到临时文件
            with open(st.session_state.temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.success('文件上传成功！')
            st.rerun()
        except Exception as e:
            st.error(f'文件上传失败：{str(e)}')

with tab2:
    if st.session_state.records:
        # 将数据转换为JSON字符串
        json_data = json.dumps([
            {**record, 'time': record['time'].isoformat()}
            for record in st.session_state.records
        ], ensure_ascii=False, indent=2)

        # 创建下载按钮
        st.download_button(
            label="下载当前数据",
            data=json_data,
            file_name='records.json',
            mime='application/json',
            help="点击下载当前所有记录数据"
        )
    else:
        st.warning("暂无数据可供下载")

with tab3:
    if st.session_state.records:
        # 将数据转换为DataFrame
        df = pd.DataFrame(st.session_state.records)
        # 添加索引列
        df['index'] = range(len(df))
        # 只显示需要的列
        edited_df = st.data_editor(
            df[['index', 'time', 'total', 'sick', 'rate']],
            column_config={
                "index": "序号",
                "time": "时间",
                "total": "总人数",
                "sick": "患病人数",
                "rate": st.column_config.NumberColumn(
                    "患病率 (%)",
                    format="%.2f %%"
                )
            },
            num_rows="dynamic",
            use_container_width=True
        )

        # 创建两列布局
        col1, col2 = st.columns(2)
        with col1:
            # 保存修改按钮
            if st.button('保存修改'):
                try:
                    # 将修改后的数据转换回原始格式
                    st.session_state.records = [
                        {
                            'time': datetime.datetime.fromisoformat(row['time']).astimezone(tz),
                            'total': row['total'],
                            'sick': row['sick'],
                            'rate': row['rate']
                        }
                        for row in edited_df.to_dict('records')
                    ]

                    # 保存到临时文件
                    with open(st.session_state.temp_file, 'w', encoding='utf-8') as f:
                        json.dump([
                            {**record, 'time': record['time'].isoformat()}
                            for record in st.session_state.records
                        ], f, ensure_ascii=False, indent=2)

                    st.success('修改已保存！')
                    st.rerun()
                except Exception as e:
                    st.error(f'保存失败：{str(e)}')

        with col2:
            # 添加一键清空按钮
            if st.button('一键清空', type="primary"):
                st.session_state.records = []
                try:
                    with open(st.session_state.temp_file, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    st.success('数据已清空！')
                    st.rerun()
                except Exception as e:
                    st.error(f'清空失败：{str(e)}')
    else:
        st.warning("暂无数据可供编辑")

# 输入区域
col1, col2 = st.columns(2)
with col1:
    total = st.number_input('总人数', min_value=1, value=28)
with col2:
    sick = st.number_input('患病人数', min_value=0, value=9)

# 创建两列布局
col1, col2 = st.columns([3, 1])  # 调整列宽比例
with col1:
    use_current_time = st.checkbox('使用当前时间', value=True)
    if not use_current_time:
        # 添加日期和时间选择器
        selected_date = st.date_input("选择日期", datetime.date.today())
        selected_time = st.time_input("选择时间", datetime.time(12, 0))
        # 修改这里：将用户选择的时间标记为东八区时间
        record_time = datetime.datetime.combine(selected_date, selected_time).replace(tzinfo=tz)
    else:
        # 使用东八区时间
        record_time = datetime.datetime.now(tz)

with col2:
    if st.button('添加记录'):
        record = {
            'time': record_time.astimezone(tz),
            'total': total,
            'sick': sick,
            'rate': sick / total * 100
        }
        st.session_state.records.append(record)

        # 保存到临时文件
        with open(st.session_state.temp_file, 'w', encoding='utf-8') as f:
            # 将datetime对象转换为字符串
            json.dump([
                {**record, 'time': record['time'].isoformat()}
                for record in st.session_state.records
            ], f, ensure_ascii=False, indent=2)

        st.success('记录已添加！')
        st.rerun()  # 刷新页面

# 绘制圆圈图和折线图
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)

    # 时间选择器卡片
    with st.container():
        st.subheader("选择对比时间")
        time_options = sorted([
            record['time'].astimezone(tz) if record['time'].tzinfo is None else record['time']
            for record in st.session_state.records
        ], reverse=True)
        col1, col2 = st.columns(2)
        with col1:
            # 默认选择最早的时间点（列表最后一个）
            time1 = st.selectbox("较早时间点", time_options, index=len(time_options)-1)
        with col2:
            # 默认选择最新的时间点（列表第一个）
            time2 = st.selectbox("较晚时间点", time_options, index=0)

    # 图表区域
    col1, col2 = st.columns(2)
    with col1:
        # 获取两个时间点的记录
        record1 = next(r for r in st.session_state.records if r['time'] == time1)
        record2 = next(r for r in st.session_state.records if r['time'] == time2)

        # 计算变化量
        sick_change = record2['sick'] - record1['sick']
        healthy_change = (record2['total'] - record2['sick']) - (record1['total'] - record1['sick'])

        # 绘制对比圆圈图
        labels = ['新增患病', '新增健康', '原有患病', '原有健康']
        values = [
            max(0, sick_change),  # 新增患病
            max(0, healthy_change),  # 新增健康
            min(record1['sick'], record2['sick']),  # 原有患病
            min(record1['total'] - record1['sick'], record2['total'] - record2['sick'])  # 原有健康
        ]

        fig = px.pie(
            names=labels,
            values=values,
            hole=0.5,
            title=f'患病变化对比 ({time2.strftime("%Y-%m-%d")} → {time1.strftime("%Y-%m-%d")})'
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(colors=['#FF6961', '#77DD77', '#FFA07A', '#90EE90']),
            hoverinfo='label+percent'
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=50, b=0, l=0, r=0),
            height=360,
            title=dict(
                text=f'患病变化对比 ({time2.strftime("%Y-%m-%d")} → {time1.strftime("%Y-%m-%d")})',
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 绘制折线图
        if df.shape[0] > 0:
            # 确保数据按时间排序
            df = df.sort_values('time')

            fig2 = px.line(
                df,
                x='time',
                y='rate',
                markers=True,
                title='患病率趋势',
                labels={'time': '时间', 'rate': '患病率 (%)'},
                line_shape='linear'  # 确保是直线连接
            )
            fig2.update_traces(
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#ff7f0e'),
                connectgaps=True  # 确保连续连接
            )
            fig2.update_layout(
                xaxis_title='时间',
                yaxis_title='患病率 (%)',
                hovermode='x unified',
                height=400,
                title=dict(
                    text='患病率趋势',
                    y=0.95,
                    x=0.5,
                    xanchor='center',
                    yanchor='top'
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("暂无数据可供绘制")
