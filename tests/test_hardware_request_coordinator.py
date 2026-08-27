import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware_request_coordinator import KrakenUsbCoordinator, RequestPriority, RgbRequestCoordinator


def test_latest_request_wins_and_logs():
    logs=[]
    c=KrakenUsbCoordinator(logs.append)
    first=c.request('LCD','A',priority=RequestPriority.HIGH,replace_key='lcd-design')
    assert c.begin(first.request_id,'LCD-Streamer')
    second=c.request('LCD','B',priority=RequestPriority.HIGH,replace_key='lcd-design')
    assert not c.is_current(first.request_id)
    assert c.current(first.request_id).state == 'superseded'
    assert c.is_current(second.request_id)
    c.begin(second.request_id,'LCD-Streamer')
    c.complete(second.request_id,'ok')
    status=c.status()
    assert status['superseded'] == 1
    assert status['owner'] == 'idle'
    assert any('Request #' in line for line in logs)


def test_rgb_coordinator_domains_do_not_share_replace_key():
    c=RgbRequestCoordinator()
    a=c.request('RGB','effect',replace_key='rgb-effect')
    b=c.request('RGB','startup',replace_key='rgb-startup')
    assert c.is_current(a.request_id)
    assert c.is_current(b.request_id)
