from aiogram import Router

from app.handlers.onboarding import router as onboarding_router
from app.handlers.start import router as start_router

main_router = Router(name="main")
main_router.include_router(start_router)
main_router.include_router(onboarding_router)
