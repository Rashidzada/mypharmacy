from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

from inventory.models import Batch


def _expiry_limits(today=None):
    today = today or timezone.localdate()
    return {
        "today": today,
        "red_limit": today + timedelta(days=45),
        "yellow_limit": today + timedelta(days=90),
        "green_limit": today + timedelta(days=180),
    }


def get_expiry_alert_querysets(today=None):
    limits = _expiry_limits(today)
    base = Batch.objects.filter(quantity__gt=0)
    expired = base.filter(expiry_date__lt=limits["today"])
    critical = base.filter(
        expiry_date__gte=limits["today"],
        expiry_date__lte=limits["red_limit"],
    )
    medium = base.filter(
        expiry_date__gt=limits["red_limit"],
        expiry_date__lte=limits["yellow_limit"],
    )
    low = base.filter(
        expiry_date__gt=limits["yellow_limit"],
        expiry_date__lte=limits["green_limit"],
    )
    return {
        "expired": expired,
        "critical": critical,
        "medium": medium,
        "low": low,
    }


def get_expiry_alert_counts(today=None, cache_seconds=60):
    limits = _expiry_limits(today)
    cache_key = f"expiry_alert_counts:{limits['today']:%Y-%m-%d}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    counts = Batch.objects.filter(quantity__gt=0).aggregate(
        expired=Count("id", filter=Q(expiry_date__lt=limits["today"])),
        critical=Count(
            "id",
            filter=Q(
                expiry_date__gte=limits["today"],
                expiry_date__lte=limits["red_limit"],
            ),
        ),
        medium=Count(
            "id",
            filter=Q(
                expiry_date__gt=limits["red_limit"],
                expiry_date__lte=limits["yellow_limit"],
            ),
        ),
        low=Count(
            "id",
            filter=Q(
                expiry_date__gt=limits["yellow_limit"],
                expiry_date__lte=limits["green_limit"],
            ),
        ),
    )
    cache.set(cache_key, counts, cache_seconds)
    return counts
