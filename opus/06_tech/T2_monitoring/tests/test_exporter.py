#!/usr/bin/env python3
import json
import os
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exporter"))

import node_health_exporter as nhe  # noqa: E402

HEAD_TS = int(time.time()) - 6
PUBKEY = "0x" + "ab" * 48


class MockEL(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        results = {
            "eth_syncing": False,
            "net_peerCount": "0x32",
            "eth_getBlockByNumber": {"number": hex(1_234_567), "timestamp": hex(HEAD_TS)},
        }
        body = json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": results[req["method"]]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


class MockCL(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        path = self.path
        if path == "/eth/v1/node/health":
            self.send_response(206)
            self.end_headers()
            return
        if path == "/eth/v1/node/syncing":
            payload = {"data": {"head_slot": "4286304", "sync_distance": "3", "is_syncing": True,
                                "is_optimistic": False, "el_offline": False}}
        elif path == "/eth/v1/node/peer_count":
            payload = {"data": {"disconnected": "1", "connecting": "0", "connected": "75", "disconnecting": "0"}}
        elif path.startswith("/eth/v1/beacon/states/head/validators"):
            payload = {"data": [{"index": "42", "balance": "32001234567", "status": "active_ongoing",
                                 "validator": {"pubkey": PUBKEY, "slashed": False}}]}
        else:
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


def serve(handler):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class ExporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.el = serve(MockEL)
        cls.cl = serve(MockCL)

    @classmethod
    def tearDownClass(cls):
        for srv in (cls.el, cls.cl):
            srv.shutdown()
            srv.server_close()

    def make_collector(self, el_port=None, cl_port=None, ids="42"):
        os.environ["EL_RPC_URL"] = f"http://127.0.0.1:{el_port or self.el.server_address[1]}"
        os.environ["CL_API_URL"] = f"http://127.0.0.1:{cl_port or self.cl.server_address[1]}"
        os.environ["VALIDATOR_IDS"] = ids
        os.environ["REQUEST_TIMEOUT"] = "2"
        return nhe.Collector(nhe.Config())

    def test_healthy_node_metrics(self):
        text = self.make_collector().collect()
        self.assertIn("eth_el_up 1", text)
        self.assertIn("eth_el_syncing 0", text)
        self.assertIn("eth_el_peers 50", text)
        self.assertIn("eth_el_head_block 1234567", text)
        self.assertIn("eth_cl_head_slot 4286304", text)
        self.assertIn('eth_validator_balance_gwei{index="42",pubkey="0xababababab"} 32001234567', text)
        self.assertIn("eth_cl_up 1", text)
        self.assertIn("eth_cl_health_status_code 206", text)
        self.assertIn("eth_cl_syncing 1", text)
        self.assertIn("eth_cl_sync_distance 3", text)
        self.assertIn("eth_cl_peers 75", text)
        self.assertIn('eth_validator_active{index="42",pubkey="0xababababab"} 1', text)
        self.assertIn('status="active_ongoing"', text)
        self.assertIn("eth_validators_found 1", text)

    def test_head_age_is_reasonable(self):
        text = self.make_collector().collect()
        line = next(l for l in text.splitlines() if l.startswith("eth_el_head_age_seconds "))
        self.assertLess(float(line.split()[1]), 120)

    def test_unreachable_endpoints_report_down(self):
        text = self.make_collector(el_port=1, cl_port=1).collect()
        self.assertIn("eth_el_up 0", text)
        self.assertIn("eth_cl_up 0", text)
        self.assertIn('node_health_exporter_errors_total{target="el"} 1', text)
        self.assertIn("eth_validators_query_up 0", text)

    def test_no_validators_configured(self):
        text = self.make_collector(ids="").collect()
        self.assertNotIn("eth_validator_active", text)

    def test_http_server_serves_metrics(self):
        state = nhe.State()
        state.set("eth_el_up 1\n")
        srv = ThreadingHTTPServer(("127.0.0.1", 0), nhe.make_handler(state))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/metrics", timeout=2) as r:
            self.assertEqual(r.read().decode(), "eth_el_up 1\n")
        srv.shutdown()
        srv.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
