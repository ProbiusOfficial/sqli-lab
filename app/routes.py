from __future__ import annotations

import inspect
import os
from typing import Any

from flask import Blueprint, jsonify, render_template, request

from app.challenges.levels import FilterError
from app.challenges.registry import get_challenge, iter_challenges
from app.config import Config
from app.context import InjectionContext
from app.db import apply_dynamic_flags_from_env, reset_database_from_init_sql

bp = Blueprint("main", __name__)


def _sanitize_mode(mode: str) -> str:
    return "god" if mode == "god" else "practice"


def _payload() -> dict[str, Any]:
    if request.is_json and request.get_json(silent=True):
        return dict(request.get_json(silent=True) or {})
    return dict(request.form or {})


def _preview_ctx() -> InjectionContext:
    q = request.args
    headers = {}
    ua = q.get("ua", "")
    ref = q.get("referer", "")
    if ua:
        headers["user-agent"] = ua
    if ref:
        headers["referer"] = ref
    return InjectionContext(
        level=str(q.get("level", "0")),
        mode=_sanitize_mode(str(q.get("mode", "practice"))),
        get={"id": str(q.get("id", "1"))},
        post={"uname": str(q.get("uname", "")), "passwd": str(q.get("passwd", ""))},
        cookie={"uname": str(q.get("cookie_uname", "guest"))},
        headers=headers,
    )


def _try_build_sql(ctx: InjectionContext) -> tuple[str | None, str | None]:
    ch = get_challenge(ctx.level)
    try:
        return ch.build_sql(ctx), None
    except FilterError as e:
        return None, str(e)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/levels")
def api_levels():
    data = [{"id": c.level_id, "title": c.title} for c in iter_challenges()]
    return jsonify({"levels": data})


@bp.get("/api/sql-preview")
def api_sql_preview():
    ctx = _preview_ctx()
    sql, err = _try_build_sql(ctx)
    if err:
        return jsonify({"ok": False, "error": err, "sql_preview": None})
    return jsonify({"ok": True, "sql_preview": sql})


@bp.post("/api/query")
def api_query():
    body = _payload()
    ctx = InjectionContext.from_payload(body)
    ctx.mode = _sanitize_mode(ctx.mode)
    ch = get_challenge(ctx.level)

    try:
        result = ch.run(ctx)
    except FilterError as e:
        if ctx.mode != "god":
            return jsonify({"ok": True, "echo_html": f"<p class='bad'>WAF：{e}</p>"})
        return jsonify(
            {
                "ok": True,
                "echo_html": f"<p class='bad'>WAF：{e}</p>",
                "executed_sql": None,
                "elapsed_ms": None,
                "rowcount": None,
                "mysql": None,
                "source_class": type(ch).__name__,
            }
        )

    if ctx.mode != "god":
        return jsonify(
            {
                "ok": True,
                "echo_html": result.get("echo_html"),
            }
        )

    return jsonify(
        {
            "ok": True,
            "echo_html": result.get("echo_html"),
            "executed_sql": result.get("executed_sql"),
            "elapsed_ms": result.get("elapsed_ms"),
            "rowcount": result.get("rowcount"),
            "mysql": result.get("mysql"),
            "source_class": type(ch).__name__,
        }
    )


@bp.get("/api/god/source")
def api_god_source():
    level = str(request.args.get("level", "0"))
    ch = get_challenge(level)
    cls = type(ch)
    try:
        text = inspect.getsource(cls)
    except (TypeError, OSError) as e:
        return jsonify({"ok": False, "error": f"无法提取源码：{e}"}), 500
    mod = getattr(cls, "__module__", "")
    name = getattr(cls, "__name__", "Challenge")
    return jsonify(
        {
            "ok": True,
            "path": f"{mod}.{name}",
            "source": text,
        }
    )


@bp.post("/api/admin/reset")
def api_admin_reset():
    token = request.headers.get("X-Reset-Token", "")
    if not Config.RESET_TOKEN:
        return jsonify({"ok": False, "error": "RESET_TOKEN 未配置，拒绝重置"}), 403
    if token != Config.RESET_TOKEN:
        return jsonify({"ok": False, "error": "令牌错误"}), 403
    try:
        reset_database_from_init_sql()
        apply_dynamic_flags_from_env()
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify({"ok": True, "message": "已重新导入 /docker-init/01_init.sql 并刷新 Flag"})


@bp.get("/healthz")
def healthz():
    return jsonify({"ok": True})
