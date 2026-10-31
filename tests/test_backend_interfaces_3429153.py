"""Current OpenLinkHub acknowledgement and Nexus schema regressions."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import openlinkhub_integration as olh
from modules.openlinkhub_nexus.v1_0.designs import _buttons, install_nexus_design
from modules.openlinkhub_update.v1_0.policy import UpdatePlan
from PIL import Image


class Response:
    status = 200

    def __init__(self, value):
        self.data = json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, limit):
        return self.data[:limit]


def test_api_write_requires_explicit_ack_but_read_catalog_does_not():
    for value in ({"code": 200, "status": 0, "message": "Rejected"},
                  {"status": True}, {}, []):
        with patch.object(olh, "urlopen", return_value=Response(value)):
            with pytest.raises(RuntimeError):
                olh._api_request(olh.DEFAULT_API_URL, "/api/color", method="POST", payload={})
    catalogue = {"code": 200, "status": 0, "data": {"Silent": {}}}
    with patch.object(olh, "urlopen", return_value=Response(catalogue)):
        assert olh._api_get(olh.DEFAULT_API_URL, "/api/temperatures") == catalogue
    with patch.object(olh, "urlopen", return_value=Response({"code": 200, "status": 1})):
        assert olh._api_request(olh.DEFAULT_API_URL, "/api/color", method="POST", payload={})["status"] == 1


def test_local_api_never_uses_proxy_redirect_or_http_fallback(monkeypatch):
    from urllib.error import HTTPError
    from urllib.request import Request
    monkeypatch.setenv("http_proxy", "http://192.0.2.5:8080")
    monkeypatch.setenv("HTTP_PROXY", "http://192.0.2.5:8080")
    assert olh._API_PROXY.proxies == {}
    handler = next(item for item in olh._API_OPENER.handlers if isinstance(item, olh._NoApiRedirect))
    request = Request(olh.DEFAULT_API_URL + "/api/color", data=b"private", method="POST")
    for destination in ("http://192.0.2.5:8080/", olh.DEFAULT_API_URL + "/api/other",
                        "https://127.0.0.1:27003/api/color"):
        with pytest.raises(HTTPError):
            handler.redirect_request(request, None, 302, "Found", {}, destination)
    with patch.object(olh._API_OPENER, "open", side_effect=HTTPError(request.full_url, 302, "Found", {}, None)) as opened:
        with pytest.raises(HTTPError):
            olh._api_request(olh.DEFAULT_API_URL, "/api/color", method="POST", payload={"color": "test"})
        assert opened.call_count == 1
        sent = opened.call_args.args[0]
        assert sent.full_url == olh.DEFAULT_API_URL + "/api/color" and sent.method == "POST"


def test_user_space_version_is_recognized_without_rpm():
    plan = UpdatePlan("user-space", "0.9.2", (), True, "local")
    with patch("modules.openlinkhub_update.v1_0.policy.update_plan", return_value=plan):
        with patch.object(olh, "_run") as run:
            assert olh.installed_version() == "0.9.2"
            run.assert_not_called()


def test_nexus_lowercase_inclusive_touch_bounds_and_legacy_import():
    button = {"actionCode": 1, "width": 100, "height": 40,
              "touchPositionMin": 0, "touchPositionMax": 99}
    result = _buttons({"0": button})["0"]
    assert result["touchPositionMax"] == 99
    assert "TouchPositionMax" not in result
    with pytest.raises(ValueError, match="überschneiden"):
        _buttons({"0": button, "1": dict(button, touchPositionMin=99, touchPositionMax=120)})
    legacy = dict(button, touchPositionMin=200)
    del legacy["touchPositionMax"]
    legacy["TouchPositionMax"] = 640
    assert _buttons({"0": legacy})["0"]["touchPositionMax"] == 639


def test_nexus_rejects_database_directory_escape_and_preserves_backup(tmp_path):
    root = tmp_path / "OpenLinkHub"
    root.mkdir()
    (root / "OpenLinkHub").write_bytes(b"binary")
    outside = tmp_path / "outside"
    (outside / "nexus").mkdir(parents=True)
    database = outside / "nexus/nexus.json"
    database.write_text('{"profiles": {}}')
    (root / "database").symlink_to(outside, target_is_directory=True)
    source = tmp_path / "bg.png"
    Image.new("RGB", (640, 48)).save(source)
    with pytest.raises(ValueError, match="Benutzerinstallation"):
        install_nexus_design(source, root, home=tmp_path)
    assert database.read_text() == '{"profiles": {}}'
