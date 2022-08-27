from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        help_texts = {
            'text': 'Здесь пишут текст поста',
            'group': 'Выберите группу, к которой относится Ваш пост',
        }
        model = Post
        fields = (
            'text',
            'group'
        )
