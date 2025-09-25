from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.core.database import session_local
from apps.models.analyticsSummary import AnalyticsSummary
from typing import Dict

router = APIRouter()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@router.get("/products/{file_id}", response_model=Dict)
def analytics_products(file_id: str, db: Session = Depends(get_db)):
    analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics tapılmadı")
    return analytics.total_sales_product

@router.get("/regions/{file_id}", response_model=Dict)
def analytics_regions(file_id: str, db: Session = Depends(get_db)):
    analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics tapılmadı")
    return analytics.total_sales_region

@router.get("/monthly-trends/{file_id}", response_model=Dict)
def analytics_monthly(file_id: str, db: Session = Depends(get_db)):
    analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics tapılmadı")
    return analytics.monthly_trends


































# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import session_local
# from models import AnalyticsSummary
# from typing import Dict
# import redis
# import json
#
# router = APIRouter()
#
# # Redis qoşulma
# r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
#
#
# def get_db():
#     db = session_local()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def cache_key_builder(prefix: str, file_id: str):
#     return f"{prefix}:{file_id}"
#
#
# @router.get("/products/{file_id}", response_model=Dict)
# def analytics_products(file_id: str, db: Session = Depends(get_db)):
#     key = cache_key_builder("products", file_id)
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
#     if not analytics:
#         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
#
#     r.setex(key, 300, json.dumps(analytics.total_sales_product))  # 5 dəqiqə cache
#     return analytics.total_sales_product
#
#
# @router.get("/regions/{file_id}", response_model=Dict)
# def analytics_regions(file_id: str, db: Session = Depends(get_db)):
#     key = cache_key_builder("regions", file_id)
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
#     if not analytics:
#         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
#
#     r.setex(key, 300, json.dumps(analytics.total_sales_region))
#     return analytics.total_sales_region
#
#
# @router.get("/monthly-trends/{file_id}", response_model=Dict)
# def analytics_monthly(file_id: str, db: Session = Depends(get_db)):
#     key = cache_key_builder("monthly_trends", file_id)
#     if cached := r.get(key):
#         return json.loads(cached)
#
#     analytics = db.query(AnalyticsSummary).filter(AnalyticsSummary.uploaded_file_id == file_id).first()
#     if not analytics:
#         raise HTTPException(status_code=404, detail="Analytics tapılmadı")
#
#     r.setex(key, 300, json.dumps(analytics.monthly_trends))
#     return analytics.monthly_trends
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
# #
# #
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
# # # from fastapi import APIRouter, Depends, Query
# # # from sqlalchemy.orm import Session
# # # from database import get_db
# # # from models import SalesRecord
# # # import redis
# # # from datetime import datetime
# # #
# # # router = APIRouter()
# # #
# # # # Redis qoşulma
# # # r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# # #
# # #
# # # def cache_key_builder(prefix: str, **kwargs):
# # #     key = prefix + ":" + ":".join([f"{k}={v}" for k, v in kwargs.items() if v])
# # #     return key
# # #
# # #
# # # @router.get("/products")
# # # def sales_per_product(
# # #     start_date: str = Query(None),
# # #     end_date: str = Query(None),
# # #     db: Session = Depends(get_db),
# # # ):
# # #     key = cache_key_builder("products", start_date=start_date, end_date=end_date)
# # #     if cached := r.get(key):
# # #         return {"cached": True, "data": eval(cached)}
# # #
# # #     query = db.query(SalesRecord.product_name, db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales"))
# # #
# # #     if start_date:
# # #         query = query.filter(SalesRecord.date >= datetime.fromisoformat(start_date))
# # #     if end_date:
# # #         query = query.filter(SalesRecord.date <= datetime.fromisoformat(end_date))
# # #
# # #     query = query.group_by(SalesRecord.product_name)
# # #     result = [{"product_name": p, "total_sales": s} for p, s in query.all()]
# # #
# # #     r.setex(key, 300, str(result))
# # #     return {"cached": False, "data": result}
# # #
# # #
# # # @router.get("/regions")
# # # def sales_per_region(db: Session = Depends(get_db)):
# # #     key = "regions"
# # #     if cached := r.get(key):
# # #         return {"cached": True, "data": eval(cached)}
# # #
# # #     query = db.query(SalesRecord.region, db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales"))
# # #     query = query.group_by(SalesRecord.region)
# # #     result = [{"region": rgn, "total_sales": s} for rgn, s in query.all()]
# # #
# # #     r.setex(key, 300, str(result))
# # #     return {"cached": False, "data": result}
# # #
# # #
# # # @router.get("/monthly-trends")
# # # def monthly_trends(db: Session = Depends(get_db)):
# # #     key = "monthly_trends"
# # #     if cached := r.get(key):
# # #         return {"cached": True, "data": eval(cached)}
# # #
# # #     query = db.query(
# # #         db.func.strftime("%Y-%m", SalesRecord.date).label("month"),
# # #         db.func.sum(SalesRecord.quantity * SalesRecord.price).label("total_sales")
# # #     ).group_by("month")
# # #
# # #     result = [{"month": m, "total_sales": s} for m, s in query.all()]
# # #
# # #     r.setex(key, 300, str(result))
# # #     return {"cached": False, "data": result}
