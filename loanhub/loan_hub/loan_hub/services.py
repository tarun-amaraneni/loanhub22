# from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
# from django.db import transaction
# from django.utils import timezone
# import logging
# from .models import Loan, LoanRepayment, InterestRate

# logger = logging.getLogger(__name__)
# DAYS_IN_YEAR = Decimal('365')

# # ----------------------------
# # Helper
# # ----------------------------
# def safe_decimal(val, default=Decimal('0.00')):
#     try:
#         return Decimal(val)
#     except (TypeError, ValueError, InvalidOperation):
#         return default

# # ----------------------------
# # Loan repayment processor
# # ----------------------------
# @transaction.atomic
# def process_loan_repayment(loan):
#     """
#     Recalculate interest and principal allocation from scratch.
#     """
#     # Fetch rate
#     try:
#         rate_obj = InterestRate.objects.get(Type_of_Receipt=loan.type_of_loan)
#         ANNUAL_RATE = safe_decimal(rate_obj.interest) / Decimal('100')
#     except InterestRate.DoesNotExist:
#         ANNUAL_RATE = Decimal('0.15')

#     # Reset principal & interest
#     principal = safe_decimal(loan.amount)
#     interest_due = Decimal('0.00')  # <-- RESET here to avoid double counting
#     last_date = loan.created_at.date()

#     repayments = loan.loanrepayment_set.all().order_by('created_at')

#     for rep in repayments:
#         rep_date = rep.created_at.date()
#         days = (rep_date - last_date).days
#         if days > 0 and principal > 0:
#             interest_due += (principal * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR).quantize(
#                 Decimal('0.01'), rounding=ROUND_HALF_UP
#             )

#         payment = safe_decimal(rep.total_payment)
#         paid_interest = min(payment, interest_due)
#         payment -= paid_interest
#         interest_due -= paid_interest

#         paid_principal = min(payment, principal)
#         principal -= paid_principal

#         rep.paid_to_interest = paid_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         rep.paid_to_principal = paid_principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         rep.save(update_fields=['paid_to_interest', 'paid_to_principal'])

#         last_date = rep_date

#     # Interest up to today
#     today = timezone.now().date()
#     days = (today - last_date).days
#     if days > 0 and principal > 0:
#         interest_due += (principal * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR).quantize(
#             Decimal('0.01'), rounding=ROUND_HALF_UP
#         )

#     # Update loan DB
#     loan.balance = principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     loan.interest = interest_due.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     if principal <= 0 and interest_due <= 0:
#         loan.loan_status = 'Closed'
#     loan.save()
#     print("✅ DONE | Balance:", principal, "Interest:", interest_due, flush=True)



from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.db import transaction
from django.utils import timezone
import logging
from .models import Loan, LoanRepayment, InterestRate
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.db import transaction
from django.utils import timezone
import logging
import json
from .models import Loan, LoanRepayment, InterestRate

logger = logging.getLogger(__name__)
DAYS_IN_YEAR = Decimal('365')
ACCUMULATIVE_TYPES = {'THRIFT FUNDS', 'WELFARE COLLECTIONS'}


def safe_decimal(val, default=Decimal('0.00')):
    try:
        return Decimal(str(val))
    except (TypeError, ValueError, InvalidOperation):
        return default


def get_deposit_entries(loan):
    """Read deposit log from loan.source (stored as JSON string)."""
    try:
        data = json.loads(loan.source or '[]')
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def set_deposit_entries(loan, entries):
    """Write deposit log to loan.source as JSON string."""
    loan.source = json.dumps(entries)


# ──────────────────────────────────────────────────────────────────────────────
# STANDARD LOAN PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

