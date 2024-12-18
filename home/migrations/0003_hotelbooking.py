# Generated by Django 5.1.4 on 2024-12-18 15:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_hotel_room_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="HotelBooking",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "booking_type",
                    models.CharField(
                        choices=[("Pre Paid", "Pre Paid"), ("Post Paid", "Post Paid")],
                        max_length=100,
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_bookings",
                        to="home.customer",
                    ),
                ),
                (
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hotel_bookings",
                        to="home.hotel",
                    ),
                ),
            ],
        ),
    ]