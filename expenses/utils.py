"""
Smart category prediction + AI insights + heatmap + money personality.
"""
import re
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone


# ============================================================
# CATEGORY PREDICTION (Keyword-based)
# ============================================================
CATEGORY_KEYWORDS = {
    'Food': [
        'pizza', 'burger', 'restaurant', 'cafe', 'coffee', 'tea', 'lunch', 'dinner',
        'breakfast', 'swiggy', 'zomato', 'hotel', 'bakery', 'snack', 'biryani',
        'dosa', 'idli', 'ice cream', 'kfc', 'mcdonald', 'dominos', 'food', 'meals',
        'parotta', 'shawarma', 'juice', 'chai',
    ],
    'Groceries': [
        'grocery', 'groceries', 'vegetable', 'vegetables', 'fruit', 'fruits', 'milk',
        'rice', 'supermarket', 'bigbasket', 'dmart', 'zepto', 'blinkit', 'instamart',
        'provision', 'oil', 'dal', 'atta',
    ],
    'Travel': [
        'uber', 'ola', 'taxi', 'cab', 'bus', 'train', 'flight', 'metro', 'petrol',
        'diesel', 'fuel', 'ticket', 'rapido', 'auto', 'toll', 'parking', 'travel',
        'irctc', 'redbus', 'trip', 'airport', 'railway',
    ],
    'Shopping': [
        'amazon', 'flipkart', 'myntra', 'shirt', 'tshirt', 'dress', 'shoes', 'sandal',
        'clothes', 'clothing', 'mall', 'shopping', 'ajio', 'meesho', 'bag', 'watch',
        'jeans', 'kurta', 'saree', 'headphone', 'mobile', 'laptop', 'gadget',
    ],
    'Bills': [
        'electricity', 'current bill', 'water bill', 'gas', 'internet', 'wifi',
        'broadband', 'recharge', 'mobile bill', 'dth', 'bill', 'rent', 'emi',
        'insurance', 'postpaid', 'prepaid', 'maintenance',
    ],
    'Health': [
        'hospital', 'doctor', 'medicine', 'pharmacy', 'tablet', 'clinic', 'gym',
        'fitness', 'medical', 'dental', 'lab', 'scan', 'test', 'yoga', 'protein',
        'consultation',
    ],
    'Entertainment': [
        'movie', 'netflix', 'prime', 'spotify', 'game', 'gaming', 'concert', 'party',
        'hotstar', 'cinema', 'bookmyshow', 'youtube', 'subscription', 'pvr', 'inox',
    ],
    'Education': [
        'book', 'books', 'course', 'udemy', 'coursera', 'tuition', 'college',
        'school', 'fees', 'exam', 'stationery', 'notebook', 'pen', 'semester',
        'coaching', 'certification',
    ],
    'Personal': [
        'salon', 'haircut', 'spa', 'cosmetics', 'perfume', 'gift', 'grooming',
        'skincare', 'barber', 'beauty',
    ],
}

_COMPILED = {
    cat: [re.compile(r'\b' + re.escape(kw) + r'\b') for kw in kws]
    for cat, kws in CATEGORY_KEYWORDS.items()
}


def predict_category(text):
    """Returns (category, confidence_percent)."""
    text = (text or '').lower().strip()
    if not text:
        return 'Other', 0

    scores = {}
    for category, patterns in _COMPILED.items():
        score = 0
        for pattern in patterns:
            hits = len(pattern.findall(text))
            if hits:
                weight = 2 if ' ' in pattern.pattern else 1
                score += hits * weight
        if score:
            scores[category] = score

    if not scores:
        return 'Other', 0

    best = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = round((scores[best] / total) * 100)
    return best, confidence


