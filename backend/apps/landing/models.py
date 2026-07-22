from django.db import models
from django.utils.translation import gettext_lazy as _

class LandingScreenshot(models.Model):
    class KeyChoices(models.TextChoices):
        HOME = 'home', _('Home')
        REFLEXAO = 'reflexao', _('Reflexão do Dia')
        BIBLIA = 'biblia', _('Bíblia')
        NOITE = 'noite', _('Palavra da Noite')

    key = models.CharField(
        max_length=50,
        choices=KeyChoices.choices,
        unique=True,
        help_text=_("Identificador único para buscar a imagem correta no frontend.")
    )
    title = models.CharField(max_length=100, help_text=_("Título interno para organização."))
    image = models.ImageField(upload_to='landing/', help_text=_("Imagem do screenshot."))
    alt_text = models.CharField(max_length=255, blank=True, help_text=_("Texto alternativo para acessibilidade."))
    is_active = models.BooleanField(default=True, help_text=_("Define se a imagem será enviada para o frontend."))
    sort_order = models.IntegerField(default=0, help_text=_("Ordem de exibição (opcional, já que a busca é por key)."))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = _('Screenshot da Landing Page')
        verbose_name_plural = _('Screenshots da Landing Page')

    def __str__(self):
        return f"{self.title} ({self.key})"

class Lead(models.Model):
    email = models.EmailField(unique=True, help_text=_("E-mail do lead."))
    name = models.CharField(max_length=150, blank=True, help_text=_("Nome do lead (opcional)."))
    source = models.CharField(max_length=100, default="Tudo Parece Pesado", help_text=_("Origem da captura ou material entregue."))
    consent_given = models.BooleanField(default=False, help_text=_("Consentimento para receber comunicações."))
    utm_source = models.CharField(max_length=100, blank=True, help_text=_("UTM Source"))
    utm_medium = models.CharField(max_length=100, blank=True, help_text=_("UTM Medium"))
    utm_campaign = models.CharField(max_length=100, blank=True, help_text=_("UTM Campaign"))
    utm_content = models.CharField(max_length=100, blank=True, help_text=_("UTM Content"))
    utm_term = models.CharField(max_length=100, blank=True, help_text=_("UTM Term"))
    brevo_sync_status = models.BooleanField(default=False, help_text=_("Status de sincronização com o Brevo."))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')

    def __str__(self):
        return self.email
