from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets, views
from rest_framework.response import Response

from accounts.models import Account

from .models import AuditLog, Transaction
from .serializers import (
    AuditLogSerializer,
    DepositSerializer,
    TransactionSerializer,
    TransferSerializer,
    WithdrawalSerializer,
)


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["transaction_type", "status"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]
    search_fields = ["reference_number", "description", "transaction_type"]

    def get_queryset(self):
        account_ids = Account.objects.filter(user=self.request.user).values_list("id", flat=True)
        return (
            Transaction.objects.filter(Q(from_account_id__in=account_ids) | Q(to_account_id__in=account_ids))
            .select_related("from_account", "to_account")
            .distinct()
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            paginated = self.get_paginated_response(serializer.data)
            paginated.data["success"] = True
            return paginated
        return Response({"success": True, "results": serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"success": True, "transaction": serializer.data}, status=status.HTTP_200_OK)


class BaseTransactionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None
    success_message = ""

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request, "client_ip": get_client_ip(request)},
        )
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        AuditLog.objects.create(
            user=request.user,
            action="transaction_completed",
            resource_type="transaction",
            resource_id=str(transaction.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
            new_values={
                "reference_number": transaction.reference_number,
                "amount": str(transaction.amount),
                "transaction_type": transaction.transaction_type,
            },
        )

        return Response(
            {
                "success": True,
                "message": self.success_message,
                "transaction": TransactionSerializer(transaction).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DepositView(BaseTransactionView):
    serializer_class = DepositSerializer
    success_message = "Deposit completed successfully."


class WithdrawalView(BaseTransactionView):
    serializer_class = WithdrawalSerializer
    success_message = "Withdrawal completed successfully."


class TransferView(BaseTransactionView):
    serializer_class = TransferSerializer
    success_message = "Transfer completed successfully."


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    search_fields = ["action", "resource_type", "status"]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("user").order_by("-created_at")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)
