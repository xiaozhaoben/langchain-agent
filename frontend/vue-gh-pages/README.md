# Vue GitHub Pages 模块

该模块可独立运行并通过 GitHub Actions 部署到 GitHub Pages。

## 本地运行

```bash
cd frontend/vue-gh-pages
npm install
npm run dev
```

## 构建

```bash
npm run build
```

构建产物目录：`dist/`

## 部署到 GitHub Pages

1. 将本仓库推送到 GitHub。
2. 在仓库 **Settings → Pages** 中，将 Source 设为 **GitHub Actions**。
3. 推送到 `main` 分支后，工作流会自动构建并部署。
