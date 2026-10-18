from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from decimal import Decimal

from .models import (
    Expense, Budget, SavingsGoal, RecurringExpense, SplitExpense,
    SplitParticipant, UserProfile, Group, GroupMember, GroupExpense,
    CATEGORY_CHOICES, CURRENCY_CHOICES
)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Your name',
            'username': 'Choose a username',
            'email': 'you@example.com',
            'password1': 'Create password (min 8 characters)',
            'password2': 'Confirm password',
        }
        icons = {
            'first_name': 'bi-person',
            'username': 'bi-at',
            'email': 'bi-envelope',
            'password1': 'bi-lock',
            'password2': 'bi-shield-lock',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': placeholders.get(name, ''),
            })
            field.icon = icons.get(name, 'bi-input-cursor')

        self.fields['password1'].widget.attrs.update({'id': 'id_password1', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'id': 'id_password2', 'autocomplete': 'new-password'})

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class ExpenseForm(forms.ModelForm):
    # ⭐ FIX: Accept DD-MM-YYYY, YYYY-MM-DD, and DD/MM/YYYY formats
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date', 'required': True}),
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']
    )

    class Meta:
        model = Expense
        fields = ('title', 'amount', 'currency', 'category', 'date', 'notes', 'receipt')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Uber ride to office',
                'id': 'id_title', 'autocomplete': 'off', 'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.01', 'min': '0.01', 'placeholder': '0.00', 'required': True,
            }),
            'currency': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_currency'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_category'}),
            # 'date' is handled above
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes',
            }),
            'receipt': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*', 'id': 'id_receipt',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].choices = [('', '✨ Auto-detect from description')] + list(CATEGORY_CHOICES)
        self.fields['receipt'].required = False
        self.fields['receipt'].help_text = '📸 Upload a photo of the bill (optional, max 5MB)'

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt and hasattr(receipt, 'size'):
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image too large. Max 5MB allowed.')
        return receipt


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('amount',)
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.01', 'min': '1', 'placeholder': 'e.g. 20000',
            }),
        }


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ('name', 'target_amount', 'saved_amount', 'target_date', 'icon', 'color')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. New iPhone'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'min': '1', 'placeholder': '50000'}),
            'saved_amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'min': '0', 'placeholder': '0'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'icon': forms.HiddenInput(),
            'color': forms.HiddenInput(),
        }


class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ('title', 'amount', 'category', 'frequency', 'start_date', 'next_due', 'is_active', 'icon', 'color')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Netflix subscription'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'min': '1', 'placeholder': '199'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'frequency': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'next_due': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'icon': forms.HiddenInput(),
            'color': forms.HiddenInput(),
        }


class SplitExpenseForm(forms.ModelForm):
    class Meta:
        model = SplitExpense
        fields = ('title', 'total_amount', 'category', 'date', 'paid_by_me', 'notes')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Dinner at restaurant'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'min': '1', 'placeholder': '1200'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'paid_by_me': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes'}),
        }


class SplitParticipantForm(forms.ModelForm):
    class Meta:
        model = SplitParticipant
        fields = ('name', 'share_amount', 'is_settled')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Friend name'}),
            'share_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'is_settled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


SplitParticipantFormSet = inlineformset_factory(
    SplitExpense, SplitParticipant, form=SplitParticipantForm,
    extra=2, can_delete=True, min_num=1, validate_min=True,
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('preferred_currency', 'email_summary_enabled')
        widgets = {
            'preferred_currency': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'email_summary_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description', 'icon', 'color')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Sharma Family'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional — what is this group for?'}),
            'icon': forms.HiddenInput(),
            'color': forms.HiddenInput(),
        }


class GroupExpenseForm(forms.ModelForm):
    class Meta:
        model = GroupExpense
        fields = ('title', 'amount', 'category', 'date', 'notes')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Groceries'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
        }


class GroupInviteForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter username to invite'})
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'No user found with username "{username}".')
        self.found_user = user
        return username