# ============================================================
# AI INSIGHTS
# ============================================================
def generate_insights(user, expenses_qs, today=None):
    """Rule-based AI insights. Returns list of dicts."""
    from .models import Budget, CATEGORY_META

    today = today or timezone.localdate()
    insights = []

    this_month_start = today.replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    this_total = expenses_qs.filter(date__gte=this_month_start, date__lte=today).aggregate(
        t=Sum('amount'))['t'] or Decimal('0')
    last_total = expenses_qs.filter(date__gte=last_month_start, date__lte=last_month_end).aggregate(
        t=Sum('amount'))['t'] or Decimal('0')

    # 1. Month-over-month
    if last_total > 0:
        change = float((this_total - last_total) / last_total * 100)
        if change >= 25:
            insights.append({
                'type': 'warning', 'icon': 'bi-graph-up-arrow',
                'title': 'Spending Spike Detected',
                'text': f'Your spending is up <b>{change:.0f}%</b> vs last month. Consider reviewing your budget.',
                'color': '#ef4444',
            })
        elif change <= -25:
            insights.append({
                'type': 'success', 'icon': 'bi-graph-down-arrow',
                'title': 'Great Job! 🎉',
                'text': f'You spent <b>{abs(change):.0f}% less</b> than last month. Keep it up!',
                'color': '#22c55e',
            })
        elif -10 <= change <= 10:
            insights.append({
                'type': 'info', 'icon': 'bi-activity',
                'title': 'Consistent Spender',
                'text': f'Your spending is stable (within {abs(change):.0f}% of last month).',
                'color': '#6366f1',
            })

    # 2. Category growth
    def cat_totals(start, end):
        rows = (expenses_qs.filter(date__gte=start, date__lte=end)
                .values('category').annotate(total=Sum('amount')))
        return {r['category'] or 'Other': float(r['total']) for r in rows}

    this_cats = cat_totals(this_month_start, today)
    last_cats = cat_totals(last_month_start, last_month_end)

    biggest_growth = None
    for cat, amt in this_cats.items():
        prev = last_cats.get(cat, 0)
        if prev > 100 and amt > prev * 1.5:
            growth = ((amt - prev) / prev) * 100
            if biggest_growth is None or growth > biggest_growth[1]:
                biggest_growth = (cat, growth, amt)

    if biggest_growth:
        cat, growth, amt = biggest_growth
        meta = CATEGORY_META.get(cat, CATEGORY_META['Other'])
        insights.append({
            'type': 'warning', 'icon': meta['icon'],
            'title': f'{cat} Category Alert',
            'text': f'You spent <b>₹{amt:,.0f}</b> on {cat} this month — up <b>{growth:.0f}%</b>.',
            'color': meta['color'],
        })

    # 3. Budget warnings
    budget = Budget.objects.filter(user=user, month=this_month_start).first()
    if budget and budget.amount > 0:
        pct = float(this_total / budget.amount * 100)
        if pct >= 100:
            insights.append({
                'type': 'danger', 'icon': 'bi-exclamation-octagon-fill',
                'title': '🚨 Budget Exceeded!',
                'text': f'You\'ve used <b>{pct:.0f}%</b> of your monthly budget. Slow down!',
                'color': '#ef4444',
            })
        elif pct >= 80:
            insights.append({
                'type': 'warning', 'icon': 'bi-exclamation-triangle-fill',
                'title': 'Approaching Budget Limit',
                'text': f'You\'ve used <b>{pct:.0f}%</b> of your budget. Only ₹{float(budget.amount - this_total):,.0f} remaining.',
                'color': '#f59e0b',
            })

    # 4. Top spending day of week
    dow_totals = {}
    for e in expenses_qs.filter(date__gte=this_month_start, date__lte=today):
        dow = e.date.strftime('%A')
        dow_totals[dow] = dow_totals.get(dow, 0) + float(e.amount)
    if dow_totals:
        top_dow = max(dow_totals, key=dow_totals.get)
        top_amt = dow_totals[top_dow]
        if top_amt > 0:
            insights.append({
                'type': 'info', 'icon': 'bi-calendar-week-fill',
                'title': f'{top_dow} Spender',
                'text': f'You spend the most on <b>{top_dow}s</b> (₹{top_amt:,.0f} this month).',
                'color': '#8b5cf6',
            })

    # 5. Monthly projection
    if today.day >= 5:
        avg = float(this_total) / today.day
        projected = avg * 30
        insights.append({
            'type': 'info', 'icon': 'bi-speedometer2',
            'title': 'Monthly Projection',
            'text': f'At your current pace, you\'ll spend <b>₹{projected:,.0f}</b> this month.',
            'color': '#06b6d4',
        })

    # 6. Empty state
    if not this_cats:
        insights.append({
            'type': 'info', 'icon': 'bi-lightbulb-fill',
            'title': 'Start Tracking',
            'text': 'Add your first expense this month to unlock smart insights!',
            'color': '#6366f1',
        })

    return insights[:5]


# ============================================================
# HEATMAP
# ============================================================
def build_heatmap(qs, today=None, weeks=13):
    """GitHub-style heatmap. Returns dict with weeks grid + metadata."""
    today = today or timezone.localdate()
    total_days = weeks * 7

    end = today
    start = end - timedelta(days=total_days - 1)

    daily = {}
    rows = (qs.filter(date__gte=start, date__lte=end)
            .values('date').annotate(total=Sum('amount')))
    for r in rows:
        daily[r['date']] = float(r['total'])

    max_amount = max(daily.values()) if daily else 0

    weeks_data = []
    current_week = []

    first_weekday = start.weekday()
    for _ in range(first_weekday):
        current_week.append(None)

    d = start
    while d <= end:
        amt = daily.get(d, 0)
        level = 0
        if max_amount > 0 and amt > 0:
            ratio = amt / max_amount
            if ratio < 0.25:
                level = 1
            elif ratio < 0.5:
                level = 2
            elif ratio < 0.75:
                level = 3
            else:
                level = 4

        current_week.append({
            'date': d,
            'amount': amt,
            'level': level,
            'is_future': d > today,
            'is_today': d == today,
        })

        if len(current_week) == 7:
            weeks_data.append(current_week)
            current_week = []

        d += timedelta(days=1)

    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks_data.append(current_week)

    return {
        'weeks': weeks_data,
        'max_amount': max_amount,
        'start': start,
        'end': end,
    }


