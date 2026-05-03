from django.db import migrations


def forwards_remove_seeded_amc_paid(apps, schema_editor):
    """
    Migration 0027 incorrectly created AMC rows as 'paid'. AMC should be unpaid until
    Razorpay verification marks a real payment. Remove only seeded placeholder rows.
    """
    PaymentRegistration = apps.get_model("app", "PaymentRegistration")
    to_delete = []
    for pr in PaymentRegistration.objects.filter(receipt__startswith="AMC-").iterator():
        notes = pr.notes if isinstance(pr.notes, dict) else {}
        if notes.get("seeded") is True:
            to_delete.append(pr.pk)
            continue
        # Legacy: paid AMC-U* seed without Razorpay capture
        rid = (pr.receipt or "")
        if (
            rid.startswith("AMC-U")
            and pr.payment_status == "paid"
            and not pr.razorpay_payment_id
            and not pr.razorpay_order_id
        ):
            to_delete.append(pr.pk)
    if to_delete:
        PaymentRegistration.objects.filter(pk__in=to_delete).delete()


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0027_seed_amc_payment_all_users"),
    ]

    operations = [
        migrations.RunPython(forwards_remove_seeded_amc_paid, backwards_noop),
    ]
