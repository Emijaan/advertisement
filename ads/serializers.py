from rest_framework import serializers
from .models import Ad

class VideoAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']
