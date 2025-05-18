from modeltranslation.translator import register, TranslationOptions
from .models import Project, Certificate, Achievement, Review, ProjectPost, ProjectComment


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'technologies')


@register(Certificate)
class CertificateTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'issuer', 'issuing_organization')


@register(Achievement)
class AchievementTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'organizer', 'category', 'issuing_organization')


@register(Review)
class ReviewTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(ProjectPost)
class ProjectPostTranslationOptions(TranslationOptions):
    fields = ('content',)


@register(ProjectComment)
class ProjectCommentTranslationOptions(TranslationOptions):
    fields = ('text',) 