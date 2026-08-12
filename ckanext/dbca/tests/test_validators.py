import pytest

import ckanext.dbca.logic.validators as validators


def set_resource_upload_limits(monkeypatch):
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.sysadmin_resource_upload_limit",
        "150",
    )
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.org_admin_resource_upload_limit",
        "35",
    )
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.org_editor_resource_upload_limit",
        "35",
    )


def set_distinct_resource_upload_limits(monkeypatch):
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.sysadmin_resource_upload_limit",
        "150",
    )
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.org_admin_resource_upload_limit",
        "100",
    )
    monkeypatch.setitem(
        validators.tk.config,
        "ckanext.dbca.org_editor_resource_upload_limit",
        "35",
    )


def test_dbca_validate_geojson_accepts_polygon():
    polygon = (
        '{"type": "Polygon", "coordinates": '
        '[[[115.8, -31.9], [115.9, -31.9], [115.9, -32.0], [115.8, -31.9]]]}'
    )

    assert validators.dbca_validate_geojson(polygon) == polygon


def test_dbca_validate_geojson_rejects_non_json():
    with pytest.raises(validators.tk.Invalid, match="Not a valid JSON string"):
        validators.dbca_validate_geojson("not-json")


def test_dbca_validate_geojson_rejects_non_polygon_geometry():
    point = '{"type": "Point", "coordinates": [115.8, -31.9]}'

    with pytest.raises(validators.tk.Invalid, match="GeoJSON Polygon is needed"):
        validators.dbca_validate_geojson(point)


def test_dbca_resource_size_enforces_sysadmin_limit(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 149 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: True)

    assert validators.dbca_resource_size(key, data, {}, {"user": "sysadmin"}) is None

    data[key] = 150 * 1000 * 1000
    assert validators.dbca_resource_size(key, data, {}, {"user": "sysadmin"}) is None

    data[key] = 151 * 1000 * 1000
    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "sysadmin"})


def test_dbca_resource_size_enforces_org_admin_limit(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 34 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: "admin",
    )

    assert validators.dbca_resource_size(key, data, {}, {"user": "admin"}) is None

    data[key] = 35 * 1000 * 1000
    assert validators.dbca_resource_size(key, data, {}, {"user": "admin"}) is None

    data[key] = 36 * 1000 * 1000
    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "admin"})


def test_dbca_resource_size_uses_parent_org_admin_limit(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 35 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "child-department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.tk.h,
        "group_tree_parents",
        lambda org_id: [
            {"id": "root-department"},
            {"id": "parent-department"},
        ],
        raising=False,
    )
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: "admin" if org_id == "parent-department" else None,
    )

    assert validators.dbca_resource_size(key, data, {}, {"user": "admin"}) is None

    data[key] = 36 * 1000 * 1000
    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "admin"})


def test_dbca_resource_size_enforces_org_editor_limit(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 34 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: "editor",
    )

    assert validators.dbca_resource_size(key, data, {}, {"user": "editor"}) is None

    data[key] = 35 * 1000 * 1000
    assert validators.dbca_resource_size(key, data, {}, {"user": "editor"}) is None

    data[key] = 36 * 1000 * 1000
    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "editor"})


def test_dbca_resource_size_uses_parent_org_editor_limit(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 35 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "child-department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.tk.h,
        "group_tree_parents",
        lambda org_id: [
            {"id": "root-department"},
            {"id": "parent-department"},
        ],
        raising=False,
    )
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: "editor" if org_id == "parent-department" else None,
    )

    assert validators.dbca_resource_size(key, data, {}, {"user": "editor"}) is None

    data[key] = 36 * 1000 * 1000
    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "editor"})


def test_dbca_resource_size_uses_nearest_parent_org_role(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 36 * 1000 * 1000,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "org-a-2-2",
    }
    roles = {
        "org-a": "admin",
        "org-a-2": "editor",
    }

    set_distinct_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.tk.h,
        "group_tree_parents",
        lambda org_id: [
            {"id": "org-a"},
            {"id": "org-a-2"},
        ],
        raising=False,
    )
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: roles.get(org_id),
    )

    with pytest.raises(validators.tk.Invalid, match="File upload too large"):
        validators.dbca_resource_size(key, data, {}, {"user": "user"})

    del roles["org-a-2"]

    assert validators.dbca_resource_size(key, data, {}, {"user": "user"}) is None


def test_dbca_resource_size_rejects_user_without_direct_or_parent_org_role(monkeypatch):
    key = ("resources", 0, "size")
    data = {
        key: 1,
        ("resources", 0, "url_type"): "upload",
        ("owner_org",): "department",
    }

    set_resource_upload_limits(monkeypatch)
    monkeypatch.setattr(validators.authz, "is_sysadmin", lambda user: False)
    monkeypatch.setattr(
        validators.tk.h,
        "group_tree_parents",
        lambda org_id: [
            {"id": "root-department"},
            {"id": "parent-department"},
        ],
        raising=False,
    )
    monkeypatch.setattr(
        validators.authz,
        "users_role_for_group_or_org",
        lambda org_id, user: None,
    )

    with pytest.raises(
        validators.tk.Invalid,
        match="Upload size limit could not be determined",
    ):
        validators.dbca_resource_size(key, data, {}, {"user": "viewer"})