@transaction.atomic
def process_loan_repayment(loan):
    """
    Recalculate interest and principal for a standard loan from scratch.
    Each repayment reduces the outstanding principal.
    """
    try:
        try:
            rate_obj = InterestRate.objects.get(Type_of_Receipt=loan.type_of_loan)
            ANNUAL_RATE = safe_decimal(rate_obj.interest) / Decimal('100')
        except InterestRate.DoesNotExist:
            ANNUAL_RATE = Decimal('0.15')

        principal    = safe_decimal(loan.amount)
        interest_due = Decimal('0.00')
        last_date    = loan.created_at.date()
        updated_reps = []

        repayments = loan.loanrepayment_set.all().order_by('created_at', 'id')

        for rep in repayments:
            rep_date = rep.created_at.date()
            days     = (rep_date - last_date).days

            if days > 0 and principal > 0:
                interest_due += (
                    principal * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR
                ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            payment = safe_decimal(rep.total_payment)

            paid_interest  = min(payment, interest_due)
            payment       -= paid_interest
            interest_due  -= paid_interest

            paid_principal  = min(payment, principal)
            principal      -= paid_principal

            rep.paid_to_interest  = paid_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            rep.paid_to_principal = paid_principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            updated_reps.append(rep)
            last_date = rep_date

        if updated_reps:
            LoanRepayment.objects.bulk_update(
                updated_reps, ['paid_to_interest', 'paid_to_principal']
            )

        today = timezone.now().date()
        days  = (today - last_date).days
        if days > 0 and principal > 0:
            interest_due += (
                principal * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        loan.balance  = principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        loan.interest = interest_due.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if principal <= 0 and interest_due <= 0:
            loan.loan_status = 'Closed'

        loan.save()
        print(f"✅ STANDARD | Loan {loan.id} | Balance: {loan.balance} | Interest: {loan.interest}", flush=True)

    except Exception as e:
        logger.error(f"🔥 process_loan_repayment failed for Loan {loan.id}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# ACCUMULATIVE DEPOSIT PROCESSING
# (THRIFT FUNDS, WELFARE COLLECTIONS)
#
# ONE loan record per member per type.
# Individual deposits stored in loan.source as JSON:
#   [{"date": "2024-01-01", "amount": "5000.00"}, ...]
# ──────────────────────────────────────────────────────────────────────────────

@transaction.atomic
def process_deposit_account(gen_no, loan_type):
    """
    Recalculates running balance and simple interest for accumulative accounts.

    Deposit history is stored in loan.source as a JSON list.
    Each entry: {"date": "YYYY-MM-DD", "amount": "1000.00"}
    Interest is calculated per interval between events on the constant balance.
    """
    try:
        try:
            rate_obj = InterestRate.objects.get(Type_of_Receipt=loan_type)
            ANNUAL_RATE = safe_decimal(rate_obj.interest) / Decimal('100')
        except InterestRate.DoesNotExist:
            ANNUAL_RATE = Decimal('0.15')

        loan = Loan.objects.filter(
            gen_no=gen_no,
            type_of_loan=loan_type,
            loan_status='Active'
        ).order_by('created_at', 'id').first()

        if not loan:
            return

        repayments = list(
            loan.loanrepayment_set.all().order_by('created_at', 'id')
        )

        # ── Load deposit entries from loan.source ─────────────────────────────
        import datetime as dt_module
        raw_entries = get_deposit_entries(loan)

        deposit_entries = []
        for entry in raw_entries:
            raw_date = entry['date']
            if isinstance(raw_date, str):
                raw_date = dt_module.date.fromisoformat(raw_date)
            deposit_entries.append({
                'date':   raw_date,
                'amount': safe_decimal(entry['amount']),
            })

        # Fallback: if source is empty treat loan.amount as the first deposit
        if not deposit_entries:
            deposit_entries = [{
                'date':   loan.created_at.date(),
                'amount': safe_decimal(loan.amount),
            }]

        # ── Build unified event list ───────────────────────────────────────────
        events = []

        for dep in deposit_entries:
            events.append({
                'date':   dep['date'],
                'type':   'deposit',
                'amount': dep['amount'],
            })

        for rep in repayments:
            events.append({
                'date':   rep.created_at.date(),
                'type':   'repayment',
                'amount': safe_decimal(rep.total_payment),
                'obj':    rep,
            })

        # Deposits before repayments on the same date
        events.sort(key=lambda e: (e['date'], 0 if e['type'] == 'deposit' else 1))

        # ── Walk the timeline ─────────────────────────────────────────────────
        balance      = Decimal('0.00')
        interest_due = Decimal('0.00')
        last_date    = events[0]['date']
        updated_reps = []

        for event in events:
            current_date = event['date']
            days = (current_date - last_date).days

            if days > 0 and balance > 0:
                interest_due += (
                    balance * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR
                ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if event['type'] == 'deposit':
                balance += event['amount']

            elif event['type'] == 'repayment':
                rep     = event['obj']
                payment = event['amount']

                paid_interest = min(payment, interest_due)
                payment      -= paid_interest
                interest_due -= paid_interest

                paid_principal = min(payment, balance)
                balance       -= paid_principal

                rep.paid_to_interest  = paid_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                rep.paid_to_principal = paid_principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                updated_reps.append(rep)

            last_date = current_date

        # Interest from last event → today
        today = timezone.now().date()
        days  = (today - last_date).days
        if days > 0 and balance > 0:
            interest_due += (
                balance * ANNUAL_RATE * Decimal(days) / DAYS_IN_YEAR
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if updated_reps:
            LoanRepayment.objects.bulk_update(
                updated_reps, ['paid_to_interest', 'paid_to_principal']
            )

        loan.balance  = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        loan.interest = interest_due.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        loan.save()

        print(
            f"✅ ACCUMULATIVE | [{loan_type}] gen_no={gen_no} | "
            f"Balance: {loan.balance} | Interest: {loan.interest}",
            flush=True
        )

    except Exception as e:
        logger.error(f"🔥 process_deposit_account failed for {gen_no} / {loan_type}: {e}")