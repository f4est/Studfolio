from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import SupportTicket, TicketResponse, TicketAttachment, SupportCategory, KnowledgeBaseArticle

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'content', 'created_at')
        }),
        (_('Дополнительно'), {
            'fields': ('is_internal_note',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'category', 'status', 'priority', 'created_at', 'assigned_to')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'description', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    date_hierarchy = 'created_at'
    inlines = [TicketResponseInline, TicketAttachmentInline]
    save_on_top = True
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']
    fieldsets = (
        (_('Информация о тикете'), {
            'fields': ('subject', 'user', 'category', 'description')
        }),
        (_('Статус и приоритет'), {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'is_closed'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, _(f"{updated} тикетов помечены как 'В обработке'."))
    mark_as_in_progress.short_description = _("Пометить как 'В обработке'")
    
    def mark_as_resolved(self, request, queryset):
        for ticket in queryset:
            ticket.resolve()
        self.message_user(request, _(f"{queryset.count()} тикетов помечены как 'Решены'."))
    mark_as_resolved.short_description = _("Пометить как 'Решены'")
    
    def mark_as_closed(self, request, queryset):
        for ticket in queryset:
            ticket.close()
        self.message_user(request, _(f"{queryset.count()} тикетов помечены как 'Закрыты'."))
    mark_as_closed.short_description = _("Пометить как 'Закрыты'")


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_link', 'user', 'created_at', 'is_internal_note')
    list_filter = ('is_internal_note', 'created_at')
    search_fields = ('content', 'user__username', 'ticket__subject')
    readonly_fields = ('created_at',)
    
    def ticket_link(self, obj):
        url = reverse('admin:support_supportticket_change', args=[obj.ticket.id])
        return format_html('<a href="{}">{}</a>', url, obj.ticket)
    ticket_link.short_description = _('Тикет')
    ticket_link.admin_order_field = 'ticket__id'


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_link', 'file_name', 'uploaded_at')
    search_fields = ('file_name', 'ticket__subject')
    readonly_fields = ('uploaded_at',)
    
    def ticket_link(self, obj):
        url = reverse('admin:support_supportticket_change', args=[obj.ticket.id])
        return format_html('<a href="{}">{}</a>', url, obj.ticket)
    ticket_link.short_description = _('Тикет')
    ticket_link.admin_order_field = 'ticket__id'


@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'views_count', 'created_at', 'updated_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'content')
        }),
        (_('Публикация'), {
            'fields': ('is_published', 'views_count', 'created_at', 'updated_at')
        }),
    )
