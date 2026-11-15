from fastapi import APIRouter

from .endpoints import predict, mandi, market, alerts, auth, admin

api_router = APIRouter()

api_router.include_router(predict.router, prefix="/predict", tags=["prediction"])
api_router.include_router(mandi.router, prefix="/mandi", tags=["mandi"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
