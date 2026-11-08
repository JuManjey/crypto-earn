#!/usr/bin/env python3
"""Prometheus-экспортер состояния Ethereum-ноды (EL JSON-RPC + Beacon API).

Только чтение: экспортер не использует ключи, не подписывает и не отправляет
транзакции. Опрашивает эндпоинты в фоне и отдаёт последний снимок на /metrics.

Переменные окружения:
  EL_RPC_URL         JSON-RPC исполнительного клиента (по умолчанию http://127.0.0.1:8545)
  CL_API_URL         Beacon API консенсус-клиента (по умолчанию http://127.0.0.1:5052)
  VALIDATOR_IDS      индексы или pubkey валидаторов через запятую (необязательно, до 64)
  LISTEN_ADDR        адрес HTTP-сервера (по умолчанию 127.0.0.1)
  LISTEN_PORT        порт HTTP-сервера (по умолчанию 9101)
  POLL_INTERVAL      период опроса, секунд (по умолчанию 15)
  REQUEST_TIMEOUT    таймаут запроса, секунд (по умолчанию 5)
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_VALIDATORS = 64


def env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip() or default


class Config:
    def __init__(self) -> None:
        self.el_url = env("EL_RPC_URL", "http://127.0.0.1:8545")
        self.cl_url = env("CL_API_URL", "http://127.0.0.1:5052").rstrip("/")
        ids = [x.strip() for x in os.environ.get("VALIDATOR_IDS", "").split(",") if x.strip()]
        self.validator_ids = ids[:MAX_VALIDATORS]
        self.listen_addr = env("LISTEN_ADDR", "127.0.0.1")
        self.listen_port = int(env("LISTEN_PORT", "9101"))
        self.poll_interval = float(env("POLL_INTERVAL", "15"))
        self.timeout = float(env("REQUEST_TIMEOUT", "5"))


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def format_value(value: float) -> str:
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return repr(value)


class Metrics:
    def __init__(self) -> None:
        self.samples: list[tuple[str, dict[str, str], float]] = []
        self.meta: dict[str, tuple[str, str]] = {}

    def gauge(self, name: str, help_text: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.meta.setdefault(name, ("gauge", help_text))
        self.samples.append((name, labels or {}, float(value)))

    def counter(self, name: str, help_text: str, value: float, labels: dict[str, str] | None = None) -> None:
        self.meta.setdefault(name, ("counter", help_text))
        self.samples.append((name, labels or {}, float(value)))

    def render(self) -> str:
        lines: list[str] = []
        for name, (kind, help_text) in self.meta.items():
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} {kind}")
            for sname, labels, value in self.samples:
                if sname != name:
                    continue
                if labels:
                    lbl = ",".join(f'{k}="{escape_label(v)}"' for k, v in sorted(labels.items()))
                    lines.append(f"{name}{{{lbl}}} {format_value(value)}")
                else:
                    lines.append(f"{name} {format_value(value)}")
        return "\n".join(lines) + "\n"


class Collector:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.errors = {"el": 0, "cl": 0, "validators": 0}
        self._rpc_id = 0

    def _http(self, url: str, data: bytes | None = None) -> tuple[int, bytes]:
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.cfg.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()

    def rpc(self, method: str, params: list | None = None):
        self._rpc_id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._rpc_id, "method": method, "params": params or []})
        status, raw = self._http(self.cfg.el_url, body.encode())
        if status != 200:
            raise RuntimeError(f"{method}: HTTP {status}")
        payload = json.loads(raw)
        if "error" in payload:
            raise RuntimeError(f"{method}: {payload['error']}")
        return payload["result"]

    def beacon(self, path: str) -> tuple[int, dict]:
        status, raw = self._http(self.cfg.cl_url + path)
        try:
            return status, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return status, {}

    def collect_el(self, m: Metrics) -> None:
        try:
            syncing = self.rpc("eth_syncing")
            peers = int(self.rpc("net_peerCount"), 16)
            block = self.rpc("eth_getBlockByNumber", ["latest", False])
            number = int(block["number"], 16)
            age = max(0.0, time.time() - int(block["timestamp"], 16))
        except (OSError, RuntimeError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.errors["el"] += 1
            m.gauge("eth_el_up", "1, если JSON-RPC исполнительного клиента отвечает", 0)
            return
        m.gauge("eth_el_up", "1, если JSON-RPC исполнительного клиента отвечает", 1)
        m.gauge("eth_el_syncing", "1, если исполнительный клиент синхронизируется", 0 if syncing is False else 1)
        m.gauge("eth_el_peers", "число пиров исполнительного клиента", peers)
        m.gauge("eth_el_head_block", "номер последнего блока", number)
        m.gauge("eth_el_head_age_seconds", "возраст последнего блока, секунд", age)

    def collect_cl(self, m: Metrics) -> None:
        try:
            health_status, _ = self.beacon("/eth/v1/node/health")
            s_status, syncing = self.beacon("/eth/v1/node/syncing")
            p_status, peers = self.beacon("/eth/v1/node/peer_count")
            if s_status != 200 or p_status != 200:
                raise RuntimeError("beacon API вернул не 200")
            sd = syncing["data"]
            connected = int(peers["data"]["connected"])
        except (OSError, RuntimeError, ValueError, KeyError, TypeError):
            self.errors["cl"] += 1
            m.gauge("eth_cl_up", "1, если Beacon API отвечает", 0)
            return
        m.gauge("eth_cl_up", "1, если Beacon API отвечает", 1)
        m.gauge("eth_cl_health_status_code", "HTTP-код /eth/v1/node/health (200 готов, 206 синхронизация)",
                health_status)
        m.gauge("eth_cl_syncing", "1, если консенсус-клиент синхронизируется", 1 if sd.get("is_syncing") else 0)
        m.gauge("eth_cl_sync_distance", "отставание от головы цепи, слотов", int(sd.get("sync_distance", 0)))
        m.gauge("eth_cl_head_slot", "слот головы цепи", int(sd.get("head_slot", 0)))
        m.gauge("eth_cl_optimistic", "1, если голова цепи оптимистичная (EL не подтвердил)",
                1 if sd.get("is_optimistic") else 0)
        m.gauge("eth_cl_el_offline", "1, если консенсус-клиент не видит исполнительный клиент",
                1 if sd.get("el_offline") else 0)
        m.gauge("eth_cl_peers", "число подключённых пиров консенсус-клиента", connected)

    def collect_validators(self, m: Metrics) -> None:
        if not self.cfg.validator_ids:
            return
        ids = ",".join(self.cfg.validator_ids)
        try:
            status, body = self.beacon(f"/eth/v1/beacon/states/head/validators?id={ids}")
            if status != 200:
                raise RuntimeError(f"HTTP {status}")
            data = body["data"]
        except (OSError, RuntimeError, KeyError, TypeError):
            self.errors["validators"] += 1
            m.gauge("eth_validators_query_up", "1, если запрос статусов валидаторов успешен", 0)
            return
        m.gauge("eth_validators_query_up", "1, если запрос статусов валидаторов успешен", 1)
        m.gauge("eth_validators_found", "сколько из запрошенных валидаторов найдено в состоянии цепи", len(data))
        for v in data:
            pubkey = v["validator"]["pubkey"]
            labels = {"index": str(v["index"]), "pubkey": pubkey[:12]}
            st = v["status"]
            m.gauge("eth_validator_status", "текущий статус валидатора (значение 1 у метки status)", 1,
                    dict(labels, status=st))
            m.gauge("eth_validator_active", "1, если статус active_ongoing", 1 if st == "active_ongoing" else 0,
                    labels)
            m.gauge("eth_validator_balance_gwei", "баланс валидатора, gwei", int(v["balance"]), labels)
            m.gauge("eth_validator_slashed", "1, если валидатор был наказан слешингом",
                    1 if v["validator"].get("slashed") else 0, labels)

    def collect(self) -> str:
        start = time.time()
        m = Metrics()
        self.collect_el(m)
        self.collect_cl(m)
        self.collect_validators(m)
        m.gauge("node_health_exporter_last_poll_timestamp", "время последнего опроса (unix)", time.time())
        m.gauge("node_health_exporter_poll_duration_seconds", "длительность опроса, секунд", time.time() - start)
        for target, count in self.errors.items():
            m.counter("node_health_exporter_errors_total", "ошибки опроса по целям", count, {"target": target})
        return m.render()


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.text = "# первый опрос ещё не завершён\n"

    def set(self, text: str) -> None:
        with self.lock:
            self.text = text

    def get(self) -> str:
        with self.lock:
            return self.text


def poll_forever(collector: Collector, state: State, interval: float, stop: threading.Event) -> None:
    while not stop.is_set():
        state.set(collector.collect())
        stop.wait(interval)


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path.split("?")[0] == "/metrics":
                body = state.get().encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            elif self.path == "/healthz":
                body = b"ok\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
            else:
                body = b"not found\n"
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler


def main() -> None:
    cfg = Config()
    collector, state, stop = Collector(cfg), State(), threading.Event()
    threading.Thread(target=poll_forever, args=(collector, state, cfg.poll_interval, stop), daemon=True).start()
    server = ThreadingHTTPServer((cfg.listen_addr, cfg.listen_port), make_handler(state))
    print(f"node_health_exporter: http://{cfg.listen_addr}:{cfg.listen_port}/metrics "
          f"(EL {cfg.el_url}, CL {cfg.cl_url}, валидаторов {len(cfg.validator_ids)})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


if __name__ == "__main__":
    main()
