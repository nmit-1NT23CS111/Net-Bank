from django.db.models import Q, Sum
from rest_framework import permissions, status, views
from rest_framework.response import Response

from accounts.models import Account
from accounts.serializers import AccountSerializer, CustomUserSerializer
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class HealthCheckView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "net-bank-api"}, status=status.HTTP_200_OK)


class DashboardSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(user=request.user).order_by("-created_at")
        transactions = (
            Transaction.objects.filter(Q(from_account__user=request.user) | Q(to_account__user=request.user))
            .select_related("from_account", "to_account")
            .distinct()
            .order_by("-created_at")
        )

        account_total = accounts.aggregate(total=Sum("balance"))["total"] or 0
        recent_transactions = transactions[:10]

        return Response(
            {
                "success": True,
                "summary": {
                    "user": CustomUserSerializer(request.user).data,
                    "account_count": accounts.count(),
                    "total_balance": str(account_total),
                    "accounts": AccountSerializer(accounts, many=True).data,
                    "recent_transactions": TransactionSerializer(recent_transactions, many=True).data,
                },
            },
            status=status.HTTP_200_OK,
        )
