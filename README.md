# AIQuotaManager

> 一个桌面端 AI 配额管理工具，帮助重度 AI 用户追踪不同平台的额度重置时间，避免在关键工作中突然额度耗尽。

AIQuotaManager is a lightweight desktop quota tracker for AI platforms. It helps users monitor usage limits, reset schedules, and quota recovery time across different AI services.

## 为什么做这个项目

在频繁使用 ChatGPT、Claude、Gemini、API 平台或其他 AI 工具时，用户经常会遇到一个问题：

- 不知道额度什么时候恢复；
- 不同平台的重置规则不一致；
- 工作过程中突然遇到额度限制；
- 需要手动记忆多个 AI 服务的使用周期。

这个项目希望把这些零散的信息整理成一个简单的桌面工具，让 AI 使用者可以更有计划地安排工作。

## 核心功能

- 添加和管理多个 AI 平台的配额规则；
- 支持倒计时重置和每日定时重置两种模式；
- 使用 Tkinter 构建轻量级桌面 GUI；
- 集成 Windows Toast 通知，在额度重置时提醒用户；
- 支持持续扩展更多平台和更多提醒方式。

## 技术栈

- Python
- Tkinter
- Windows Toast Notification
- 本地配置管理

## 适合谁使用

- 高频使用 AI 工具的个人用户；
- 同时使用多个 AI 平台的创作者、开发者、研究者；
- 希望管理 AI 使用节奏和额度周期的人。

## 快速开始

```bash
git clone https://github.com/libinpg/AIQuotaManager.git
cd AIQuotaManager
python main.py
```

> 如果项目中依赖第三方包，请先根据实际代码安装对应依赖。

## 后续计划

- [ ] 增加更多 AI 平台预设规则；
- [ ] 支持导入 / 导出配置；
- [ ] 增加跨平台通知能力；
- [ ] 增加更清晰的额度日历视图；
- [ ] 优化 UI 交互体验。

## 项目定位

这个项目不是为了做复杂的企业级系统，而是一个面向个人 AI 工作流的效率工具。它关注的是一个很具体的问题：**当 AI 成为日常工具后，如何管理自己的使用节奏。**

## License

MIT License