# ============================================================
# MONEY PERSONALITY ANALYZER
# ============================================================
def analyze_personality(user, qs=None, today=None):
    """Classify user's money personality. Returns dict."""
    from .models import Expense
    from django.db.models import Avg, Sum, Max

    today = today or timezone.localdate()
    qs = qs or Expense.objects.filter(user=user)

    three_months_ago = today - timedelta(days=90)
    recent = qs.filter(date__gte=three_months_ago)
    count = recent.count()

    if count < 5:
        return {
            'type': 'unknown',
            'emoji': '🌱',
            'title': 'New Tracker',
            'description': 'Keep logging expenses — after 5+ entries, we\'ll reveal your money personality!',
            'color': '#94a3b8',
            'traits': ['Getting started'],
            'tips': ['Add at least 5 expenses', 'Log daily for better insights'],
        }

    total = float(recent.aggregate(t=Sum('amount_in_inr'))['t'] or 0)
    avg_txn = float(recent.aggregate(a=Avg('amount_in_inr'))['a'] or 0)
    monthly_avg = total / 3

    distinct_cats = recent.values('category').distinct().count()

    small_txns = recent.filter(amount_in_inr__lt=200).count()
    small_ratio = small_txns / count if count else 0

    big_txns = recent.filter(amount_in_inr__gte=5000).count()

    cat_totals = recent.values('category').annotate(t=Sum('amount_in_inr')).order_by('-t')
    top_cat = cat_totals[0] if cat_totals else None
    top_cat_pct = (float(top_cat['t']) / total * 100) if top_cat and total else 0

    # Classify
    if small_ratio >= 0.6 and count >= 15:
        personality = {
            'type': 'impulse',
            'emoji': '⚡',
            'title': 'Impulse Buyer',
            'description': f'You make many small purchases ({small_txns} under ₹200 in 3 months). Tiny amounts add up fast!',
            'color': '#f59e0b',
            'traits': [
                f'{int(small_ratio * 100)}% transactions under ₹200',
                f'Avg txn: ₹{avg_txn:,.0f}',
                'Loves quick buys',
            ],
            'tips': [
                'Try 24-hour rule before small purchases',
                'Set daily spending cap',
                'Batch coffee/snack runs weekly',
            ],
        }
    elif big_txns >= 3 and avg_txn >= 2000:
        personality = {
            'type': 'bigticket',
            'emoji': '💎',
            'title': 'Big Ticket Buyer',
            'description': f'You prefer fewer, larger purchases ({big_txns} big txns avg ₹{avg_txn:,.0f}). Quality over quantity!',
            'color': '#8b5cf6',
            'traits': [
                f'Avg transaction: ₹{avg_txn:,.0f}',
                f'{big_txns} big purchases (₹5K+)',
                'Values quality',
            ],
            'tips': [
                'Track big purchases in a wishlist before buying',
                'Wait 7 days for purchases over ₹5,000',
                'Compare 3 options before buying',
            ],
        }
    elif top_cat_pct >= 50 and distinct_cats <= 4:
        personality = {
            'type': 'loyal',
            'emoji': '🎯',
            'title': 'Focused Spender',
            'description': f'{top_cat_pct:.0f}% of your spending is on {top_cat["category"]}. You know what you want!',
            'color': '#06b6d4',
            'traits': [
                f'{top_cat_pct:.0f}% on {top_cat["category"]}',
                f'Only {distinct_cats} categories used',
                'Decisive spender',
            ],
            'tips': [
                f'Set a specific budget for {top_cat["category"]}',
                'Explore if other categories are underserved',
                'Rebalance for long-term goals',
            ],
        }
    elif monthly_avg < 8000 and count >= 10:
        personality = {
            'type': 'saver',
            'emoji': '🐿️',
            'title': 'Smart Saver',
            'description': f'You spend only ₹{monthly_avg:,.0f}/month — disciplined and focused on savings!',
            'color': '#22c55e',
            'traits': [
                f'Monthly avg: ₹{monthly_avg:,.0f}',
                f'{count} transactions in 3 months',
                'Budget conscious',
            ],
            'tips': [
                'Consider investing your savings',
                'Set up automatic SIP',
                'Build 6-month emergency fund',
            ],
        }
    else:
        personality = {
            'type': 'balanced',
            'emoji': '⚖️',
            'title': 'Balanced Spender',
            'description': 'You have a healthy mix of spending — not too high, not too low. Well balanced!',
            'color': '#6366f1',
            'traits': [
                f'Monthly avg: ₹{monthly_avg:,.0f}',
                f'{distinct_cats} categories',
                f'Avg txn: ₹{avg_txn:,.0f}',
            ],
            'tips': [
                'Increase savings rate by 5%',
                'Review subscriptions quarterly',
                'Set up annual financial goals',
            ],
        }

    return personality