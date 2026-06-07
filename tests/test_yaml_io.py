"""YAML I/O tests — Phase 1 Unit 5."""

from __future__ import annotations

import pytest

from research_scaffold_harness.contracts.yaml_io import (
    dump_yaml,
    load_model_yaml,
    load_yaml,
    model_to_yaml_dict,
    write_model_yaml,
    yaml_to_string,
)
from research_scaffold_harness.models.ca import ScaffoldConfigInfo

_HASH = "sha256:" + "a" * 64


def _config_payload() -> dict:
    return {
        "version": "0.1.0",
        "prompt_template_id": "tpl-001",
        "prompt_template_hash": _HASH,
        "config_hash": _HASH,
    }


def test_yaml_to_string_deterministic() -> None:
    data = {"b_key": 1, "a_key": 2, "nested": {"x": [1, 2, 3]}}
    result = yaml_to_string(data)
    assert "b_key" in result
    assert "!!" not in result  # no Python object tags
    assert result.startswith("b_key:")  # sort_keys=False preserves insertion order


def test_yaml_to_string_indent() -> None:
    data = {"parent": {"child": "value"}}
    result = yaml_to_string(data)
    assert "  child: value" in result


def test_dump_and_load_round_trip(tmp_path) -> None:
    data = {"key": "value", "number": 42, "nested": {"a": [1, 2]}}
    path = tmp_path / "test.yaml"
    dump_yaml(data, path)
    loaded = load_yaml(path)
    assert loaded == data


def test_dump_yaml_creates_parent_dirs(tmp_path) -> None:
    path = tmp_path / "deep" / "nested" / "dir" / "file.yaml"
    dump_yaml({"x": 1}, path)
    assert path.exists()
    assert load_yaml(path) == {"x": 1}


def test_load_yaml_rejects_non_mapping(tmp_path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected YAML mapping"):
        load_yaml(path)


def test_write_model_yaml_and_load_model_yaml_round_trip(tmp_path) -> None:
    model = ScaffoldConfigInfo.model_validate(_config_payload())
    path = tmp_path / "config.yaml"
    write_model_yaml(model, path)
    loaded = load_model_yaml(ScaffoldConfigInfo, path)
    assert loaded == model


def test_model_to_yaml_dict_produces_json_safe_primitives() -> None:
    model = ScaffoldConfigInfo.model_validate(_config_payload())
    data = model_to_yaml_dict(model)
    assert isinstance(data, dict)
    assert all(isinstance(v, str) for v in data.values())


def test_exclude_none_omits_none_fields(tmp_path) -> None:
    from research_scaffold_harness.models.ca import ScaffoldTaskInfo

    model = ScaffoldTaskInfo.model_validate({
        "research_question": "Does X cause Y?",
        "domain": "pharmacology",
        "expert_checkable": True,
        "ground_truth_ref": None,
    })
    data_with = model_to_yaml_dict(model, exclude_none=False)
    data_without = model_to_yaml_dict(model, exclude_none=True)
    assert "ground_truth_ref" in data_with
    assert "ground_truth_ref" not in data_without


def test_write_model_yaml_exclude_none(tmp_path) -> None:
    from research_scaffold_harness.models.ca import ScaffoldTaskInfo

    model = ScaffoldTaskInfo.model_validate({
        "research_question": "Does X cause Y?",
        "domain": "pharmacology",
        "expert_checkable": True,
        "ground_truth_ref": None,
    })
    path = tmp_path / "task.yaml"
    write_model_yaml(model, path, exclude_none=True)
    raw = path.read_text(encoding="utf-8")
    assert "ground_truth_ref" not in raw
