const STORAGE_KEY = "langchain-agent-front-history";

const elements = {
  form: document.querySelector("#chat-form"),
  input: document.querySelector("#message-input"),
  sendButton: document.querySelector("#send-button"),
  statusText: document.querySelector("#status-text"),
  messageList: document.querySelector("#message-list"),
  emptyState: document.querySelector("#empty-state"),
  template: document.querySelector("#message-template"),
  clearHistory: document.querySelector("#clear-history"),
  promptChips: document.querySelectorAll(".prompt-chip"),
};

const state = {
  messages: loadMessages(),
  isSending: false,
};

const typingState = {
  queue: "",
  timer: null,
  speed: 32, // chars per tick
};

function loadMessages() {
  try {
    const cached = sessionStorage.getItem(STORAGE_KEY);
    return cached ? JSON.parse(cached) : [];
  } catch (error) {
    return [];
  }
}

function saveMessages() {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state.messages));
}

function autoResize() {
  elements.input.style.height = "auto";
  elements.input.style.height = `${Math.min(elements.input.scrollHeight, 180)}px`;
}

function setStatus(text, isError = false) {
  elements.statusText.textContent = text;
  elements.statusText.classList.toggle("has-error", isError);
}

function scrollToBottom() {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: "smooth",
  });
}

function renderMessages() {
  elements.messageList.innerHTML = "";

  state.messages.forEach((message) => {
    const node = createMessageNode(message);
    elements.messageList.appendChild(node);
  });

  const hasMessages = state.messages.length > 0;
  elements.emptyState.hidden = hasMessages;
  scrollToBottom();
}

function createMessageNode(message) {
  const fragment = elements.template.content.cloneNode(true);
  const article = fragment.querySelector(".message");
  const meta = fragment.querySelector(".message-meta");
  const bubble = fragment.querySelector(".message-bubble");

  article.dataset.role = message.role;
  meta.textContent = message.role === "user" ? "你" : "智能客服";
  bubble.textContent = message.content || (message.role === "assistant" ? "思考中..." : "");
  return fragment;
}

function appendMessage(message) {
  const fragment = createMessageNode(message);
  elements.messageList.appendChild(fragment);
  elements.emptyState.hidden = true;
  scrollToBottom();
}

function updateLastAssistantBubble(content) {
  const items = elements.messageList.querySelectorAll(".message");
  if (!items.length) {
    return;
  }
  const last = items[items.length - 1];
  if (last.dataset.role !== "assistant") {
    return;
  }
  const bubble = last.querySelector(".message-bubble");
  if (bubble) {
    bubble.textContent = content || "思考中...";
  }
}

function enqueueAssistantText(text) {
  if (!text) {
    return;
  }
  typingState.queue += text;
  if (!typingState.timer) {
    typingState.timer = setInterval(tickTyping, 18);
  }
}

function tickTyping() {
  if (!typingState.queue) {
    stopTyping();
    return;
  }
  const slice = typingState.queue.slice(0, typingState.speed);
  typingState.queue = typingState.queue.slice(typingState.speed);
  const lastAssistant = state.messages[state.messages.length - 1];
  if (!lastAssistant || lastAssistant.role !== "assistant") {
    stopTyping();
    return;
  }
  lastAssistant.content += slice;
  saveMessages();
  updateLastAssistantBubble(lastAssistant.content);
  scrollToBottom();
}

function stopTyping() {
  if (typingState.timer) {
    clearInterval(typingState.timer);
    typingState.timer = null;
  }
}

function flushTyping() {
  if (!typingState.queue) {
    stopTyping();
    return;
  }
  const lastAssistant = state.messages[state.messages.length - 1];
  if (lastAssistant && lastAssistant.role === "assistant") {
    lastAssistant.content += typingState.queue;
    typingState.queue = "";
    saveMessages();
    updateLastAssistantBubble(lastAssistant.content);
  }
  stopTyping();
}

function setSending(isSending) {
  state.isSending = isSending;
  document.body.classList.toggle("is-loading", isSending);
  elements.input.disabled = isSending;
  elements.sendButton.disabled = isSending;
}

async function streamChatResponse(prompt) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: prompt }),
  });

  if (!response.ok) {
    let detail = "请求失败，请稍后重试";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (error) {
      detail = await response.text();
    }
    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error("浏览器不支持流式响应");
  }

  return response;
}

async function handleSubmit(prompt) {
  if (!prompt || state.isSending) {
    return;
  }

  const userMessage = { role: "user", content: prompt };
  const assistantMessage = { role: "assistant", content: "" };

  state.messages.push(userMessage, assistantMessage);
  saveMessages();
  appendMessage(userMessage);
  appendMessage(assistantMessage);
  typingState.queue = "";
  stopTyping();
  setSending(true);
  setStatus("智能客服思考中...");

  try {
    const response = await streamChatResponse(prompt);
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    const isSse = (response.headers.get("Content-Type") || "").includes("text/event-stream");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      const chunkText = decoder.decode(value, { stream: true });
      if (!isSse) {
        enqueueAssistantText(chunkText);
        continue;
      }

      buffer += chunkText;
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const eventBlock of events) {
        const lines = eventBlock.split("\n");
        let eventName = "";
        const dataLines = [];

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventName = line.slice(6).trim();
            continue;
          }
          if (line.startsWith("data:")) {
            dataLines.push(line.slice(5).trimStart());
          }
        }

        if (eventName === "done") {
          continue;
        }

        if (dataLines.length) {
          enqueueAssistantText(dataLines.join("\n"));
        }
      }
    }

    flushTyping();
    assistantMessage.content = assistantMessage.content.trim();
    saveMessages();
    updateLastAssistantBubble(assistantMessage.content);
    setStatus("回复完成");
  } catch (error) {
    flushTyping();
    assistantMessage.content =
      error instanceof Error ? `抱歉，当前请求失败：${error.message}` : "抱歉，当前请求失败。";
    saveMessages();
    renderMessages();
    setStatus("请求失败", true);
  } finally {
    setSending(false);
    elements.input.focus();
  }
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = elements.input.value.trim();

  if (!prompt) {
    setStatus("请输入问题后再发送", true);
    return;
  }

  elements.input.value = "";
  autoResize();
  await handleSubmit(prompt);
});

elements.input.addEventListener("input", autoResize);
elements.input.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.form.requestSubmit();
  }
});

elements.clearHistory.addEventListener("click", () => {
  state.messages = [];
  saveMessages();
  renderMessages();
  setStatus("会话已清空");
  elements.input.focus();
});

elements.promptChips.forEach((button) => {
  button.addEventListener("click", () => {
    elements.input.value = button.textContent.trim();
    autoResize();
    elements.input.focus();
  });
});

renderMessages();
autoResize();
elements.input.focus();
