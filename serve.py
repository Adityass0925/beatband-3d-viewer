"""BeatBand V1 3D viewer - local server.

Serves this folder at http://localhost:8765/ (this computer only) and opens
it in the default browser once the server is ready.

  serve.py              start the server (opens the browser)
  serve.py --no-browser start without opening the browser
  serve.py --status     exit code 0 if the viewer is running, 1 if not
  serve.py --stop       stop a running viewer
"""
import functools
import http.server
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))
URL = f"http://localhost:{PORT}/"
TOKEN_FILE = os.path.join(ROOT, ".stop-token")
LOG_FILE = os.path.join(ROOT, "server.log")
STOP_PATH = "/__stop_viewer"

# pythonw has no console: send output to a log file instead of nowhere.
if sys.stdout is None or sys.stderr is None:
    _log = open(LOG_FILE, "a", buffering=1, encoding="utf-8")
    sys.stdout = sys.stdout or _log
    sys.stderr = sys.stderr or _log


class Handler(http.server.SimpleHTTPRequestHandler):
    # Force correct types: some Windows setups map .js to text/plain,
    # which makes the browser refuse to run the 3D code.
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".html": "text/html",
        ".json": "application/json",
        ".png": "image/png",
        ".glb": "model/gltf-binary",
    }
    stop_token = ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == STOP_PATH:
            token = urllib.parse.parse_qs(parsed.query).get("token", [""])[0]
            ok = bool(self.stop_token) and secrets.compare_digest(token, self.stop_token)
            self.send_response(200 if ok else 403)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"stopping" if ok else b"forbidden")
            if ok:
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if parsed.path.startswith("/.") or parsed.path.endswith((".py", ".log")):
            self.send_error(404)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass  # keep quiet


def is_running() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=2) as r:
            return b"BeatBand" in r.read(4096)
    except Exception:
        return False


def stop() -> int:
    if not is_running():
        print("  The viewer was not running.")
        return 0
    try:
        with open(TOKEN_FILE, encoding="utf-8") as f:
            token = f.read().strip()
        q = urllib.parse.urlencode({"token": token})
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}{STOP_PATH}?{q}", timeout=3).read()
        print("  The viewer has been stopped.")
        return 0
    except Exception as e:
        print(f"  Could not stop the viewer: {e}")
        return 1


def serve(open_browser: bool) -> int:
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        print(f"ERROR: index.html not found in {ROOT}")
        return 1

    token = secrets.token_hex(16)
    handler_cls = type("BoundHandler", (Handler,), {"stop_token": token})
    handler = functools.partial(handler_cls, directory=ROOT)
    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    except OSError:
        if is_running():
            if open_browser:
                webbrowser.open(URL)
            return 0
        print(f"ERROR: port {PORT} is being used by another program.")
        return 1

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    print(f"Viewer running at {URL}")

    if open_browser:
        threading.Timer(0.3, lambda: webbrowser.open(URL)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        try:
            os.remove(TOKEN_FILE)
        except OSError:
            pass
    print("Viewer stopped")
    return 0


def main() -> int:
    args = set(sys.argv[1:])
    if "--status" in args:
        return 0 if is_running() else 1
    if "--stop" in args:
        return stop()
    return serve(open_browser="--no-browser" not in args)


if __name__ == "__main__":
    sys.exit(main())
