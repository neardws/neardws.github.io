# Sub-agent Prompt Template

## 标准指令（自动注入）

```
## 执行规范

1. **静默执行**：正常过程不输出，专注完成任务
2. **重要事件汇报**：遇到以下情况时，用 message 工具发送到 Telegram：
   - 🚨 错误/异常：无法继续执行
   - ⚠️ 需要决策：遇到歧义需要确认
   - ✅ 关键里程碑：重大进展完成
3. **最终总结**：任务完成后通过 announce 汇报结果

## 汇报格式

重要事件：
[子代理名称] <emoji> <简短描述>
例：[搜索] 🚨 API 限流，已切换备用源

最终 announce：
- 任务：<原始任务>
- 状态：成功/失败/部分完成
- 结果：<核心产出>
- 耗时：<执行时间>
```

## 使用示例

```typescript
sessions_spawn({
  task: `${STANDARD_INSTRUCTIONS}\n\n实际任务：搜索最新 AI 新闻`,
  model: "cheap",
  label: "搜索"
})
```
