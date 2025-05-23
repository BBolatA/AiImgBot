# Generated by Django 5.2 on 2025-04-22 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GenerationTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("prompt", models.TextField()),
                ("tg_chat_id", models.BigIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QUEUED", "Queued"),
                            ("STARTED", "Started"),
                            ("READY", "Ready"),
                            ("ERROR", "Error"),
                        ],
                        default="QUEUED",
                        max_length=10,
                    ),
                ),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="fooocus/"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
