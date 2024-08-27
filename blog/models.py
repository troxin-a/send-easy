from django.db import models

NULLABLE = {"blank": True, "null": True}

class Article(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=150)
    slug = models.SlugField(verbose_name="slug", max_length=250, unique=True)
    content = models.TextField(verbose_name="Содержимое статьи", **NULLABLE)
    preview = models.ImageField(verbose_name="Превью", upload_to="blog/", **NULLABLE)
    views_count = models.IntegerField(verbose_name="Количество просмотров", default=0, editable=False)
    is_published = models.BooleanField(verbose_name="Опубликован", default=False)
    public_date = models.DateField(verbose_name="Дата публикации", auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "статью"
        verbose_name_plural = "Статьи"
        ordering = ("-id",)
