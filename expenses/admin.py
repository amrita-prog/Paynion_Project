from django.contrib import admin
from .models import Expense, ExpenseSplit

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description','amount','paid_by','group','split_type','created_at',)
    search_fields = ('description','paid_by__full_name','group__title',)
    list_filter = ('split_type','created_at','group',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense',
        'user',
        'amount',
    )
    search_fields = (
        'user__full_name',
        'expense__description',
    )
