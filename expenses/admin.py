from django.contrib import admin

from .models import (
    Expense, Budget, SavingsGoal, RecurringExpense,
    SplitExpense, SplitParticipant, UserProfile,
    Group, GroupMember, GroupExpense,
)


# ============================================================
# EXPENSE
# ============================================================
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'amount', 'currency', 'date', 'created_at')
    list_filter = ('category', 'currency', 'date', 'user')
    search_fields = ('title', 'notes', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    list_per_page = 25


# ============================================================
# BUDGET
# ============================================================
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'amount')
    list_filter = ('month', 'user')
    ordering = ('-month',)


# ============================================================
# SAVINGS GOAL
# ============================================================
@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'saved_amount', 'target_date')
    list_filter = ('target_date', 'user')
    search_fields = ('name', 'user__username')
    ordering = ('target_date',)


# ============================================================
# RECURRING EXPENSE
# ============================================================
@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'frequency', 'next_due', 'is_active')
    list_filter = ('frequency', 'is_active', 'user')
    search_fields = ('title',)
    ordering = ('next_due',)


# ============================================================
# SPLIT EXPENSE
# ============================================================
class SplitParticipantInline(admin.TabularInline):
    model = SplitParticipant
    extra = 0
    fields = ('name', 'share_amount', 'is_settled', 'settled_at')
    readonly_fields = ('settled_at',)


@admin.register(SplitExpense)
class SplitExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'total_amount', 'date', 'paid_by_me')
    list_filter = ('date', 'paid_by_me', 'category', 'user')
    search_fields = ('title', 'notes')
    inlines = [SplitParticipantInline]
    ordering = ('-date',)


# ============================================================
# USER PROFILE
# ============================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'preferred_currency', 'phone_number',
        'sms_alerts_enabled', 'email_summary_enabled',
    )
    list_filter = ('preferred_currency', 'sms_alerts_enabled', 'email_summary_enabled')
    search_fields = ('user__username', 'phone_number')


# ============================================================
# GROUP / FAMILY
# ============================================================
class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 0
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)
    autocomplete_fields = ('user',)


class GroupExpenseInline(admin.TabularInline):
    model = GroupExpense
    extra = 0
    fields = ('title', 'paid_by', 'amount', 'category', 'date')
    readonly_fields = ()


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'member_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'created_by__username', 'description')
    inlines = [GroupMemberInline, GroupExpenseInline]
    ordering = ('-created_at',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(GroupExpense)
class GroupExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'paid_by', 'amount', 'category', 'date')
    list_filter = ('category', 'date', 'group')
    search_fields = ('title', 'notes', 'paid_by__username')
    ordering = ('-date',)