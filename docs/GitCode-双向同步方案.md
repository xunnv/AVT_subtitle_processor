# GitCode ↔ GitHub 双向 Release 同步方案

> 最后更新：2026-05-23

## 适用仓库

| 平台 | 路径 |
|---|---|
| GitHub | `xunnv/AVT_subtitle_processor` |
| GitCode | `SCPfoundation/AVT_subtitle_processor` |

## 工作流总览

### Workflow 1: `sync-release-to-gitcode.yml`

```
方向: GitHub → GitCode
触发: Release 发布时自动 / 手动 workflow_dispatch（可指定 tag）
行为:
  1. 推送代码 + 所有 Tag 到 GitCode
  2. 在 GitCode 创建同名 Release（包含 Release Notes）
```

### Workflow 2: `sync-from-gitcode.yml`

```
方向: GitCode → GitHub
触发: 每 6 小时 cron / 手动 workflow_dispatch
行为:
  1. 拉取 GitCode 所有 Release 列表
  2. 对比 GitHub 对应 Release，找出缺失的附件
  3. 下载 GitCode 附件 → 上传到 GitHub Release
  4. 只同步 type != "source" 的附件（跳过自动生成的源码包）
```

## 迁移到其他项目

每个文件顶部有 `env` 变量块，迁移只需改 2 行：

```yaml
env:
  GITCODE_USER: SCPfoundation       # 改
  GITCODE_REPO: AVT_subtitle_processor  # 改
```

然后在新仓库配置 `GITCODE_TOKEN` Secret（`Settings → Secrets and variables → Actions`）。

## 你的发布流程

```
1. 在 GitCode 打 Tag、创建 Release、上传附件
2. 6 小时内 GitHub Actions 自动拉附件到 GitHub
3. 如需同步 GitHub Release Notes 到 GitCode：手动触发 sync-release-to-gitcode
```

## 踩坑记录

### 1. GitCode Release body `\r\n` 乱码
- **原因**: `jq --argjson` 造成 JSON 双重转义
- **解决**: 改用 `jq --arg body "$RAW_BODY"`，让 jq 自动处理换行

### 2. 大文件上传 OOM
- **原因**: `curl --data-binary @file` 把 1.5GB 文件读入内存
- **解决**: 改用 `curl -T file` 流式传输

### 3. 附件上传 403
- **原因**: Actions 默认 `GITHUB_TOKEN` 只有 `contents: read`
- **解决**: 添加 `permissions: contents: write`

### 4. GitCode API 能力边界
- ✅ 查询 Release 列表 / 按 Tag 查询 / 创建 Release
- ❌ 上传附件 / 删除 Release / 更新 Release
- 🔑 认证用 Header `PRIVATE-TOKEN`，不是 body 中的 `access_token`

### 5. GitCode 镜像仓库限制
- 镜像仓库锁定外部 push，需改为普通仓库
