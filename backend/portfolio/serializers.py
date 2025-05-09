from rest_framework import serializers
from .models import (
    Portfolio, 
    AboutSection, 
    Education, 
    Skill, 
    Project, 
    Certificate, 
    PortfolioComment
)
from users.serializers import UserSerializer


class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = ['id', 'content', 'photo', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'start_date', 'end_date',
            'description', 'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level', 'category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'image', 'url', 'github_url',
            'start_date', 'end_date', 'is_ongoing', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'id', 'title', 'issuer', 'issue_date', 'expiration_date',
            'description', 'credential_id', 'credential_url', 'file',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = PortfolioComment
        fields = [
            'id', 'portfolio', 'author', 'section', 'text',
            'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'portfolio', 'author', 'created_at', 'updated_at']


class PortfolioCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioComment
        fields = ['portfolio', 'section', 'text', 'rating']
        

class PortfolioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    about = AboutSectionSerializer(read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'title', 'is_public', 'theme',
            'created_at', 'updated_at', 'about', 'educations', 'skills', 'projects', 'certificates', 'comments'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_comments(self, obj):
        # Возвращаем только комментарии, если пользователь имеет права
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        
        # Владелец портфолио, преподаватель или администратор могут видеть все комментарии
        if (request.user == obj.user or 
            request.user.is_teacher() or 
            request.user.is_admin()):
            comments = obj.comments.all()
            return PortfolioCommentSerializer(comments, many=True).data
        return []


class PortfolioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['title', 'is_public', 'theme']
    
    def create(self, validated_data):
        user = self.context['request'].user
        portfolio = Portfolio.objects.create(user=user, **validated_data)
        return portfolio