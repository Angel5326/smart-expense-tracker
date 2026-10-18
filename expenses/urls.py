from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    # ============================================================
    # Dashboard
    # ============================================================
    path('', views.dashboard, name='dashboard'),

    # ============================================================
    # Authentication
    # ============================================================
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ============================================================
    # Expenses
    # ============================================================
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # ============================================================
    # Budget
    # ============================================================
    path('budget/', views.manage_budget, name='manage_budget'),

    # ============================================================
    # Savings Goals
    # ============================================================
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/add/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_update, name='goal_update'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('goals/<int:pk>/add-savings/', views.goal_add_savings, name='goal_add_savings'),

    # ============================================================
    # Recurring Expenses
    # ============================================================
    path('recurring/', views.recurring_list, name='recurring_list'),
    path('recurring/add/', views.recurring_create, name='recurring_create'),
    path('recurring/<int:pk>/edit/', views.recurring_update, name='recurring_update'),
    path('recurring/<int:pk>/delete/', views.recurring_delete, name='recurring_delete'),
    path('recurring/<int:pk>/mark-paid/', views.recurring_mark_paid, name='recurring_mark_paid'),
    path('recurring/<int:pk>/toggle/', views.recurring_toggle, name='recurring_toggle'),

    # ============================================================
    # Split Expenses
    # ============================================================
    path('splits/', views.split_list, name='split_list'),
    path('splits/add/', views.split_create, name='split_create'),
    path('splits/<int:pk>/', views.split_detail, name='split_detail'),
    path('splits/<int:pk>/edit/', views.split_update, name='split_update'),
    path('splits/<int:pk>/delete/', views.split_delete, name='split_delete'),
    path('splits/<int:pk>/settle/<int:participant_pk>/', views.split_settle, name='split_settle'),

    # ============================================================
    # Groups / Family
    # ============================================================
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/add-expense/', views.group_add_expense, name='group_add_expense'),
    path('groups/<int:pk>/invite/', views.group_invite, name='group_invite'),
    path('groups/<int:pk>/leave/', views.group_leave, name='group_leave'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    # ============================================================
    # Settings
    # ============================================================
    path('settings/currency/', views.currency_settings, name='currency_settings'),
    path('settings/sms/', views.sms_settings, name='sms_settings'),
    path('settings/sms/test/', views.sms_test, name='sms_test'),

    # ============================================================
    # Personality + ML
    # ============================================================
    path('personality/', views.personality_view, name='personality'),
    path('ml/train/', views.ml_train_view, name='ml_train_view'),

    # ============================================================
    # API
    # ============================================================
    path('api/predict-category/', views.predict_category_api, name='predict_category_api'),

    # ============================================================
    # Reports / Exports
    # ============================================================
    path('reports/csv/', views.export_csv, name='export_csv'),
    path('reports/pdf/', views.export_pdf, name='export_pdf'),
    path('reports/excel/', views.export_excel, name='export_excel'),

    # ============================================================
    # Email
    # ============================================================
    path('email/send-summary/', views.send_summary_now, name='send_summary_now'),
]