from django import forms

from blog.models import Article
from sender.forms import FormStyleMixin


class ArticleModelForm(FormStyleMixin, forms.ModelForm):

    class Meta:
        model = Article
        fields = (
            "title",
            "preview",
            "content",
            "is_published",
        )
