
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

app = FastAPI(
    title="Clothing Store API",
    description="服飾商品資料庫 API",
    version="1.0.0"
)


@lru_cache
def get_engine():
    # 從環境變數讀取 TiDB Cloud 連線資料
    host = os.getenv("TIDB_HOST")
    port = int(os.getenv("TIDB_PORT", "4000"))
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE", "clothing_store")
    ca_path = os.getenv("TIDB_CA_PATH")

    if not all([host, user, password, ca_path]):
        raise RuntimeError("請設定完整的 TiDB Cloud 環境變數")

    if not Path(ca_path).is_file():
        raise RuntimeError("找不到 TiDB Cloud CA 憑證")

    db_url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

    return create_engine(
        db_url,
        connect_args={"ssl": {"ca": ca_path}},
        pool_pre_ping=True
    )


@app.get("/")
def home():
    return {
        "message": "Clothing Store API 正常運作",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/products")
def get_products(
    category_id: int | None = None,
    keyword: str | None = None,
    limit: int = Query(default=60, ge=1, le=100)
):
    sql = text("""
        SELECT
            p.product_id,
            p.product_name,
            b.brand_name,
            c.category_name,
            p.price,
            p.stock,
            p.description,
            p.image_url
        FROM products p
        LEFT JOIN brands b
            ON p.brand_id = b.brand_id
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        WHERE (:category_id IS NULL OR p.category_id = :category_id)
          AND (:keyword IS NULL OR p.product_name LIKE :keyword)
        ORDER BY p.product_id
        LIMIT :limit
    """)

    try:
        with get_engine().connect() as conn:
            result = conn.execute(
                sql,
                {
                    "category_id": category_id,
                    "keyword": keyword,
                    "limit": limit
                }
            )
            return [dict(row) for row in result.mappings().all()]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
def get_categories():
    try:
        with get_engine().connect() as conn:
            result = conn.execute(text("""
                SELECT category_id, category_name
                FROM categories
                ORDER BY category_id
            """))
            return [dict(row) for row in result.mappings().all()]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
