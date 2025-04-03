from django.db import models

import uuid

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=50)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    share1 = models.ImageField(upload_to='shares/', blank=True)
    share2 = models.ImageField(upload_to='shares/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.class_name} - {self.roll_number}"