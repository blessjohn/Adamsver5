import uuid

from django.db import migrations


def forwards_seed_amc(apps, schema_editor):
    User = apps.get_model("app", "User")
    PaymentRegistration = apps.get_model("app", "PaymentRegistration")
    for user in User.objects.all().only(
        "id", "username", "first_name", "last_name", "email", "mobile_number"
    ).iterator():
        if PaymentRegistration.objects.filter(
            user_id=user.pk, receipt__startswith="AMC-"
        ).exists():
            continue
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
        receipt = f"AMC-U{user.pk}-{uuid.uuid4().hex[:10].upper()}"
        PaymentRegistration.objects.create(
            user_id=user.pk,
            name=name[:150],
            email=user.email,
            phone=str(user.mobile_number)[:20],
            amount=50000,
            currency="INR",
            receipt=receipt[:100],
            payment_status="paid",
            notes={
                "membership_type": "amc",
                "membership_label": "AMC (₹500)",
                "seeded": True,
            },
        )


def backwards_remove_seeded_amc(apps, schema_editor):
    PaymentRegistration = apps.get_model("app", "PaymentRegistration")
    PaymentRegistration.objects.filter(receipt__startswith="AMC-").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0026_sync_user_mid_adams_format"),
    ]

    operations = [
        migrations.RunPython(forwards_seed_amc, backwards_remove_seeded_amc),
    ]
