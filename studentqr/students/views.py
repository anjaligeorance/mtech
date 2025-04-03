from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer
from .utils import process_student_qr, visual_cryptography_decrypt
from django.http import HttpResponse, FileResponse
from PIL import Image
import io
import os
from django.conf import settings

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def perform_create(self, serializer):
        # Save student first
        student = serializer.save()
        # Generate QR code and encrypt
        process_student_qr(student)
    
    @action(detail=True, methods=['get'])
    def decrypt(self, request, pk=None):
        """Decrypt and return the combined QR code"""
        student = self.get_object()
        
        # Get full paths to shares
        share1_path = os.path.join(settings.MEDIA_ROOT, student.share1.name)
        share2_path = os.path.join(settings.MEDIA_ROOT, student.share2.name)
        
        # Decrypt by combining shares
        decrypted_img = visual_cryptography_decrypt(share1_path, share2_path)
        
        # Prepare image for HTTP response
        img_io = io.BytesIO()
        decrypted_img.save(img_io, format='PNG')
        img_io.seek(0)
        
        return FileResponse(img_io, content_type='image/png')