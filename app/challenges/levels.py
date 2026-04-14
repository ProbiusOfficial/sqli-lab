from __future__ import annotations

import html
import re
import time
from typing import Any

import pymysql

from app.context import InjectionContext
from app.db import get_conn


class FilterError(ValueError):
    pass


FLAG_HINT = (
    "Flag 在独立表 flag_store 中，默认业务查询不返回；"
    "需通过 UNION 等扩展结果集读取 flag_store.flag（注意列数与类型匹配）。"
)


def _collect_columns(rows: list[dict[str, Any]]) -> list[str]:
    cols: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                cols.append(k)
    return cols


def _rows_html(rows: list[dict[str, Any]] | None) -> str:
    if not rows:
        return "<p>（无查询结果）</p>"
    cols = _collect_columns(rows)
    thead_cells = "".join(f"<th>{html.escape(str(c), quote=True)}</th>" for c in cols)
    thead_row = f"<tr>{thead_cells}</tr>"
    body = ""
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c, "")
            text = "" if v is None else str(v)
            cells.append(f"<td>{html.escape(text, quote=False)}</td>")
        body += f"<tr>{''.join(cells)}</tr>"
    return f"<table class='res'><thead>{thead_row}</thead><tbody>{body}</tbody></table>"


def _strip_once_ci(s: str, needle: str) -> str:
    pattern = re.compile(re.escape(needle), re.IGNORECASE)
    return pattern.sub("", s, count=1)


USERS_SELECT = "`id`, `name`, `col2`, `col3`, `col4`"


class Challenge:
    """子类提供 level_id / title / schema / hints（hints 仅在源码中展示）。"""

    def source_path(self) -> str:
        return __file__

    def build_sql(self, ctx: InjectionContext) -> str:  # pragma: no cover
        raise NotImplementedError

    def run(self, ctx: InjectionContext) -> dict[str, Any]:
        sql = self.build_sql(ctx)
        t0 = time.perf_counter()
        err: dict[str, Any] | None = None
        rows: list[dict[str, Any]] | None = None
        rowcount = 0
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    rows = cur.fetchall()  # type: ignore[assignment]
                    rowcount = cur.rowcount
        except Exception as e:  # noqa: BLE001
            err = {"type": e.__class__.__name__, "message": str(e)}
            if isinstance(e, pymysql.err.OperationalError) and getattr(e, "args", None):
                err["errno"] = e.args[0]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        echo = self.render_echo(ctx, sql, rows, err)
        return {
            "echo_html": echo,
            "executed_sql": sql,
            "elapsed_ms": round(elapsed_ms, 3),
            "rowcount": rowcount,
            "mysql": err,
        }

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            return f"<p class='err'>数据库错误：{html.escape(str(err.get('message','')), quote=False)}</p>"
        return _rows_html(rows)


class L0(Challenge):
    level_id = "0"
    title = "数字型注入（GET id）"
    schema = "lv_0"
    hints = [
        FLAG_HINT,
        "本关 id 为数字拼接：WHERE id= 后无引号。",
        "可尝试 OR、注释、UNION 等（注意与字符型闭合差异）。",
    ]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = (ctx.get_param("id", "1") or "1").strip() or "1"
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id={raw} LIMIT 50"
        )


class L1(Challenge):
    level_id = "1"
    title = "单引号注入（GET id）"
    schema = "lv_1"
    hints = [
        FLAG_HINT,
        "尝试在 id 后闭合单引号，观察报错与语句形态。",
        "使用 ORDER BY 判断列数，再用 UNION 选择显位。",
        "注释符可使用 # 或 --+（注意空格）。",
    ]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id='{raw}' LIMIT 50"
        )


class L2(Challenge):
    level_id = "2"
    title = "双引号注入（GET id）"
    schema = "lv_2"
    hints = [FLAG_HINT, "本关使用双引号包裹参数。", "闭合方式从 ' 变为 \"。", "其余利用链与单引号类似。"]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id=\"{raw}\" LIMIT 50"
        )


class L3(Challenge):
    level_id = "3"
    title = "单括号注入（GET id）"
    schema = "lv_3"
    hints = [FLAG_HINT, "注意括号与引号共同闭合。", "常见形态：') 或 )) 等，结合注释截断后半段。"]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id=('{raw}') LIMIT 50"
        )


class L4(Challenge):
    level_id = "4"
    title = "双写绕过（GET id）"
    schema = "lv_4"
    hints = [FLAG_HINT, "部分关键字被“删除一次”。", "尝试双写关键字使其过滤后仍恢复为合法 SQL。"]

    def _filter(self, raw: str) -> str:
        for kw in ("union", "select", "from", "where", "and", "or"):
            raw = _strip_once_ci(raw, kw)
        return raw

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = self._filter(ctx.get_param("id", "1"))
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id='{raw}' LIMIT 50"
        )


