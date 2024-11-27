from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, IncomeViewSet, ExpenseViewSet, TransactionViewSet

router = DefaultRouter()
router.register('wallets', WalletViewSet)
router.register('incomes', IncomeViewSet)
router.register('expenses', ExpenseViewSet)
router.register('transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
