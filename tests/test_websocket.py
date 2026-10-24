import pytest
from homeassistant.auth.const import GROUP_ID_USER
from homeassistant.helpers import area_registry as ar, entity_registry as er, floor_registry as fr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.laa_dashboard.const import DOMAIN


@pytest.fixture
async def setup(hass, hass_admin_user, hass_read_only_user):
    from unittest.mock import patch
    from homeassistant.setup import async_setup_component
    assert await async_setup_component(hass, "http", {})
    assert await async_setup_component(hass, "websocket_api", {})
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    with patch("homeassistant.components.frontend.add_extra_js_url"), patch("homeassistant.components.panel_custom.async_register_panel"):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    floor = fr.async_get(hass).async_create("Ground", level=0)
    area = ar.async_get(hass).async_create("Salon", floor_id=floor.floor_id)
    reg = er.async_get(hass)
    for eid in ("light.lamp", "camera.door"):
        e = reg.async_get_or_create(eid.split(".")[0], "test", eid, suggested_object_id=eid.split(".")[1])
        reg.async_update_entity(e.entity_id, area_id=area.id)
        hass.states.async_set(e.entity_id, "on")
    return entry


async def call(client, **msg):
    client._n = getattr(client, "_n", 0) + 1
    await client.send_json({"id": client._n, **msg})
    r = await client.receive_json()
    return r


async def test_admin_sees_everything_and_saves(hass, hass_ws_client, setup, hass_admin_user):
    c = await hass_ws_client(hass)
    r = await call(c, type="laa_dashboard/view")
    assert r["result"]["profile"] is None
    assert set(r["result"]["floors"][0]["rooms"][0]["entities"]) == {"light", "camera"}
    r = await call(c, type="laa_dashboard/save_config", profiles=[{"id": "p", "name": "Kid", "user_ids": ["u"]}], default_profile_id="p", redirect_non_admins=True)
    assert r["result"]["default_profile_id"] == "p" and r["result"]["profiles"][0]["deny_domains"] == []
    r = await call(c, type="laa_dashboard/view", as_profile="p")
    assert r["result"]["profile"]["id"] == "p"


async def test_non_admin_is_filtered_and_cannot_admin(hass, hass_ws_client, setup, hass_read_only_user):
    admin = await hass_ws_client(hass)
    from custom_components.laa_dashboard import rules
    p = rules.new_profile("p", "Kid", user_ids=[hass_read_only_user.id])
    await call(admin, type="laa_dashboard/save_config", profiles=[p], redirect_non_admins=True)
    token = await hass.auth.async_create_refresh_token(hass_read_only_user, "http://example.com")
    access = hass.auth.async_create_access_token(token)
    user_client = await hass_ws_client(hass, access)
    r = await call(user_client, type="laa_dashboard/view")
    assert list(r["result"]["floors"][0]["rooms"][0]["entities"]) == ["light"]          # camera hidden by default
    assert (await call(user_client, type="laa_dashboard/view", as_profile="p"))["success"] is False
    assert (await call(user_client, type="laa_dashboard/get_config"))["success"] is False
    assert (await call(user_client, type="laa_dashboard/me"))["result"]["redirect"] is True


async def test_non_admin_without_profile_sees_nothing(hass, hass_ws_client, setup, hass_read_only_user):
    token = await hass.auth.async_create_refresh_token(hass_read_only_user, "http://example.com")
    client = await hass_ws_client(hass, hass.auth.async_create_access_token(token))
    r = await call(client, type="laa_dashboard/view")
    assert r["result"] == {"profile": None, "floors": [], "other": {}}
