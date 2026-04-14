from __future__ import annotations

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

import pymysql
from pymysql.cursors import DictCursor

from app.config import Config


def _connect(**kwargs: Any) -> pymysql.connections.Connection:
    # 默认 utf8mb4；关卡可传入 charset（如宽字节关 GBK）覆盖，避免与固定参数重复传入
    params: dict[str, Any] = {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "password": Config.MYSQL_PASSWORD,
        "database": Config.MYSQL_DATABASE,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True,
    }
    params.update(kwargs)
    return pymysql.connect(**params)


@contextmanager
def get_conn(**kwargs: Any) -> Generator[pymysql.connections.Connection, None, None]:
    conn = _connect(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


def apply_dynamic_flags_from_env() -> None:
    """将 FLAG / STATIC 写回各关 flag_store（容器内与 entrypoint 一致）。"""
    if os.environ.get("DASFLAG"):
        val = os.environ["DASFLAG"]
    elif os.environ.get("FLAG"):
        val = os.environ["FLAG"]
    elif os.environ.get("GZCTF_FLAG"):
        val = os.environ["GZCTF_FLAG"]
    else:
        val = os.environ.get("STATIC_FLAG", "HelloCTF{sql_injection_lab}")

    dbs = [
        "lv_0",
        "lv_1",
        "lv_2",
        "lv_3",
        "lv_4",
        "lv_5",
        "lv_6",
        "lv_7",
        "lv_8",
        "lv_9",
        "lv_10",
        "lv_11",
        "lv_12",
        "lv_13",
    ]
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_ADMIN_USER,
        password=Config.MYSQL_ADMIN_PASSWORD,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            for db in dbs:
                cur.execute(
                    f"UPDATE `{db}`.`flag_store` SET `flag`=%s WHERE `id`=1 LIMIT 1",
                    (val,),
                )
    finally:
        conn.close()


def reset_database_from_init_sql() -> None:
    """使用 root 重新执行 01_init.sql（单容器内，等同环境复原）。"""
    init_path = Path("/docker-init/01_init.sql")
    if not init_path.is_file():
        raise FileNotFoundError(str(init_path))
    env = os.environ.copy()
    env["MYSQL_PWD"] = Config.MYSQL_ROOT_PASSWORD
    with open(init_path, "rb") as stdin_f:
        subprocess.run(
            ["mysql", "-uroot", "-h", Config.MYSQL_HOST],
            env=env,
            stdin=stdin_f,
            check=True,
            capture_output=True,
        )
