from django.db import models
from django.utils import timezone

# base stract model for all models that have a publish state
class BasePublishedModel(models.Model):
    class PublishStateOptions(models.TextChoices):
        PUBLISHED = 'PU', 'PUBLICADO'
        DRAFT = 'BR', 'BORRADOR'
        PRIVATE = 'PR', 'PRIVADO'

    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    published_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)

    class Meta:
        abstract = True
        ordering = ['-updated', '-timestamp']

    def save(self, *args, **kwargs):
        if self.state_is_published and self.published_timestamp is None:
            self.published_timestamp = timezone.now()
        elif not self.state_is_published:
            self.published_timestamp = None
        super().save(*args, **kwargs)

    @property
    def state_is_published(self):
        return self.state == self.PublishStateOptions.PUBLISHED

    def is_published(self):
        published_timestamp = self.published_timestamp
        return self.state_is_published and published_timestamp < timezone.now()
