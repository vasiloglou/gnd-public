"""Report currency explicitly after the model adds its currency requirement."""


def summarize(facts):
    submitted = {row["expense"] for row in facts["expense_submitted_by_employee"]}
    amounts = {row["expense"]: row["amount"] for row in facts["expense_has_amount"]}
    currencies = {row["expense"]: row["currency"] for row in facts["expense_has_currency"]}
    totals = {}
    for expense in sorted(submitted):
        currency = currencies[expense]
        totals[currency] = totals.get(currency, 0) + amounts[expense]
    return {
        "submitted": len(submitted),
        "approved": len(facts["expense_is_approved"]),
        "totals_by_currency": totals,
    }
