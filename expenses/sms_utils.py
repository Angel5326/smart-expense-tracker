"""
SMS alerts via Twilio (or console fallback for dev).
"""
from django.conf import settings


def send_sms(to_number, message):
    """
    Send SMS via Twilio if configured, else print to console.
    Returns: (success_bool, info_string)
    """
    if not to_number:
        return False, 'No phone number.'

    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '')

    # Dev fallback — console
    if not (sid and token and from_number):
        print('\n' + '=' * 60)
        print('📱 [SMS — Console Mode]')
        print(f'To: {to_number}')
        print(f'Message: {message}')
        print('=' * 60 + '\n')
        return True, 'Sent via console (dev mode). Configure Twilio in settings for real SMS.'

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(body=message, from_=from_number, to=to_number)
        return True, 'SMS sent via Twilio.'
    except Exception as e:
        return False, f'Twilio error: {e}'


def check_budget_alerts(user, spent, budget_amount, currency_symbol='₹'):
    """Budget 80%+ cross aanaa SMS anuppum."""
    if not budget_amount or budget_amount <= 0:
        return None

    profile = getattr(user, 'profile', None)
    if not profile or not profile.sms_alerts_enabled or not profile.phone_number:
        return None

    pct = float(spent / budget_amount * 100)
    if pct >= 100:
        return send_sms(
            profile.phone_number,
            f'🚨 SpendWise Alert: You EXCEEDED your monthly budget! '
            f'Spent {currency_symbol}{spent:,.0f} of {currency_symbol}{budget_amount:,.0f} ({pct:.0f}%).'
        )
    elif pct >= 90:
        return send_sms(
            profile.phone_number,
            f'⚠️ SpendWise: You\'ve used {pct:.0f}% of your budget. '
            f'Only {currency_symbol}{float(budget_amount - spent):,.0f} left this month.'
        )
    return None