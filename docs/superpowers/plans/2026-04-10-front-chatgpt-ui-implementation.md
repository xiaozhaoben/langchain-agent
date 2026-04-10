# Front ChatGPT UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `front` 原生静态聊天页改造成深色 ChatGPT 风格聊天界面，同时保留现有单会话与 SSE 流式回复能力。

**Architecture:** 继续使用 `front/index.html` + `front/static/styles.css` + `front/static/app.js` 的原生静态架构，不引入新前端框架。通过先补最小 Node + JSDOM 测试支撑，再重构 HTML 骨架、前端交互逻辑和深色样式，实现可测试的 UI 重构。运行时仍由 `front/server.py` 提供静态资源和 `/api/chat` SSE 接口。

**Tech Stack:** HTML5, CSS3, 原生 ES Module JavaScript, Python `http.server`, Node.js `node:test`, JSDOM

---

## File Map

- Create: `front/package.json`
- Create: `front/tests/app.test.js`
- Modify: `front/index.html`
- Modify: `front/static/app.js`
- Modify: `front/static/styles.css`
- Verify: `front/server.py`

## Task 1: 建立前端最小测试支撑并让脚本可被测试导入

**Files:**
- Create: `front/package.json`
- Create: `front/tests/app.test.js`
- Modify: `front/static/app.js`

- [ ] **Step 1: 写失败测试，要求 `app.js` 可导入且空会话时显示欢迎态**

在 `front/tests/app.test.js` 中写入：

```js
import test from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";

function buildDom() {
  return new JSDOM(
    `<!DOCTYPE html>
    <html lang="zh-CN">
      <body>
        <div class="app-shell">
          <aside class="sidebar">
            <button id="new-chat" type="button">新对话</button>
            <button id="clear-history" type="button">清空会话</button>
            <button class="prompt-chip" type="button">扫地机器人怎么保养？</button>
          </aside>
          <main class="chat-main">
            <header class="chat-topbar"></header>
            <section id="message-scroll" class="message-scroll">
              <section id="message-list" class="message-list"></section>
              <section id="empty-state" class="empty-state">
                <h1>今天想了解你的扫地机器人什么问题？</h1>
              </section>
            </section>
            <form id="chat-form" class="composer-form">
              <textarea id="message-input" name="message"></textarea>
              <button id="send-button" type="submit">发送</button>
              <p id="status-text"></p>
            </form>
            <template id="message-template">
              <article class="message">
                <div class="message-avatar"></div>
                <div class="message-body">
                  <div class="message-meta"></div>
                  <div class="message-bubble"></div>
                </div>
              </article>
            </template>
          </main>
        </div>
      </body>
    </html>`,
    { url: "http://localhost/" }
  );
}

test("initChatApp shows empty state when no cached messages exist", async () => {
  const dom = buildDom();
  global.window = dom.window;
  global.document = dom.window.document;
  global.sessionStorage = dom.window.sessionStorage;

  const { initChatApp } = await import("../static/app.js");
  const app = initChatApp();

  assert.equal(app.state.messages.length, 0);
  assert.equal(document.querySelector("#empty-state").hidden, false);
  assert.equal(document.querySelector("#message-list").children.length, 0);
  assert.equal(document.querySelector("#status-text").textContent, "等待提问");
});
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run: `npm test -- --testNamePattern="empty state"`, working directory `D:\langchain-agent\front`

Expected: FAIL，报错类似 `initChatApp is not exported` 或 `document is not defined`

- [ ] **Step 3: 增加测试依赖声明，并把脚本改成可导入的初始化函数**

在 `front/package.json` 中写入：

```json
{
  "name": "langchain-agent-front",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test"
  },
  "dependencies": {
    "jsdom": "^24.1.3"
  }
}
```

将 `front/static/app.js` 重构为以初始化函数为入口，最小骨架如下：

```js
const STORAGE_KEY = "langchain-agent-front-history";

function loadMessages(storage) {
  try {
    const cached = storage.getItem(STORAGE_KEY);
    return cached ? JSON.parse(cached) : [];
  } catch (error) {
    return [];
  }
}

export function initChatApp(root = document) {
  const elements = {
    form: root.querySelector("#chat-form"),
    input: root.querySelector("#message-input"),
    sendButton: root.querySelector("#send-button"),
    statusText: root.querySelector("#status-text"),
    messageList: root.querySelector("#message-list"),
    emptyState: root.querySelector("#empty-state"),
    template: root.querySelector("#message-template"),
    clearHistory: root.querySelector("#clear-history"),
    newChat: root.querySelector("#new-chat"),
    promptChips: root.querySelectorAll(".prompt-chip"),
  };

  const state = {
    messages: loadMessages(window.sessionStorage),
    isSending: false,
  };

  function setStatus(text) {
    elements.statusText.textContent = text;
  }

  function renderMessages() {
    elements.messageList.innerHTML = "";
    elements.emptyState.hidden = state.messages.length > 0;
  }

  renderMessages();
  setStatus("等待提问");

  return { elements, state };
}

