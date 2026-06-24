from rest_framework import viewsets
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer
from tenants.permissions import HasTenant, IsTenantActive
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        HasTenant,
        IsTenantActive
    ]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        HasTenant,
        IsTenantActive
    ]

    queryset = Expense.objects.select_related("category").all()
    serializer_class = ExpenseSerializer