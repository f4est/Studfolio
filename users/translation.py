from modeltranslation.translator import register, TranslationOptions
from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings, ResumeTemplate

@register(CustomUser)
class CustomUserTranslationOptions(TranslationOptions):
    fields = ('bio', 'university', 'faculty', 'specialization')

@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(PortfolioTheme)
class PortfolioThemeTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ResumeTemplate)
class ResumeTemplateTranslationOptions(TranslationOptions):
    fields = ('name', 'description',) 