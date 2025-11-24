import json
import bleach
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models.chat import Message
from .models.users import Technician


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Uwierzytelnianie - AuthMiddlewareStack już to robi, ale to jest podwójne zabezpieczenie.
        if not self.user.is_authenticated:
            await self.close()
            return

        # Pobierz profil technika i firmę. To jest bezpieczne, bo IsCompanyMember to wymusza.
        self.technician = await self.get_technician_profile(self.user)
        if not self.technician:
            await self.close()
            return

        self.company = self.technician.company
        self.room_group_name = f'chat_company_{self.company.id}'

        # Dołącz do pokoju czatu firmy
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data.get('message', '').strip()
        except (json.JSONDecodeError, AttributeError):
            return  # Ignoruj nieprawidłowe dane

        # Podstawowa walidacja
        if not message_content or len(message_content) > 1024:
            return

        # Sanityzacja, aby zapobiec XSS
        clean_content = bleach.clean(message_content, strip=True)

        # Zapisz wiadomość w bazie
        new_message = await self.save_message(clean_content)

        # Przygotuj dane do wysłania do wszystkich w pokoju
        message_payload = {
            'id': new_message.id,
            'sender_id': self.technician.id,
            'sender_name': self.technician.full_name,  # Używamy property z Twojego modelu
            'content': new_message.content,
            'timestamp': new_message.timestamp.isoformat(),
        }

        # Wyślij wiadomość do grupy (pokoju)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',  # Wywoła metodę chat_message
                'message': message_payload
            }
        )

    # Handler, który odbiera wiadomość z grupy i wysyła ją do klienta przez WebSocket
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    # Metoda pomocnicza do asynchronicznego dostępu do bazy
    @database_sync_to_async
    def get_technician_profile(self, user):
        try:
            # Używamy prefetch_related, aby od razu pobrać firmę
            return Technician.objects.select_related('company').get(user=user)
        except Technician.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        return Message.objects.create(
            company=self.company,
            sender=self.technician,
            content=content
        )