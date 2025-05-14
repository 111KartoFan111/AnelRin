from django import forms
from weddings.models import GeminiChat

class GeminiChatForm(forms.ModelForm):
    class Meta:
        model = GeminiChat
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите ваш вопрос о свадьбе...',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'content': '',
        }