if (typeof document !== "undefined") {
  initChatApp();
}
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `npm test -- --testNamePattern="empty state"`, working directory `D:\langchain-agent\front`

Expected: PASS，输出 1 passed

- [ ] **Step 5: 提交这一小步**

```bash
git add front/package.json front/tests/app.test.js front/static/app.js
git commit -m "test(front): add app bootstrap tests"
```

## Task 2: 重构 HTML 骨架为 ChatGPT 风格双栏布局

**Files:**
- Modify: `front/index.html`
- Test: `front/tests/app.test.js`

- [ ] **Step 1: 写失败测试，要求页面包含侧栏、顶部栏、消息滚动区和贴底输入区**

在 `front/tests/app.test.js` 追加：

```js
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

test("index.html exposes the new chatgpt-like layout hooks", () => {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const html = fs.readFileSync(path.join(currentDir, "..", "index.html"), "utf8");

  assert.match(html, /class="app-shell"/);
  assert.match(html, /class="sidebar"/);
  assert.match(html, /id="new-chat"/);
  assert.match(html, /class="chat-main"/);
  assert.match(html, /id="message-scroll"/);
  assert.match(html, /class="composer-shell"/);
});
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run: `npm test -- --testNamePattern="layout hooks"`, working directory `D:\langchain-agent\front`

Expected: FAIL，提示缺少 `app-shell` 或 `composer-shell`

- [ ] **Step 3: 重写 `index.html` 页面骨架并修复中文文案**

将 `front/index.html` 调整为如下结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>智扫通机器人智能客服</title>
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar-top">
          <button id="new-chat" class="sidebar-primary" type="button">新对话</button>
          <button id="clear-history" class="sidebar-secondary" type="button">清空会话</button>
        </div>

        <section class="sidebar-section">
          <p class="sidebar-label">快捷提问</p>
          <div class="sidebar-prompts">
            <button class="prompt-chip" type="button">扫地机器人怎么保养？</button>
            <button class="prompt-chip" type="button">给我生成本月使用报告</button>
            <button class="prompt-chip" type="button">机器人总是卡住怎么办？</button>
          </div>
        </section>

        <footer class="sidebar-footer">
          <p class="brand-name">智扫通客服</p>
          <p class="brand-status">已连接智能客服服务</p>
        </footer>
      </aside>

      <main class="chat-main">
        <header class="chat-topbar">
          <p class="topbar-title">智扫通机器人智能客服</p>
          <p class="topbar-subtitle">随时咨询保养、故障排查和使用报告</p>
        </header>

        <section id="message-scroll" class="message-scroll">
          <section id="empty-state" class="empty-state">
            <h1>今天想了解你的扫地机器人什么问题？</h1>
            <p>你可以直接提问，也可以使用左侧快捷问题开始。</p>
            <div class="empty-actions">
              <button class="prompt-chip" type="button">扫地机器人怎么保养？</button>
              <button class="prompt-chip" type="button">生成我的本月使用报告</button>
              <button class="prompt-chip" type="button">拖地功能效果不好怎么办？</button>
            </div>
          </section>
          <section id="message-list" class="message-list" aria-live="polite"></section>
        </section>

        <form id="chat-form" class="composer-shell">
          <label class="sr-only" for="message-input">输入问题</label>
          <div class="composer-form">
            <textarea
              id="message-input"
              name="message"
              rows="1"
              maxlength="2000"
              placeholder="询问机器人使用、保养、故障和报告..."
              required
            ></textarea>
            <button id="send-button" class="send-button" type="submit">发送</button>
          </div>
          <p id="status-text" class="status-text">等待提问</p>
        </form>
      </main>
    </div>

    <template id="message-template">
      <article class="message">
        <div class="message-avatar"></div>
        <div class="message-body">
          <div class="message-meta"></div>
          <div class="message-bubble"></div>
        </div>
      </article>
    </template>

    <script type="module" src="/static/app.js"></script>
  </body>
</html>
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `npm test -- --testNamePattern="layout hooks"`, working directory `D:\langchain-agent\front`

Expected: PASS，输出 1 passed

- [ ] **Step 5: 提交这一小步**

```bash
git add front/index.html front/tests/app.test.js
git commit -m "feat(front): add chatgpt-like page shell"
```

## Task 3: 实现新对话、清空会话和快捷提问交互

**Files:**
- Modify: `front/static/app.js`
- Test: `front/tests/app.test.js`

- [ ] **Step 1: 写失败测试，覆盖快捷提问填充与清空会话行为**

在 `front/tests/app.test.js` 追加：

```js
test("prompt chips fill the input and clear actions reset the welcome state", async () => {
  const dom = buildDom();
  global.window = dom.window;
  global.document = dom.window.document;
  global.sessionStorage = dom.window.sessionStorage;

  const { initChatApp } = await import("../static/app.js?scenario=prompt");
  const app = initChatApp();

  const firstChip = document.querySelector(".prompt-chip");
  firstChip.click();
  assert.equal(document.querySelector("#message-input").value, "扫地机器人怎么保养？");

  app.state.messages.push({ role: "user", content: "测试消息" });
  app.renderMessages();
  assert.equal(document.querySelector("#empty-state").hidden, true);

  document.querySelector("#clear-history").click();
  assert.deepEqual(app.state.messages, []);
  assert.equal(document.querySelector("#empty-state").hidden, false);
  assert.equal(document.querySelector("#status-text").textContent, "会话已清空");
});
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run: `npm test -- --testNamePattern="clear actions"`, working directory `D:\langchain-agent\front`

