"""
Admin configuration for the Drivers app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Driver, DriverDocument


class DriverDocumentInline(admin.TabularInline):
    """
    Inline admin for driver documents.
    """
    model = DriverDocument
    extra = 0
    readonly_fields = ['reviewed_at', 'reviewed_by', 'created_at']
    fields = [
        'document_type',
        'document_url',
        'status',
        'expiry_date',
        'rejection_reason',
        'reviewed_at',
        'reviewed_by',
    ]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Admin configuration for Driver model.
    """
    list_display = [
        'user',
        'license_number',
        'rating_display',
        'total_trips',
        'is_verified',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'is_verified',
        'is_active',
        'accepts_smoking',
        'accepts_pets',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__full_name',
        'license_number',
    ]
    readonly_fields = [
        'id',
        'rating',
        'total_trips',
        'total_reviews',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    inlines = [DriverDocumentInline]

    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'is_verified', 'is_active')
        }),
        (_('License Information'), {
            'fields': ('license_number', 'license_expiry', 'license_photo_url')
        }),
        (_('Statistics'), {
            'fields': ('rating', 'total_trips', 'total_reviews')
        }),
        (_('Preferences'), {
            'fields': ('bio', 'accepts_smoking', 'accepts_pets', 'accepts_luggage')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_display(self, obj):
        """Display rating with stars."""
        stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html(
            '<span title="{}">{} ({:.1f})</span>',
            f'{obj.rating:.2f}',
            stars,
            obj.rating
        )
    rating_display.short_description = _('Rating')

    actions = ['verify_drivers', 'unverify_drivers']

    @admin.action(description=_('Verify selected drivers'))
    def verify_drivers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} driver(s) verified.')

    @admin.action(description=_('Unverify selected drivers'))
    def unverify_drivers(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} driver(s) unverified.')


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for DriverDocument model.
    """
    list_display = [
        'driver',
        'document_type',
        'status',
        'expiry_date',
        'reviewed_at',
        'created_at',
    ]
    list_filter = [
        'document_type',
        'status',
        'created_at',
    ]
    search_fields = [
        'driver__user__email',
        'driver__user__full_name',
        'driver__license_number',
    ]
    readonly_fields = [
        'id',
        'reviewed_at',
        'reviewed_by',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'driver', 'document_type')
        }),
        (_('Document'), {
            'fields': ('document_url', 'expiry_date')
        }),
        (_('Review'), {
            'fields': ('status', 'rejection_reason', 'reviewed_at', 'reviewed_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_documents', 'reject_documents']

    @admin.action(description=_('Approve selected documents'))
    def approve_documents(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=DriverDocument.DocumentStatus.APPROVED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} document(s) approved.')

    @admin.action(description=_('Reject selected documents'))
    def reject_documents(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=DriverDocument.DocumentStatus.REJECTED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} document(s) rejected.')