class L5(Challenge):
    level_id = "5"
    title = "大小写绕过（GET id）"
    schema = "lv_5"
    hints = [
        FLAG_HINT,
        "本关禁止出现小写形式的 union/select/from/where/and/or。",
        "尝试使用大写或混合大小写关键字。",
    ]

    def _check(self, raw: str) -> None:
        banned = ("union", "select", "from", "where", "and", "or")
        for kw in banned:
            if kw in raw:
                raise FilterError(f"blocked lowercase token: {kw}")

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        self._check(raw)
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id='{raw}' LIMIT 50"
        )


class L6(Challenge):
    level_id = "6"
    title = "宽字节注入（GET id，GBK + addslashes）"
    schema = "lv_6"
    hints = [
        FLAG_HINT,
        "连接使用 GBK；服务端对输入做 addslashes 风格转义。",
        "思考 %df 与反斜杠如何吞掉转义，使单引号重新获得语法意义。",
        "默认回显我们使用Latin-1编码,所以无法展现效果，你可以尝试勾选展示原始数据，这样在 hex 里可以直接看到例如 df 5c 这类字节对，和「Latin-1 里仍显示成 ß + \」对照，更容易理解 GBK 线宽字节吃反斜杠的现象。"
        "可以使用cyberchef from hex（recipe=From_Hex('Auto')&oenc=936&ieol=CRLF&oeol=CRLF） 后显示为gbk编码；"
    ]

    @staticmethod
    def _addslashes_bytes(data: bytes) -> bytes:
        out = bytearray()
        for c in data:
            if c in (0x27, 0x22, 0x5C, 0):
                out.append(0x5C)
            out.append(c)
        return bytes(out)

    def _build_sql_bytes(self, ctx: InjectionContext) -> bytes:
        raw = ctx.get_param("id", "1")
        raw_b = raw.encode("latin-1", errors="replace")
        esc_b = self._addslashes_bytes(raw_b)
        prefix = (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` WHERE id='"
        ).encode("ascii")
        return prefix + esc_b + b"' LIMIT 50"

    def build_sql(self, ctx: InjectionContext) -> str:
        # 与下发字节一致的一一对应展示（便于上帝模式对照）
        return self._build_sql_bytes(ctx).decode("latin-1")

    def run(self, ctx: InjectionContext) -> dict[str, Any]:
        sql_b = self._build_sql_bytes(ctx)
        sql_display = sql_b.decode("latin-1")
        t0 = time.perf_counter()
        err: dict[str, Any] | None = None
        rows: list[dict[str, Any]] | None = None
        rowcount = 0
        try:
            with get_conn(charset="gbk", init_command="SET NAMES gbk") as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_b)
                    rows = cur.fetchall()  # type: ignore[assignment]
                    rowcount = cur.rowcount
        except Exception as e:  # noqa: BLE001
            err = {"type": e.__class__.__name__, "message": str(e)}
            if isinstance(e, pymysql.err.OperationalError) and getattr(e, "args", None):
                err["errno"] = e.args[0]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        echo = self.render_echo(ctx, sql_display, rows, err)
        return {
            "echo_html": echo,
            "executed_sql": sql_display,
            "elapsed_ms": round(elapsed_ms, 3),
            "rowcount": rowcount,
            "mysql": err,
        }


class L7(Challenge):
    level_id = "7"
    title = "报错注入（GET id，无显位）"
    schema = "lv_7"
    hints = [FLAG_HINT, "页面不返回 UNION 显位。", "可尝试 updatexml/extractvalue 等报错带出数据。"]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id=\"{raw}\" LIMIT 1"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            msg = str(err.get("message", ""))
            safe = html.escape(msg[:900], quote=False)
            return f"<p class='hint'>数据库返回了错误信息（节选）：</p><pre class='sql'>{safe}</pre>"
        if rows:
            return _rows_html(rows)
        return "<p>（无结果）</p>"


class L8(Challenge):
    level_id = "8"
    title = "布尔盲注（GET id）"
    schema = "lv_8"
    hints = [FLAG_HINT, "页面只区分“命中/未命中”两种状态。", "通过真假分支逐位猜解数据。"]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id='{raw}' LIMIT 5"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            return f"<p class='err'>语法/执行错误：{html.escape(str(err.get('message','')), quote=False)}</p>"
        if rows:
            return "<p class='ok'><b>You are in!!!</b>（查询返回了行）</p>"
        return "<p class='bad'><b>Missing the mark</b>（查询未返回行）</p>"


class L9(Challenge):
    level_id = "9"
    title = "时间盲注（GET id）"
    schema = "lv_9"
    hints = [
        FLAG_HINT,
        "结合 sleep/if 观察响应耗时。",
        "上帝模式会显示服务端计时，练习模式仅返回固定提示。",
    ]

    def build_sql(self, ctx: InjectionContext) -> str:
        raw = ctx.get_param("id", "1")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE id='{raw}' LIMIT 5"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            return f"<p class='err'>语法/执行错误：{html.escape(str(err.get('message','')), quote=False)}</p>"
        if ctx.mode == "god":
            return "<p>请求已处理（上帝模式请查看耗时）。</p>"
        return "<p>请求已处理。</p>"


class L10(Challenge):
    level_id = "10"
    title = "POST 登录框（uname / passwd）"
    schema = "lv_10"
    hints = [FLAG_HINT, "注入点位于 POST 的 uname（或 passwd）。", "抓包修改表单字段即可。"]

    USERS_LOGIN = "`id`, `username`, `password`, `col3`, `col4`"

    def build_sql(self, ctx: InjectionContext) -> str:
        u = ctx.post_param("uname", "")
        p = ctx.post_param("passwd", "")
        return (
            f"SELECT {self.USERS_LOGIN} FROM `{self.schema}`.`users` "
            f"WHERE username='{u}' AND password='{p}' LIMIT 5"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            return f"<p class='err'>数据库错误：{html.escape(str(err.get('message','')), quote=False)}</p>"
        if rows:
            return "<p class='ok'>登录成功（查询命中至少一行）。</p>" + _rows_html(rows)
        return "<p class='bad'>登录失败（查询无命中）。</p>"


class L11(Challenge):
    level_id = "11"
    title = "Cookie 注入（cookie: uname）"
    schema = "lv_11"
    hints = [FLAG_HINT, "注入点来自 Cookie 中的 uname。", "浏览器侧可用开发者工具或本页 Cookie 输入框模拟。"]

    def build_sql(self, ctx: InjectionContext) -> str:
        u = ctx.cookie_param("uname", "guest")
        return (
            f"SELECT {USERS_SELECT} FROM `{self.schema}`.`users` "
            f"WHERE name='{u}' LIMIT 50"
        )


class L12(Challenge):
    level_id = "12"
    title = "User-Agent 注入"
    schema = "lv_12"
    hints = [FLAG_HINT, "服务端把 User-Agent 拼进 SQL。", "无显位时可配合报错函数。"]

    UA_SELECT = "`id`, `ua`, `hit`"

    def build_sql(self, ctx: InjectionContext) -> str:
        ua = ctx.header("user-agent", "Mozilla/5.0")
        return (
            f"SELECT {self.UA_SELECT} FROM `{self.schema}`.`ua_logs` "
            f"WHERE ua='{ua}' LIMIT 10"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            msg = str(err.get("message", ""))
            safe = html.escape(msg[:900], quote=False)
            return f"<p class='hint'>数据库错误（可尝试报错注入）：</p><pre class='sql'>{safe}</pre>"
        return _rows_html(rows)


class L13(Challenge):
    level_id = "13"
    title = "Referer 注入"
    schema = "lv_13"
    hints = [FLAG_HINT, "注入点来自 Referer。", "闭合方式与 UA 题类似，注意引号配对。"]

    REF_SELECT = "`id`, `ref`, `hit`"

    def build_sql(self, ctx: InjectionContext) -> str:
        ref = ctx.header("referer", "http://127.0.0.1/")
        return (
            f"SELECT {self.REF_SELECT} FROM `{self.schema}`.`ref_logs` "
            f"WHERE ref='{ref}' LIMIT 10"
        )

    def render_echo(
        self,
        ctx: InjectionContext,
        sql: str,
        rows: list[dict[str, Any]] | None,
        err: dict[str, Any] | None,
    ) -> str:
        if err:
            msg = str(err.get("message", ""))
            safe = html.escape(msg[:900], quote=False)
            return f"<p class='hint'>数据库错误（可尝试报错注入）：</p><pre class='sql'>{safe}</pre>"
        return _rows_html(rows)


ALL_CHALLENGES: list[Challenge] = [
    L0(),
    L1(),
    L2(),
    L3(),
    L4(),
    L5(),
    L6(),
    L7(),
    L8(),
    L9(),
    L10(),
    L11(),
    L12(),
    L13(),
]
