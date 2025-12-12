"""
Admin configuration for the Reviews app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review model.
    """
    list_display = [
        'id_short',
        'reviewer_link',
        'target_link',
        'rating_stars',
        'review_type',
        'is_visible',
        'is_flagged',
        'created_at',
    ]
    list_filter = [
        'review_type',
        'rating',
        'is_visible',
        'is_flagged',
        'created_at',
    ]
    search_fields = [
        'reviewer__email',
        'reviewer__full_name',
        'target__email',
        'target__full_name',
        'comment',
    ]
    readonly_fields = [
        'id',
        'response_at',
        'moderated_at',
        'moderated_by',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('id', 'ride', 'review_type')
        }),
        (_('Participants'), {
            'fields': ('reviewer', 'target')
        }),
        (_('Review'), {
            'fields': ('rating', 'comment')
        }),
        (_('Response'), {
            'fields': ('response', 'response_at')
        }),
        (_('Moderation'), {
            'fields': (
                'is_visible',
                'is_flagged',
                'flagged_reason',
                'moderated_at',
                'moderated_by',
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        """Short ID display."""
        return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def reviewer_link(self, obj):
        """Link to reviewer admin page."""
        from django.urls import reverse
        url = reverse('admin:users_user_change', args=[obj.reviewer.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.reviewer.full_name or obj.reviewer.email
        )
    reviewer_link.short_description = _('Reviewer')

    def target_link(self, obj):
        """Link to target admin page."""
        from django.urls import reverse
        url = reverse('admin:users_user_change', args=[obj.target.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.target.full_name or obj.target.email
        )
    target_link.short_description = _('Target')

    def rating_stars(self, obj):
        """Display rating as stars."""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: gold;">{}</span>',
            stars
        )
    rating_stars.short_description = _('Rating')

    actions = ['approve_reviews', 'hide_reviews', 'unflag_reviews']

    @admin.action(description=_('Approve selected reviews'))
    def approve_reviews(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_visible=True,
            is_flagged=False,
            moderated_at=timezone.now(),
            moderated_by=request.user
        )
        self.message_user(request, f'{updated} review(s) approved.')

    @admin.action(description=_('Hide selected reviews'))
    def hide_reviews(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_visible=False,
            is_flagged=False,
            moderated_at=timezone.now(),
            moderated_by=request.user
        )
        self.message_user(request, f'{updated} review(s) hidden.')

    @admin.action(description=_('Unflag selected reviews'))
    def unflag_reviews(self, request, queryset):
        updated = queryset.update(is_flagged=False, flagged_reason='')
        self.message_user(request, f'{updated} review(s) unflagged.')

