from ninja import Router
from .porduct import router as PorductRouter

__all__=["router"]

router = Router()

router.add_router("/porduct", PorductRouter)