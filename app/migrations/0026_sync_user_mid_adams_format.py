from django.db import migrations


def forwards_sync_mid(apps, schema_editor):
    User = apps.get_model("app", "User")
    for uid in User.objects.order_by("pk").values_list("pk", flat=True):
        canonical = f"ADAMS-{uid:06d}"
        User.objects.filter(pk=uid).update(mid=canonical)


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0025_paymentregistration_user"),
    ]

    operations = [
        migrations.RunPython(forwards_sync_mid, backwards_noop),
    ]
