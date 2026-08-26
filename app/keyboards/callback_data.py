from aiogram.filters.callback_data import CallbackData


class OnboardingCallback(CallbackData, prefix="onboarding"):
    action: str


class QuestionCallback(CallbackData, prefix="question"):
    action: str
    value: str