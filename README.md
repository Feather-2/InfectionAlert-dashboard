# InfectionAlert 仪表盘

## 简介
InfectionAlert 是一个用于追踪和可视化身边人群患病情况的仪表盘应用。它可以帮助用户记录和监控特定群体的健康状况，并通过直观的图表展示患病率的变化趋势。

## 功能特性
- 📊 实时数据记录：记录总人数和患病人数
- ⏰ 时间选择：支持自定义记录时间或使用当前时间
- 📈 数据可视化：
  - 患病率趋势折线图
  - 患病变化对比饼图
- 📁 数据管理：
  - 上传/下载JSON格式数据
  - 在线编辑数据
  - 一键清空数据
- 🌐 时区支持：自动处理东八区时间

## 使用方法
1. 在页面下方输入总人数和患病人数
2. 选择是否使用当前时间，或手动选择日期和时间
3. 点击"添加记录"按钮保存数据
4. 使用顶部标签页进行数据管理：
   - 上传数据：导入已有的JSON格式数据
   - 下载数据：导出当前所有记录
   - 管理数据：编辑或删除现有记录

## 数据格式
数据以JSON格式存储，包含以下字段：
```json
{
"time": "ISO格式时间字符串",
"total": "总人数",
"sick": "患病人数",
"rate": "患病率百分比"
}
```

## 在线访问
[点击这里访问在线应用](https://infectionalert-dashboard-feather.streamlit.app/)


## 注意事项
- 数据存储在浏览器临时文件中，清除浏览器缓存会导致数据丢失
- 建议定期下载数据备份
- 上传文件需符合指定JSON格式

## 许可证
MIT License
