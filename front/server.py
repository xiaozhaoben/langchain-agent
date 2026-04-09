from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from agent.react_agent import ReactAgent

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_ROOT = STATIC_DIR.resolve()

agent = ReactAgent()


class FrontHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            self._serve_file(BASE_DIR / "index.html")
            return

        if path == "/api/health":
            self._send_json({"status": "ok"})
            return

        if path.startswith("/static/"):
            file_path = (STATIC_DIR / path.removeprefix("/static/")).resolve()
            if STATIC_ROOT not in file_path.parents and file_path != STATIC_ROOT:
                self._send_json({"detail": "资源不存在"}, status=HTTPStatus.NOT_FOUND)
                return
            self._serve_file(file_path)
            return

        self._send_json({"detail": "资源不存在"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/chat":
            self._send_json({"detail": "资源不存在"}, status=HTTPStatus.NOT_FOUND)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"detail": "请求体不是有效的 JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        message = str(payload.get("message", "")).strip()
        if not message:
            self._send_json({"detail": "消息不能为空"}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        try:
            for chunk in agent.execute_stream(message):
                if chunk:
                    self._write_sse(chunk)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as exc:
            error_message = f"\n抱歉，处理请求时发生异常：{exc}\n"
            self._write_sse(error_message)
        finally:
            try:
                self._write_sse("", event="done")
                self._finish_chunks()
            except (BrokenPipeError, ConnectionResetError):
                return

    def log_message(self, format: str, *args) -> None:
        return

    def _serve_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"detail": "资源不存在"}, status=HTTPStatus.NOT_FOUND)
            return

        content_type, _ = mimetypes.guess_type(file_path.name)
        content_type = content_type or "application/octet-stream"
        file_bytes = file_path.read_bytes()

        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type = f"{content_type}; charset=utf-8"

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)

    def _send_json(self, payload: dict[str, str], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_chunk(self, data: bytes) -> None:
        if not data:
            return

        self.wfile.write(f"{len(data):X}\r\n".encode("ascii"))
        self.wfile.write(data)
        self.wfile.write(b"\r\n")
        self.wfile.flush()

    def _write_sse(self, data: str, event: str | None = None) -> None:
        if data is None:
            return

        payload_lines = data.splitlines() or [""]
        sse_lines: list[str] = []

        if event:
            sse_lines.append(f"event: {event}")

        for line in payload_lines:
            sse_lines.append(f"data: {line}")

        sse_lines.append("")
        payload = "\n".join(sse_lines).encode("utf-8")
        self._write_chunk(payload)

    def _finish_chunks(self) -> None:
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), FrontHandler)
    print(f"Front server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
