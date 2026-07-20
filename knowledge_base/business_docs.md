# 业务文档

## 老系统对接规范
- 使用REST API，认证方式Bearer Token
- 主要接口：/sync/data, /legacy/query

## 数据监听要求
- 每5分钟轮询MySQL变化
- 支持文件增量更新检测

## 项目数据分析KPI
- 总价值计算、趋势分析
- 生成Excel/PDF报告

## 知识库维护
- 定期更新向量数据库
- 支持中文语义搜索