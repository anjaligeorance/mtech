from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'class_name', 'roll_number', 'qr_code', 'share1', 'share2', 'created_at']
        read_only_fields = ['id', 'qr_code', 'share1', 'share2', 'created_at']