from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from apps.core.database import session_local
from apps.models.salesRecord import SalesRecord
from apps.models.analyticsSummary import AnalyticsSummary
from apps.api.schemas.schemas import AnalyticsSummaryResponse
from fastapi.encoders import jsonable_encoder
from typing import Dict, Optional
from sqlalchemy import func
import redis
import json

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Redis qoşulma
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

def cache_key_builder(prefix: str, **kwargs):
    key = prefix + ":" + ":".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    return key

# ------------------------------
# AnalyticsSummary-based endpoints
# ------------------------------
@router.get("/summary/{file_id}", response_model=AnalyticsSummaryResponse)
def analytics_summary(file_id: str, db: Session = Depends(get_db)):
    key = f"summary:{file_id}"
    if cached := r.get(key):
        return json.loads(cached)

    analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics tapılmadı")

    data = jsonable_encoder(analytics)
    r.setex(key, 300, json.dumps(data))  # 5 dəqiqə cache
    return data

# ------------------------------
# SalesRecord aggregation endpoints
# ------------------------------
@router.get("/products", response_model=Dict)
def analytics_products(
    file_id: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    product_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    key = cache_key_builder("products", file_id=file_id, start_date=start_date, end_date=end_date,
                            region=region, product_name=product_name)
    if cached := r.get(key):
        return json.loads(cached)

    query = db.query(SalesRecord.product_name,
                     func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")) \
              .filter(SalesRecord.uploaded_file_id == file_id)

    if start_date:
        query = query.filter(SalesRecord.date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.date <= end_date)
    if region:
        query = query.filter(SalesRecord.region == region)
    if product_name:
        query = query.filter(SalesRecord.product_name == product_name)

    query = query.group_by(SalesRecord.product_name)
    result = {p: s for p, s in query.all()}

    r.setex(key, 300, json.dumps(result))
    return result

@router.get("/regions", response_model=Dict)
def analytics_regions(
    file_id: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    key = cache_key_builder("regions", file_id=file_id, start_date=start_date, end_date=end_date)
    if cached := r.get(key):
        return json.loads(cached)

    query = db.query(SalesRecord.region,
                     func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")) \
              .filter(SalesRecord.uploaded_file_id == file_id)

    if start_date:
        query = query.filter(SalesRecord.date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.date <= end_date)

    query = query.group_by(SalesRecord.region)
    result = {rgn: s for rgn, s in query.all()}

    r.setex(key, 300, json.dumps(result))
    return result

@router.get("/monthly-trends", response_model=Dict)
def analytics_monthly(file_id: str = Query(...), db: Session = Depends(get_db)):
    key = f"monthly_trends:{file_id}"
    if cached := r.get(key):
        return json.loads(cached)

    query = db.query(
        func.strftime("%Y-%m", SalesRecord.date).label("month"),
        func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")
    ).filter(SalesRecord.uploaded_file_id == file_id) \
     .group_by("month")

    result = {month: total for month, total in query.all()}

    r.setex(key, 300, json.dumps(result))
    return result








































# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from apps.core.database import session_local
# from apps.models.salesRecord import SalesRecord
# from apps.models.analyticsSummary import AnalyticsSummary
# from typing import Dict, Optional
# import redis
# import json
# from datetime import datetime
#
# from sqlalchemy import func
#
#
#
# router = APIRouter()
#
# # Redis qoşulma
# r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
#
# def get_db():
#     db = session_local()
#     try:
#         yield db
#     finally:
#         db.close()
#
# def cache_key_builder(prefix: str, **kwargs):
#     key = prefix + ":" + ":".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
#     return key
#
# @router.get("/analytics/products", response_model=Dict)
# def analytics_products(
#     file_id: str = Query(...),
#     start_date: Optional[str] = Query(None),
#     end_date: Optional[str] = Query(None),
#     region: Optional[str] = Query(None),
#     product_name: Optional[str] = Query(None),
#     db: Session = Depends(get_db)
# ):
#     key = cache_key_builder("products", file_id=file_id, start_date=start_date, end_date=end_date,
#                             region=region, product_name=product_name)
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     query = db.query(SalesRecord.product_name,
#                      db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")) \
#               .filter(SalesRecord.uploaded_file_id == file_id)
#
#     if start_date:
#         query = query.filter(SalesRecord.date >= start_date)
#     if end_date:
#         query = query.filter(SalesRecord.date <= end_date)
#     if region:
#         query = query.filter(SalesRecord.region == region)
#     if product_name:
#         query = query.filter(SalesRecord.product_name == product_name)
#
#     query = query.group_by(SalesRecord.product_name)
#     result = {p: s for p, s in query.all()}
#
#     r.setex(key, 300, json.dumps(result))  # 5 dəqiqə cache
#     return result
#
# @router.get("/analytics/regions", response_model=Dict)
# def analytics_regions(
#     file_id: str = Query(...),
#     start_date: Optional[str] = Query(None),
#     end_date: Optional[str] = Query(None),
#     db: Session = Depends(get_db)
# ):
#     key = cache_key_builder("regions", file_id=file_id, start_date=start_date, end_date=end_date)
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     query = db.query(SalesRecord.region,
#                      db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")) \
#               .filter(SalesRecord.uploaded_file_id == file_id)
#
#     if start_date:
#         query = query.filter(SalesRecord.date >= start_date)
#     if end_date:
#         query = query.filter(SalesRecord.date <= end_date)
#
#     query = query.group_by(SalesRecord.region)
#     result = {rgn: s for rgn, s in query.all()}
#
#     r.setex(key, 300, json.dumps(result))
#     return result
#
# @router.get("/analytics/monthly-trends", response_model=Dict)
# def analytics_monthly(
#     file_id: str = Query(...),
#     db: Session = Depends(get_db)
# ):
#     key = f"monthly_trends:{file_id}"
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     query = db.query(
#         db.func.strftime("%Y-%m", SalesRecord.date).label("month"),
#         db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")
#     ).filter(SalesRecord.uploaded_file_id == file_id) \
#      .group_by("month")
#
#     result = {month: total for month, total in query.all()}
#
#     r.setex(key, 300, json.dumps(result))
#     return result
#
#
#
#
# router = APIRouter(prefix="/analytics", tags=["Analytics"])
#
# @router.get("/products")
# def get_product_sales(
#     start_date: str = Query(None),
#     end_date: str = Query(None),
#     region: str = Query(None),
#     db: Session = Depends(get_db)
# ):
#     query = db.query(SalesRecord.product_name, func.sum(SalesRecord.quantity * SalesRecord.price))
#     # filter-ləri tətbiq et
#     result = query.group_by(SalesRecord.product_name).all()
#     return result
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from apps.core.database import session_local
# # from apps.models.analyticsSummary import AnalyticsSummary
# # from typing import Dict
# #
# # router = APIRouter()
# #
# # def get_db():
# #     db = session_local()
# #     try:
# #         yield db
# #     finally:
# #         db.close()
# #
# # @router.get("/products/{file_id}", response_model=Dict)
# # def analytics_products(file_id: str, db: Session = Depends(get_db)):
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #     return analytics.total_sales_product
# #
# # @router.get("/regions/{file_id}", response_model=Dict)
# # def analytics_regions(file_id: str, db: Session = Depends(get_db)):
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #     return analytics.total_sales_region
# #
# # @router.get("/monthly-trends/{file_id}", response_model=Dict)
# # def analytics_monthly(file_id: str, db: Session = Depends(get_db)):
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #     return analytics.monthly_trends
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from database import session_local
# # from models import AnalyticsSummary
# # from typing import Dict
# # import redis
# # import json
# #
# # router = APIRouter()
# #
# # # Redis qoşulma
# # r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# #
# #
# # def get_db():
# #     db = session_local()
# #     try:
# #         yield db
# #     finally:
# #         db.close()
# #
# #
# # def cache_key_builder(prefix: str, file_id: str):
# #     return f"{prefix}:{file_id}"
# #
# #
# # @router.get("/products/{file_id}", response_model=Dict)
# # def analytics_products(file_id: str, db: Session = Depends(get_db)):
# #     key = cache_key_builder("products", file_id)
# #     if cached := r.get(key):
# #         return json.loads(cached)
# #
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #
# #     r.setex(key, 300, json.dumps(analytics.total_sales_product))  # 5 dəqiqə cache
# #     return analytics.total_sales_product
# #
# #
# # @router.get("/regions/{file_id}", response_model=Dict)
# # def analytics_regions(file_id: str, db: Session = Depends(get_db)):
# #     key = cache_key_builder("regions", file_id)
# #     if cached := r.get(key):
# #         return json.loads(cached)
# #
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #
# #     r.setex(key, 300, json.dumps(analytics.total_sales_region))
# #     return analytics.total_sales_region
# #
# #
# # @router.get("/monthly-trends/{file_id}", response_model=Dict)
# # def analytics_monthly(file_id: str, db: Session = Depends(get_db)):
# #     key = cache_key_builder("monthly_trends", file_id)
# #     if cached := r.get(key):
# #         return json.loads(cached)
# #
# #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# #     if not analytics:
# #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# #
# #     r.setex(key, 300, json.dumps(analytics.monthly_trends))
# #     return analytics.monthly_trends
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# # # from fastapi import APIRouter, Depends, HTTPException
# # # from sqlalchemy.orm import Session
# # # from database import session_local
# # # from models import AnalyticsSummary
# # # from typing import Dict
# # #
# # # router = APIRouter()
# # #
# # # def get_db():
# # #     db = session_local()
# # #     try:
# # #         yield db
# # #     finally:
# # #         db.close()
# # #
# # #
# # #
# # #
# # # @router.get("/products/{file_id}", response_model=Dict)
# # # def analytics_products(file_id: str, db: Session = Depends(get_db)):
# # #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# # #     if not analytics:
# # #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# # #     return analytics.total_sales_product
# # #
# # # @router.get("/regions/{file_id}", response_model=Dict)
# # # def analytics_regions(file_id: str, db: Session = Depends(get_db)):
# # #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# # #     if not analytics:
# # #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# # #     return analytics.total_sales_region
# # #
# # # @router.get("/monthly-trends/{file_id}", response_model=Dict)
# # # def analytics_monthly(file_id: str, db: Session = Depends(get_db)):
# # #     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
# # #     if not analytics:
# # #         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
# # #     return analytics.monthly_trends
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # # # from fastapi import APIRouter, Depends, Query
# # # # from sqlalchemy.orm import Session
# # # # from database import get_db
# # # # from models import SalesRecord
# # # # import redis
# # # # from datetime import datetime
# # # #
# # # # router = APIRouter()
# # # #
# # # # # Redis qoşulma
# # # # r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# # # #
# # # #
# # # # def cache_key_builder(prefix: str, **kwargs):
# # # #     key = prefix + ":" + ":".join([f"{k}={v}" for k, v in kwargs.items() if v])
# # # #     return key
# # # #
# # # #
# # # # @router.get("/products")
# # # # def sales_per_product(
# # # #     start_date: str = Query(None),
# # # #     end_date: str = Query(None),
# # # #     db: Session = Depends(get_db),
# # # # ):
# # # #     key = cache_key_builder("products", start_date=start_date, end_date=end_date)
# # # #     if cached := r.get(key):
# # # #         return {"cached": True, "data": eval(cached)}
# # # #
# # # #     query = db.query(SalesRecord.product_name, db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales"))
# # # #
# # # #     if start_date:
# # # #         query = query.filter(SalesRecord.date >= datetime.fromisoformat(start_date))
# # # #     if end_date:
# # # #         query = query.filter(SalesRecord.date <= datetime.fromisoformat(end_date))
# # # #
# # # #     query = query.group_by(SalesRecord.product_name)
# # # #     result = [{"product_name": p, "total_sales": s} for p, s in query.all()]
# # # #
# # # #     r.setex(key, 300, str(result))
# # # #     return {"cached": False, "data": result}
# # # #
# # # #
# # # # @router.get("/regions")
# # # # def sales_per_region(db: Session = Depends(get_db)):
# # # #     key = "regions"
# # # #     if cached := r.get(key):
# # # #         return {"cached": True, "data": eval(cached)}
# # # #
# # # #     query = db.query(SalesRecord.region, db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales"))
# # # #     query = query.group_by(SalesRecord.region)
# # # #     result = [{"region": rgn, "total_sales": s} for rgn, s in query.all()]
# # # #
# # # #     r.setex(key, 300, str(result))
# # # #     return {"cached": False, "data": result}
# # # #
# # # #
# # # # @router.get("/monthly-trends")
# # # # def monthly_trends(db: Session = Depends(get_db)):
# # # #     key = "monthly_trends"
# # # #     if cached := r.get(key):
# # # #         return {"cached": True, "data": eval(cached)}
# # # #
# # # #     query = db.query(
# # # #         db.func.strftime("%Y-%m", SalesRecord.date).label("month"),
# # # #         db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")
# # # #     ).group_by("month")
# # # #
# # # #     result = [{"month": m, "total_sales": s} for m, s in query.all()]
# # # #
# # # #     r.setex(key, 300, str(result))
# # # #     return {"cached": False, "data": result}
