from modeltranslation.translator import register, TranslationOptions
from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings

@register(CustomUser)
class CustomUserTranslationOptions(TranslationOptions):
    fields = ('bio',)

@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(PortfolioTheme)
class PortfolioThemeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(PortfolioSettings)
class PortfolioSettingsTranslationOptions(TranslationOptions):
    fields = ('custom_css', 'custom_js') 