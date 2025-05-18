from modeltranslation.translator import register, TranslationOptions
from .models import SupportCategory, KnowledgeBaseArticle, SupportTicket

@register(SupportCategory)
class SupportCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(KnowledgeBaseArticle)
class KnowledgeBaseArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(SupportTicket)
class SupportTicketTranslationOptions(TranslationOptions):
    fields = ('subject',) 