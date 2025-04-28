from datetime import timedelta
from django.utils import timezone

from django.contrib import admin
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ValidationError


class GoldSettings(models.Model):
    weekly_gold_cap = models.PositiveIntegerField(default=1000, help_text='Gold cap per week')

    def clean(self):
        # If we’re creating (no PK yet) and another exists, it’s invalid
        if not self.pk and GoldSettings.objects.exists():
            raise ValidationError("Can only have one GoldSettings instance")

    def save(self, *args, **kwargs):
        # run the clean check before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Gold Settings"

    class Meta:
        verbose_name_plural = "Gold Settings"


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    gold = models.PositiveIntegerField(default=0)
    weekly_earned = models.PositiveIntegerField(default=0)
    week_start = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        now = timezone.now()
        if now - self.week_start >= timedelta(days=7):
            self.week_start = now
            self.weekly_earned = 0

        if self.pk:
            old = Profile.objects.get(pk=self.pk)
            gain = self.gold - old.gold
        else:
            gain = self.gold

        SettingsModel = apps.get_model('accounts', 'GoldSettings')
        try:
            cap = SettingsModel.objects.first().weekly_gold_cap
        except (AttributeError, TypeError):
            cap = 1000

        if gain > 0:
            allowed = max(cap - self.weekly_earned, 0)
            if gain > allowed:
                gain = allowed
                self.gold = old.gold + allowed
            self.weekly_earned += gain

        super().save(*args, **kwargs)


@admin.register(GoldSettings)
class GoldSettingsAdmin(admin.ModelAdmin):
    list_display = ('weekly_gold_cap',)

# Create a custom UserAdmin class
class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ("gold","weekly_earned","week_start")
    readonly_fields = ("weekly_earned", "week_start")
    extra = 1
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined', 'gold_balance')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
    def gold_balance(self, obj):
        return obj.profile.gold
    gold_balance.short_description = 'Gold'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Unregister the default UserAdmin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
