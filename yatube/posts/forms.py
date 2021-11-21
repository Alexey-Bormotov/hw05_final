from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError(
                'Пост не должен быть пустым!',
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError(
                'Комментарий не должен быть пустым!',
            )
        return data