Expected: FAIL，提示未绑定点击事件、`renderMessages` 未暴露或状态文本不匹配

- [ ] **Step 3: 在 `app.js` 中补齐交互绑定和可复用渲染函数**

将 `front/static/app.js` 的核心逻辑扩展为：

```js
function saveMessages(storage, messages) {
  storage.setItem(STORAGE_KEY, JSON.stringify(messages));
}

function autoResize(input) {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 220)}px`;
}

export function initChatApp(root = document) {
  const elements = {
    form: root.querySelector("#chat-form"),
    input: root.querySelector("#message-input"),
    sendButton: root.querySelector("#send-button"),
    statusText: root.querySelector("#status-text"),
    messageList: root.querySelector("#message-list"),
    emptyState: root.querySelector("#empty-state"),
    template: root.querySelector("#message-template"),
    clearHistory: root.querySelector("#clear-history"),
    newChat: root.querySelector("#new-chat"),
    promptChips: root.querySelectorAll(".prompt-chip"),
  };

  const storage = window.sessionStorage;
  const state = {
    messages: loadMessages(storage),
    isSending: false,
  };

  function setStatus(text, isError = false) {
    elements.statusText.textContent = text;
    elements.statusText.classList.toggle("has-error", isError);
  }

  function renderMessages() {
    elements.messageList.innerHTML = "";
    elements.emptyState.hidden = state.messages.length > 0;
  }

  function resetConversation(statusText) {
    state.messages = [];
    saveMessages(storage, state.messages);
    renderMessages();
    setStatus(statusText);
    elements.input.focus();
  }

  elements.promptChips.forEach((button) => {
    button.addEventListener("click", () => {
      elements.input.value = button.textContent.trim();
      autoResize(elements.input);
      elements.input.focus();
    });
  });

  elements.clearHistory.addEventListener("click", () => {
    resetConversation("会话已清空");
  });

  elements.newChat.addEventListener("click", () => {
    resetConversation("已开始新对话");
  });

  renderMessages();
  setStatus("等待提问");
  autoResize(elements.input);

  return { elements, state, renderMessages, setStatus };
}
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `npm test -- --testNamePattern="clear actions"`, working directory `D:\langchain-agent\front`

Expected: PASS，输出 1 passed

- [ ] **Step 5: 提交这一小步**

```bash
git add front/static/app.js front/tests/app.test.js
git commit -m "feat(front): add sidebar interactions"
```

## Task 4: 适配新消息结构并保留流式回复体验

**Files:**
- Modify: `front/static/app.js`
- Test: `front/tests/app.test.js`

- [ ] **Step 1: 写失败测试，覆盖消息渲染与助手占位更新**

在 `front/tests/app.test.js` 追加：

