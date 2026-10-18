from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# ============================================================
# CONSTANTS
# ============================================================
CATEGORY_CHOICES = [
    ('Food', 'Food & Dining'),
    ('Groceries', 'Groceries'),
    ('Travel', 'Travel & Transport'),
    ('Shopping', 'Shopping'),
    ('Bills', 'Bills & Utilities'),
    ('Health', 'Health & Medical'),
    ('Entertainment', 'Entertainment'),
    ('Education', 'Education'),
    ('Personal', 'Personal Care'),
    ('Other', 'Other'),
]

CATEGORY_META = {
    'Food':          {'icon': 'bi-cup-hot-fill',      'color': '#ff6b6b'},
    'Groceries':     {'icon': 'bi-basket-fill',       'color': '#22c55e'},
    'Travel':        {'icon': 'bi-airplane-fill',     'color': '#3b82f6'},
    'Shopping':      {'icon': 'bi-bag-fill',          'color': '#a855f7'},
    'Bills':         {'icon': 'bi-receipt-cutoff',    'color': '#f59e0b'},
    'Health':        {'icon': 'bi-heart-pulse-fill',  'color': '#ef4444'},
    'Entertainment': {'icon': 'bi-controller',        'color': '#ec4899'},
    'Education':     {'icon': 'bi-book-fill',         'color': '#14b8a6'},
    'Personal':      {'icon': 'bi-person-fill',       'color': '#8b5cf6'},
    'Other':         {'icon': 'bi-tag-fill',          'color': '#94a3b8'},
}

CURRENCY_CHOICES = [
    ('INR', 'Indian Rupee (₹)'),
    ('USD', 'US Dollar ($)'),
    ('EUR', 'Euro (€)'),
    ('GBP', 'British Pound (£)'),
    ('SGD', 'Singapore Dollar (S$)'),
    ('AED', 'UAE Dirham (د.إ)'),
    ('JPY', 'Japanese Yen (¥)'),
    ('AUD', 'Australian Dollar (A$)'),
]

CURRENCY_SYMBOLS = {
    'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£',
    'SGD': 'S$', 'AED': 'د.إ', 'JPY': '¥', 'AUD': 'A$',
}

# 1 unit of currency = X INR (demo rates — real app uses API)
EXCHANGE_RATES_TO_INR = {
    'INR': Decimal('1.0'),
    'USD': Decimal('83.5'),
    'EUR': Decimal('90.2'),
    'GBP': Decimal('105.8'),
    'SGD': Decimal('62.0'),
    'AED': Decimal('22.7'),
    'JPY': Decimal('0.55'),
    'AUD': Decimal('54.5'),
}

RECURRENCE_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
]


# ============================================================
# USER PROFILE
# ============================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default='INR'
    )
    email_summary_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=20, blank=True,
        help_text='With country code, e.g. +919876543210'
    )
    sms_alerts_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} · {self.preferred_currency}'

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.preferred_currency, '₹')


# ============================================================
# EXPENSE
# ============================================================
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    amount_in_inr = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, blank=True)
    date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='receipts/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']
        indexes = [models.Index(fields=['user', '-date'])]

    def __str__(self):
        return f'{self.title} — {self.amount} {self.currency}'

    def save(self, *args, **kwargs):
        rate = EXCHANGE_RATES_TO_INR.get(self.currency, Decimal('1.0'))
        self.amount_in_inr = (Decimal(self.amount) * rate).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    @property
    def icon(self):
        return CATEGORY_META.get(self.category, CATEGORY_META['Other'])['icon']

    @property
    def color(self):
        return CATEGORY_META.get(self.category, CATEGORY_META['Other'])['color']

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, '₹')

    @property
    def display_amount(self):
        return f'{self.currency_symbol}{self.amount}'


# ============================================================
# BUDGET
# ============================================================
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']

    def __str__(self):
        return f'{self.user.username} · {self.month:%b %Y} · {self.amount}'


# ============================================================
# SAVINGS GOAL
# ============================================================
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    target_date = models.DateField()
    icon = models.CharField(max_length=40, default='bi-trophy-fill')
    color = models.CharField(max_length=20, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f'{self.name} · {self.saved_amount}/{self.target_amount}'

    @property
    def progress_percent(self):
        if self.target_amount <= 0:
            return 0
        return min(round(float(self.saved_amount / self.target_amount * 100), 1), 100)

    @property
    def remaining(self):
        return max(self.target_amount - self.saved_amount, Decimal('0'))

    @property
    def days_left(self):
        return (self.target_date - timezone.localdate()).days

    @property
    def daily_target(self):
        days = self.days_left
        if days <= 0 or self.remaining <= 0:
            return Decimal('0')
        return round(self.remaining / days, 2)

    @property
    def is_achieved(self):
        return self.saved_amount >= self.target_amount

    @property
    def is_overdue(self):
        return self.days_left < 0 and not self.is_achieved


# ============================================================
# RECURRING EXPENSE
# ============================================================
class RecurringExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    frequency = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='monthly')
    start_date = models.DateField(default=timezone.localdate)
    next_due = models.DateField()
    last_paid = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=40, default='bi-arrow-repeat')
    color = models.CharField(max_length=20, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['next_due']

    def __str__(self):
        return f'{self.title} · {self.frequency}'

    def advance_next_due(self):
        from datetime import timedelta
        d = self.next_due
        if self.frequency == 'daily':
            self.next_due = d + timedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_due = d + timedelta(days=7)
        elif self.frequency == 'monthly':
            self.next_due = d + timedelta(days=30)
        elif self.frequency == 'yearly':
            self.next_due = d + timedelta(days=365)

    @property
    def is_due(self):
        return self.is_active and self.next_due <= timezone.localdate()

    @property
    def days_until_due(self):
        return (self.next_due - timezone.localdate()).days

    @property
    def monthly_equivalent(self):
        if self.frequency == 'daily':
            return self.amount * 30
        elif self.frequency == 'weekly':
            return self.amount * 4
        elif self.frequency == 'monthly':
            return self.amount
        elif self.frequency == 'yearly':
            return self.amount / 12
        return self.amount


# ============================================================
# SPLIT EXPENSE
# ============================================================
class SplitExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='splits')
    title = models.CharField(max_length=150)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Other')
    date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    paid_by_me = models.BooleanField(default=True, help_text='Did you pay the full amount?')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.title} · ₹{self.total_amount}'

    @property
    def participants_count(self):
        return self.participants.count() + 1

    @property
    def my_share(self):
        total = self.total_amount
        count = self.participants_count or 1
        return (total / count).quantize(Decimal('0.01'))

    @property
    def amount_to_receive(self):
        if not self.paid_by_me:
            return Decimal('0')
        return sum((p.share_amount for p in self.participants.all() if not p.is_settled), Decimal('0'))

    @property
    def amount_to_pay(self):
        if self.paid_by_me:
            return Decimal('0')
        return self.my_share


class SplitParticipant(models.Model):
    split = models.ForeignKey(SplitExpense, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    share_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} · ₹{self.share_amount}'


# ============================================================
# GROUP / FAMILY TRACKING
# ============================================================
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMember', related_name='expense_groups')
    icon = models.CharField(max_length=40, default='bi-people-fill')
    color = models.CharField(max_length=20, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def total_spent(self):
        return self.expenses.aggregate(t=models.Sum('amount'))['t'] or Decimal('0')


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f'{self.user.username} in {self.group.name}'


class GroupExpense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_payments')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Other')
    date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.title} · ₹{self.amount}'

    @property
    def per_head(self):
        count = self.group.member_count or 1
        return (self.amount / count).quantize(Decimal('0.01'))