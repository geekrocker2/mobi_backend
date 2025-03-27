from rest_framework import serializers
from .models import CustomUser
from .models import DirectMessage


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'profile_photo', 'location', 'date_of_birth',
            'interests', 'theme_song', 'top_friends'
        ]
        read_only_fields = ['id', 'username', 'email']

    def validate_top_friends(self, value):
        """
        Ensure that no more than 8 friends are selected as top friends.
        'value' is expected to be a list of user IDs.
        """
        if len(value) > 8:
            raise serializers.ValidationError("You can select up to 8 top friends only.")
        return value
class DirectMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'receiver', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']