```js
test("renderMessages and updateLastAssistantBubble follow the new message layout", async () => {
  const dom = buildDom();
  global.window = dom.window;
  global.document = dom.window.document;
  global.sessionStorage = dom.window.sessionStorage;

  const { initChatApp } = await import("../static/app.js?scenario=render");
  const app = initChatApp();

  app.state.messages = [
    { role: "user", content: "你好" },
    { role: "assistant", content: "" },
  ];
  app.renderMessages();

  assert.equal(document.querySelectorAll(".message").length, 2);
  assert.equal(document.querySelector('[data-role="user"] .message-meta').textContent, "你");
  assert.equal(document.querySelector('[data-role="assistant"] .message-meta').textContent, "智扫通助手");
  assert.equal(document.querySelector('[data-role="assistant"] .message-bubble').textContent, "思考中...");

  app.updateLastAssistantBubble("这是流式回复");
  assert.equal(document.querySelector('[data-role="assistant"] .message-bubble').textContent, "这是流式回复");
});
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run: `npm test -- --testNamePattern="new message layout"`, working directory `D:\langchain-agent\front`

Expected: FAIL，提示 `updateLastAssistantBubble` 未导出或消息标签文本不匹配

- [ ] **Step 3: 实现消息模板适配、状态切换与流式更新辅助函数**

在 `front/static/app.js` 中实现以下核心函数：

```js
function createMessageNode(template, message) {
  const fragment = template.content.cloneNode(true);
  const article = fragment.querySelector(".message");
  const avatar = fragment.querySelector(".message-avatar");
  const meta = fragment.querySelector(".message-meta");
  const bubble = fragment.querySelector(".message-bubble");

  article.dataset.role = message.role;
  avatar.textContent = message.role === "user" ? "你" : "智";
  meta.textContent = message.role === "user" ? "你" : "智扫通助手";
  bubble.textContent = message.content || (message.role === "assistant" ? "思考中..." : "");
  return fragment;
}

function setSendingState(root, elements, isSending) {
  root.body?.classList.toggle("is-loading", isSending);
  elements.input.disabled = isSending;
  elements.sendButton.disabled = isSending;
}

export function initChatApp(root = document) {
  // 保留前文 elements、state、setStatus、renderMessages 等逻辑

  function renderMessages() {
    elements.messageList.innerHTML = "";
    state.messages.forEach((message) => {
      elements.messageList.appendChild(createMessageNode(elements.template, message));
    });
    elements.emptyState.hidden = state.messages.length > 0;
  }

  function updateLastAssistantBubble(content) {
    const items = elements.messageList.querySelectorAll(".message");
    const last = items[items.length - 1];
    if (!last || last.dataset.role !== "assistant") {
      return;
    }
    const bubble = last.querySelector(".message-bubble");
    if (bubble) {
      bubble.textContent = content || "思考中...";
    }
  }

  function appendMessage(message) {
    elements.messageList.appendChild(createMessageNode(elements.template, message));
    elements.emptyState.hidden = true;
  }

  return {
    elements,
    state,
    renderMessages,
    updateLastAssistantBubble,
    appendMessage,
    setStatus,
    setSendingState,
  };
}
```

随后把现有 `handleSubmit`、`streamChatResponse`、`enqueueAssistantText`、`flushTyping` 等逻辑接回这个新结构，保留以下行为：

- 用户提交后先追加用户消息和空助手消息
- 状态文案依次显示“智扫通助手思考中...”与“回复完成”
- 错误时在最后一条助手消息中显示中文错误提示
- 流式回复结束后写回 `sessionStorage`

- [ ] **Step 4: 运行测试并确认通过**

Run: `npm test -- --testNamePattern="new message layout"`, working directory `D:\langchain-agent\front`

Expected: PASS，输出 1 passed

- [ ] **Step 5: 提交这一小步**

```bash
git add front/static/app.js front/tests/app.test.js
git commit -m "feat(front): adapt chat rendering for new layout"
```

## Task 5: 重写深色样式并为响应式布局提供最小覆盖

**Files:**
- Modify: `front/static/styles.css`
- Test: `front/tests/app.test.js`

- [ ] **Step 1: 写失败测试，约束深色主题和响应式关键选择器**

在 `front/tests/app.test.js` 追加：

```js
test("styles.css includes dark shell tokens and responsive layout hooks", async () => {
  const fs = await import("node:fs");
  const path = await import("node:path");
  const { fileURLToPath } = await import("node:url");
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const css = fs.readFileSync(path.join(currentDir, "..", "static", "styles.css"), "utf8");

  assert.match(css, /--app-bg:/);
  assert.match(css, /--sidebar-bg:/);
  assert.match(css, /\.app-shell/);
  assert.match(css, /\.sidebar/);
  assert.match(css, /\.chat-main/);
  assert.match(css, /\.composer-shell/);
  assert.match(css, /@media \(max-width: 900px\)/);
});
```

- [ ] **Step 2: 运行测试并确认按预期失败**

Run: `npm test -- --testNamePattern="dark shell tokens"`, working directory `D:\langchain-agent\front`

Expected: FAIL，提示缺少 `--app-bg` 或 `.composer-shell`

- [ ] **Step 3: 重写 `styles.css` 为深色 ChatGPT 风格布局**

将 `front/static/styles.css` 调整为如下方向：

```css
:root {
  --app-bg: #212121;
  --sidebar-bg: #171717;
  --panel-bg: #212121;
  --panel-border: #2f2f2f;
  --text-main: #ececec;
  --text-muted: #a3a3a3;
  --assistant-bg: #212121;
  --user-bg: #303030;
  --accent: #ffffff;
  --accent-strong: #d4d4d4;
  --chip-bg: #2a2a2a;
  --danger: #ff7b72;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--text-main);
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
}

