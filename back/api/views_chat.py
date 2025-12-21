from rest_framework import viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination
from .models.chat import Message
from .serializers_chat import MessageSerializer
from .views import IsCompanyMember  # Importujemy Twoje istniejące uprawnienie

class MessagePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    pagination_class = MessagePagination

    def get_queryset(self):
        technician = self.request.user.technician_profile
        queryset = Message.objects.filter(company=technician.company).select_related('sender')

        return queryset.order_by('-timestamp')