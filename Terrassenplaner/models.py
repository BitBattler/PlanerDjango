from django.db import models
from django.core.validators import MinValueValidator

class Kategorie(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Material(models.Model):
    material_name = models.CharField(max_length=100, db_index=True)
    material_laenge = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0.01)], null=True, blank=True)
    material_breite = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0.01)], null=True, blank=True)
    material_hoehe = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0.01)], null=True, blank=True)
    material_kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, related_name='materialien')
    artikelnummer = models.CharField(max_length=50, unique=True, null=True, blank=True)
    verpackungseinheit = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.material_name} - {self.material_laenge}m x {self.material_breite}m x {self.material_hoehe}m "

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materialien'
        ordering = ['material_name']

