# 加密云存档 API

这里保留已部署云服务的关键源码和数据库迁移，便于审阅与维护。运行中的服务由独立 Sites 项目托管；GitHub Pages 只发布 `docs/` 网页。

客户端使用随机连接码派生 AES-256-GCM 密钥与认证令牌。服务端只接收密文，以配置好的个人存档 ID 和令牌摘要限制读写，并用 revision 检查防止旧设备覆盖新进度。CORS 允许学习网站与本地检查页面。

生产连接码、令牌、认证摘要和学习进度均不在此目录。`db/schema.ts` 是 Drizzle 表结构，`drizzle/` 是生成并已应用的迁移，`lib/sync-api.mjs` 提供请求处理。

在支持 `node:sqlite` 的 Node 中，可以执行 `node cloud-api/tests/sync.test.mjs` 检查认证、来源限制、加密载荷格式、并发冲突和上次存档备份。
