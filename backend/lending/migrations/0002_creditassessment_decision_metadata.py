from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lending", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="creditassessment",
            name="eligibility",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="creditassessment",
            name="model_version",
            field=models.CharField(default="rules-v1", max_length=50),
        ),
        migrations.AddField(
            model_name="creditassessment",
            name="input_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="creditassessment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="creditassessment",
            name="decision",
            field=models.CharField(
                choices=[
                    ("APPROVED", "Approved"),
                    ("REJECTED", "Rejected"),
                    ("MANUAL_REVIEW", "Manual review"),
                ],
                default="REJECTED",
                max_length=20,
            ),
        ),
    ]