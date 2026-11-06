
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


app = FastAPI(
    title="Clothing Store API",
    description="服飾商品資料庫 API",
    version="1.0.0"
)

# 允許 GitHub Pages 網站讀取 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yi-1228.github.io",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# TiDB Cloud 資料庫連線
@lru_cache()
def get_engine():
    host = os.getenv("TIDB_HOST")
    port = int(os.getenv("TIDB_PORT", "4000"))
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE", "clothing_store")
    ca_path = os.getenv("TIDB_CA_PATH")

    if not all([host, user, password, ca_path]):
        raise ValueError("資料庫連線環境變數設定不完整")

    if not Path(ca_path).is_file():
        raise ValueError("找不到 TiDB CA 憑證檔案")

    db_url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"charset": "utf8mb4"}
    )

    engine = create_engine(
        db_url,
        connect_args={
            "ssl": {
                "ca": ca_path
            }
        },
        pool_pre_ping=True
    )

    return engine


# 首頁
@app.get("/")
def home():
    return {
        "message": "Clothing Store API is running",
        "docs": "/docs"
    }


# 檢查資料庫連線
@app.get("/health")
def health():
    try:
        engine = get_engine()

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )


# 查詢商品
@app.get("/products")
def get_products(
    category_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    limit: int = Query(default=60, ge=1, le=100)
):
    try:
        engine = get_engine()

        sql = """
            SELECT
                p.product_id,
                p.product_name,
                p.brand_id,
                b.brand_name,
                p.category_id,
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
            WHERE 1=1
        """

        params = {
            "limit": limit
        }

        if category_id is not None:
            sql += " AND p.category_id = :category_id"
            params["category_id"] = category_id

        if keyword:
            sql += " AND p.product_name LIKE :keyword"
            params["keyword"] = f"%{keyword}%"

        sql += " ORDER BY p.product_id ASC LIMIT :limit"

        with engine.connect() as connection:
            result = connection.execute(
                text(sql),
                params
            )

            products = [
                dict(row)
                for row in result.mappings().all()
            ]

        return products

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve products"
        )


# 查詢商品分類
@app.get("/categories")
def get_categories():
    try:
        engine = get_engine()

        sql = """
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_id ASC
        """

        with engine.connect() as connection:
            result = connection.execute(text(sql))

            categories = [
                dict(row)
                for row in result.mappings().all()
            ]

        return categories

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve categories"
        )
