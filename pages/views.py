from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from .models import Wallet, Income, Expense, Transaction
from .serializers import WalletSerializer, IncomeSerializer, ExpenseSerializer, TransactionSerializer

class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class IncomeViewSet(ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class ExpenseViewSet(ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """
        Филтратсия аз рӯйи параметрҳои дархост.
        """
        queryset = super().get_queryset()

        # Филтратсия аз рӯйи амали охирин
        recent = self.request.query_params.get('recent')
        if recent:
            try:
                recent_count = int(recent)
                queryset = queryset.order_by('-time')[:recent_count]
            except ValueError:
                pass

        # Филтратсия аз рӯйи вақт (рӯзона, моҳона, солона)
        period = self.request.query_params.get('period')
        if period == 'daily':
            queryset = queryset.filter(time__date=now().date())
        elif period == 'monthly':
            queryset = queryset.filter(time__year=now().year, time__month=now().month)
        elif period == 'yearly':
            queryset = queryset.filter(time__year=now().year)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Дар натиҷаи API суммаи умумии даромад, хароҷот ва балансро нишон медиҳад.
        """
        response = super().list(request, *args, **kwargs)

        # Ҳисоб кардани даромад ва хароҷоти умумӣ
        income_total = self.get_queryset().filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense_total = self.get_queryset().filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

        # Нишон додани баланс (танҳо барои корбар)
        wallet = Wallet.objects.filter(user=request.user).first()
        balance = wallet.balance if wallet else 0

        # Илова кардани маълумотҳои иловагӣ ба натиҷаи API
        response.data = {
            'balance': balance,
            'total_income': income_total,
            'total_expense': expense_total,
            'transactions': response.data
        }

        return response
