from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import os
import pymysql


class MySQLClient:
    def __init__(self) -> None:
        host = os.getenv("MYSQL_HOST")
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        if not all([host, user, password, database]):
            raise RuntimeError("Config MySQL incompleta: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")
        use_ssl = os.getenv("MYSQL_SSL", "false").lower() == "true"
        ssl_ca = os.getenv("MYSQL_SSL_CA")  # ruta a CA si aplica
        ssl_params = {"ca": ssl_ca} if use_ssl and ssl_ca else None
        self._conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor,
            read_timeout=5,
            write_timeout=5,
            connect_timeout=5,
            ssl=ssl_params,
        )

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Solo SELECT permitidos en modo read-only")
        with self._conn.cursor() as cur:
            cur.execute(sql, params or [])
            rows = cur.fetchall() or []
        return rows

    def introspect_schema(
        self,
        include_tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        schema = os.getenv("MYSQL_DATABASE")
        tables: Dict[str, Any] = {}
        inc = set([t.strip() for t in (include_tables or []) if t and t.strip()])
        exc = set([t.strip() for t in (exclude_tables or []) if t and t.strip()])
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s ORDER BY TABLE_NAME",
                [schema],
            )
            all_tables = [r["TABLE_NAME"] for r in cur.fetchall()]
            for t in all_tables:
                if inc and t not in inc:
                    continue
                if t in exc:
                    continue
                # Columnas
                cur.execute(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
                    ORDER BY ORDINAL_POSITION
                    """,
                    [schema, t],
                )
                cols = [
                    {
                        "name": r["COLUMN_NAME"],
                        "type": r["DATA_TYPE"],
                        "nullable": (r["IS_NULLABLE"] == "YES"),
                    }
                    for r in cur.fetchall()
                ]
                # PK
                cur.execute(
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND CONSTRAINT_NAME='PRIMARY'
                    ORDER BY ORDINAL_POSITION
                    """,
                    [schema, t],
                )
                pk = [r["COLUMN_NAME"] for r in cur.fetchall()]
                # FKs
                cur.execute(
                    """
                    SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL
                    """,
                    [schema, t],
                )
                fks = [
                    {
                        "column": r["COLUMN_NAME"],
                        "ref_table": r["REFERENCED_TABLE_NAME"],
                        "ref_column": r["REFERENCED_COLUMN_NAME"],
                    }
                    for r in cur.fetchall()
                ]
                tables[t] = {"columns": cols, "primary_key": pk, "foreign_keys": fks}
        return {"schema": schema, "tables": tables}

    @staticmethod
    def format_schema_for_prompt(introspected: Dict[str, Any], max_tables: int = 30, max_cols: int = 30) -> str:
        tables = introspected.get("tables", {})
        lines: List[str] = []
        for idx, (t, meta) in enumerate(tables.items()):
            if idx >= max_tables:
                break
            cols = meta.get("columns", [])[:max_cols]
            col_str = ", ".join([f"{c['name']} {c['type']}{'?' if c.get('nullable') else ''}" for c in cols])
            pk = meta.get("primary_key", [])
            pk_str = f" PK({', '.join(pk)})" if pk else ""
            lines.append(f"{t}({col_str}){pk_str}")
        return "; ".join(lines)


