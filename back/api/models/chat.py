from django.db import models
from .users import Technician, Company  # Poprawny import dla Twojej struktury

class Message(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} in {self.company} at {self.timestamp}"