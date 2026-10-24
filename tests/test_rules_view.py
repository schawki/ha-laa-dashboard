from custom_components.laa_dashboard import rules, view

P = rules.new_profile("kid", "Child", rooms_mode="selected", rooms=["chambre"], domains_mode="selected", domains=["light", "media_player"])
E = [
    {"entity_id": "light.a", "name": "Lamp", "domain": "light", "area_id": "chambre"},
    {"entity_id": "light.b", "name": "Salon lamp", "domain": "light", "area_id": "salon"},
    {"entity_id": "camera.c", "name": "Cam", "domain": "camera", "area_id": "chambre"},
    {"entity_id": "switch.d", "name": "Plug", "domain": "switch", "area_id": "chambre"},
    {"entity_id": "light.e", "name": "Loose", "domain": "light", "area_id": None},
]


def vis(p, i):
    e = E[i]
    return rules.entity_visible(p, e["entity_id"], e["domain"], e["area_id"])


def test_room_domain_and_default_camera_deny():
    assert [vis(P, i) for i in range(5)] == [True, False, False, False, False]


def test_deny_beats_allow_and_allow_beats_room_and_domain():
    p = rules.new_profile("x", "X", rooms_mode="selected", rooms=["chambre"], allow_entities=["light.b", "camera.c"], deny_entities=["camera.c"])
    assert vis(p, 1) is True          # allowed explicitly despite room
    assert vis(p, 2) is False         # denied explicitly
    p2 = rules.new_profile("y", "Y", allow_entities=["camera.c"])
    assert vis(p2, 2) is True         # allow overrides the camera default


def test_no_room_selectable():
    p = rules.new_profile("z", "Z", rooms_mode="selected", rooms=[rules.NO_ROOM])
    assert [vis(p, i) for i in (0, 4)] == [False, True]


def test_profile_for_user():
    a, b = rules.new_profile("a", "A", user_ids=["u1"]), rules.new_profile("b", "B")
    assert rules.profile_for_user([a, b], "b", "u1")["id"] == "a"
    assert rules.profile_for_user([a, b], "b", "u2")["id"] == "b"
    assert rules.profile_for_user([a, b], None, "u2") is None


def test_normalize_cleans():
    p = rules.normalize({"id": 1, "name": "  ", "rooms_mode": "weird", "rooms": ["b", "a", "a", ""], "bogus": 1})
    assert p["name"] == "1" and p["rooms_mode"] == "all" and p["rooms"] == ["a", "b"] and "bogus" not in p


FL = [{"id": "up", "name": "Upstairs", "level": 1}, {"id": "gf", "name": "Ground", "level": 0}]
AR = [{"id": "chambre", "name": "Chambre", "floor_id": "up"}, {"id": "salon", "name": "Salon", "floor_id": "gf"}, {"id": "cave", "name": "Cave", "floor_id": None}]


def test_view_admin_sees_all_ordered_by_level():
    v = view.build(FL, AR, E, None)
    assert [f["name"] for f in v["floors"]] == ["Ground", "Upstairs"]
    assert list(v["floors"][1]["rooms"][0]["entities"]) == ["camera", "light", "switch"]
    assert list(v["other"]) == ["light"]


def test_view_profile_filters_and_drops_empty():
    v = view.build(FL, AR, E, P)
    assert [f["name"] for f in v["floors"]] == ["Upstairs"]
    assert v["floors"][0]["rooms"][0]["entities"] == {"light": [{"entity_id": "light.a", "name": "Lamp"}]}
    assert v["other"] == {}


def test_area_without_floor_goes_last():
    v = view.build(FL, AR, [{"entity_id": "light.k", "name": "K", "domain": "light", "area_id": "cave"}], None)
    assert v["floors"][0]["name"] is None