.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
  padding: 16px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--panel-border);
}

.chat-main {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  background: var(--panel-bg);
}

.message-scroll {
  overflow-y: auto;
  padding: 24px 0 120px;
}

.message-list,
.empty-state {
  width: min(860px, calc(100% - 32px));
  margin: 0 auto;
}

.composer-shell {
  position: sticky;
  bottom: 0;
  padding: 16px 24px 24px;
  background: linear-gradient(to top, rgba(33, 33, 33, 0.98), rgba(33, 33, 33, 0.82));
}

.composer-form {
  width: min(860px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--panel-border);
  border-radius: 28px;
  background: #2b2b2b;
}

.message[data-role="assistant"] .message-bubble {
  background: transparent;
}

.message[data-role="user"] .message-bubble {
  background: var(--user-bg);
  border-radius: 24px;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid var(--panel-border);
  }

  .composer-form {
    grid-template-columns: 1fr;
  }
}
```

要求保留以下视觉结果：

- 桌面端左深右浅的双栏结构
- 主聊天区消息宽度受控
- 输入区固定在底部视觉区域
- 移动端布局不挤压输入区

- [ ] **Step 4: 运行测试并确认通过**

Run: `npm test -- --testNamePattern="dark shell tokens"`, working directory `D:\langchain-agent\front`

Expected: PASS，输出 1 passed

- [ ] **Step 5: 提交这一小步**

```bash
git add front/static/styles.css front/tests/app.test.js
git commit -m "feat(front): restyle chat ui to dark workspace"
```

## Task 6: 端到端验证聊天流、清空逻辑和响应式结果

**Files:**
- Verify: `front/server.py`
- Verify: `front/index.html`
- Verify: `front/static/app.js`
- Verify: `front/static/styles.css`

- [ ] **Step 1: 运行完整测试套件**

Run: `npm test`, working directory `D:\langchain-agent\front`

Expected: PASS，全部测试通过

- [ ] **Step 2: 启动本地前端服务**

Run: `python front/server.py`, working directory `D:\langchain-agent`

Expected: 输出 `Front server running at http://127.0.0.1:8000`

- [ ] **Step 3: 手工验证桌面端流程**

在浏览器访问 `http://127.0.0.1:8000` 并确认：

- 空页面显示深色欢迎态
- 左侧栏展示“新对话”“清空会话”和快捷问题
- 点击快捷问题后输入框自动填充文本
- 发送消息后用户消息右对齐显示
- 助手回复以流式方式逐步展示
- 点击“清空会话”后恢复欢迎态

- [ ] **Step 4: 手工验证窄屏布局**

将浏览器宽度缩小到约 390px 并确认：

- 侧栏折叠为顶部块状区域
- 输入区仍可完整显示
- 消息区不会被底部输入区遮挡

- [ ] **Step 5: 提交验证完成的最终改动**

```bash
git add front/index.html front/static/app.js front/static/styles.css front/package.json front/tests/app.test.js
git commit -m "feat(front): redesign chat page to match chatgpt layout"
```

## Self-Review

### Spec Coverage Check

- 深色 ChatGPT 风格布局：Task 2 + Task 5
- 左侧栏包含新对话、清空会话、推荐问题和状态信息：Task 2 + Task 3
- 欢迎态与建议问题卡片：Task 2 + Task 3
- 输入区贴底与连续聊天体验：Task 2 + Task 5
- 保留 SSE 流式回复：Task 4
- 修复中文乱码：Task 2
- 移动端适配：Task 5 + Task 6

没有遗漏的 spec 条目。

### Placeholder Scan

- 无 `TODO`、`TBD`、`implement later`
- 每个任务都有明确文件路径、测试命令和预期结果
- 每个代码步骤都给出具体代码骨架

### Type Consistency Check

- 初始化入口统一为 `initChatApp`
- 状态字段统一为 `state.messages`、`state.isSending`
- 欢迎态节点统一为 `#empty-state`
- 输入节点统一为 `#message-input`
- 发送按钮统一为 `#send-button`

命名保持一致，可直接进入执行。
