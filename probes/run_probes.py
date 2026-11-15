#!/usr/bin/env python3
"""嵌套结构路径统计验收探针。

契约：
  from boltons.report import flatten_paths
  res = flatten_paths({"a": {"b": 1}, "c": [1, 2]})
  res.paths    叶子路径列表，形如 "a.b"、"c[0]"
  res.max_depth 最大嵌套层数（顶层为 1）
  res.leaves   叶子数量
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
FAIL = 0


def probe(code, desc, fn):
    global FAIL
    try:
        fn()
        print(f"[PASS] {code} {desc}")
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {code} {desc}\n        {type(exc).__name__}: {exc}")
        FAIL += 1


def main():
    try:
        from boltons.report import flatten_paths  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] P0 导入 boltons.report 失败：{type(exc).__name__}: {exc}")
        print("-" * 60)
        print("探针汇总：0/4 通过")
        return 1

    OBJ = {"a": {"b": 1}, "c": [1, 2]}

    def p1():
        res = flatten_paths(OBJ)
        assert "a.b" in res.paths, res.paths

    def p2():
        res = flatten_paths(OBJ)
        assert "c[0]" in res.paths and "c[1]" in res.paths, res.paths

    def p3():
        res = flatten_paths(OBJ)
        assert res.max_depth == 3, res.max_depth

    def p4():
        res = flatten_paths(OBJ)
        assert res.leaves == 3, res.leaves

    probe("P1", "字典键路径", p1)
    probe("P2", "列表下标路径", p2)
    probe("P3", "最大深度", p3)
    probe("P4", "叶子计数", p4)

    print("-" * 60)
    print(f"探针汇总：{4 - FAIL}/4 通过")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
