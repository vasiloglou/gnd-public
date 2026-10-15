"""Report for the initial EUR-only domain, written by the application developer."""


def summarize(facts):
    submitted = {row["expense"] for row in facts["expense_submitted_by_employee"]}
    amounts = {row["expense"]: row["amount"] for row in facts["expense_has_amount"]}
    return {
        "submitted": len(submitted),
        "approved": len(facts["expense_is_approved"]),
        "total_eur": sum(amounts[expense] for expense in submitted),
    }
