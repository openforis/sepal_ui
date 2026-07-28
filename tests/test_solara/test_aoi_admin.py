"""Tests for AOI admin processing."""

import asyncio

from pysepal.solara.components.aoi import admin


class _FakeFeature:
    def propertyNames(self):
        return ["iso3_code", "gaul0_name"]

    def toDictionary(self, _properties):
        return {"iso3_code": "COL", "gaul0_name": "Colombia"}


class _FakeFeatureCollection:
    def first(self):
        return _FakeFeature()


class _FakeAsyncInterface:
    def __init__(self):
        self.closed = False
        self.calls = []
        self.async_calls = []
        self.blocking_call_saw_running_loop = None

    def get_info(self, payload):
        try:
            asyncio.get_running_loop()
            self.blocking_call_saw_running_loop = True
        except RuntimeError:
            self.blocking_call_saw_running_loop = False
        self.calls.append(payload)
        return payload

    async def get_info_async(self, payload):
        self.async_calls.append(payload)
        self.calls.append(payload)
        return payload

    def close(self):
        self.closed = True


def test_process_admin_closes_created_interface(monkeypatch):
    """Verify that a GEE interface created internally is closed after use."""
    created = []

    def make_interface(*args, **kwargs):
        interface = _FakeAsyncInterface()
        created.append(interface)
        return interface

    monkeypatch.setattr(admin.su, "init_ee", lambda: None)
    monkeypatch.setattr(admin.pygaul, "Items", lambda admin=None: _FakeFeatureCollection())
    monkeypatch.setattr(admin, "GEEInterface", make_interface)

    result = asyncio.run(admin.process_admin("ADMIN0", "62", gee=True))

    assert result.admin == "62"
    assert created[0].closed is True
    assert created[0].calls == [{"iso3_code": "COL", "gaul0_name": "Colombia"}]


def test_process_admin_keeps_provided_interface_open(monkeypatch):
    """Verify that an externally provided GEE interface is not closed."""
    interface = _FakeAsyncInterface()

    monkeypatch.setattr(admin.su, "init_ee", lambda: None)
    monkeypatch.setattr(admin.pygaul, "Items", lambda admin=None: _FakeFeatureCollection())

    result = asyncio.run(admin.process_admin("ADMIN0", "62", gee=True, gee_interface=interface))

    assert result.admin == "62"
    assert interface.closed is False
    assert interface.calls == [{"iso3_code": "COL", "gaul0_name": "Colombia"}]


def test_process_admin_keeps_gee_traffic_off_caller_loop(monkeypatch):
    """process_admin must use the blocking GEE API from a worker thread.

    eeclient caches one httpx.AsyncClient per session; its pooled HTTP/2
    connection binds to the first event loop that drives it. Awaiting
    get_info_async here runs that traffic on the Solara kernel loop, and any
    later call routed through GEEInterface's private loop (e.g. add_ee_layer
    -> get_map_id) then fails with "bound to a different event loop".
    """
    interface = _FakeAsyncInterface()

    monkeypatch.setattr(admin.su, "init_ee", lambda: None)
    monkeypatch.setattr(admin.pygaul, "Items", lambda admin=None: _FakeFeatureCollection())

    asyncio.run(admin.process_admin("ADMIN0", "62", gee=True, gee_interface=interface))

    assert interface.async_calls == []
    assert interface.blocking_call_saw_running_loop is False
