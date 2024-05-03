from django import forms
from .models import Material
import re

# Planer Formular
class TerrassenPlanerForm(forms.Form):
    
    deck_laenge = forms.DecimalField(
        label='Länge (in mm)', 
        initial='2000',
        min_value=10
        )
    
    deck_breite = forms.DecimalField(
        label='Breite (in mm)', 
        initial='2000',
        min_value=10
        )
    
    montageauswahl = forms.ChoiceField(
        choices=[
            ('clips', 'Clips'),
            ('schrauben', 'Schrauben')
        ],
        label="Montageauswahl",
        required=True
        )
    
    verlegemuster = forms.ChoiceField(
        choices=[
            ('', 'Keine Auswahl'),
            ('wilder_verband', 'Wild'),
            ('englischer_verband', 'Englisch'),
        ],
        label="Verlegemuster auswählen",
        required=True
        )
    
    querverbinder = forms.ChoiceField(
        choices=[
            ('ja', 'Ja'),
            ('nein', 'Nein'),
        ],
        label="Querverbinder?",
        initial='nein',
        required=True
        )
    
    unterkonstruktion = forms.ModelChoiceField(
        queryset=Material.objects.filter(material_kategorie__name='Unterkonstruktionen'),
        label="Unterkonstruktion auswählen",
        empty_label=None 
        )
    
    terrassenbelag = forms.ModelChoiceField(
        queryset=Material.objects.filter(material_kategorie__name='Terrassenbelag'),
        label="Terrassenbelag auswählen",
        empty_label=None  
        )

    stellfuss = forms.ModelChoiceField(
        queryset=Material.objects.filter(material_kategorie__name='Stellfuss'),
        label="Stellfuss",
        empty_label="Keine Auswahl",  
        required=False  
        )

    def __init__(self, *args, **kwargs):
        super(TerrassenPlanerForm, self).__init__(*args, **kwargs)
        self.fields['unterkonstruktion'].label_from_instance = self.clean_label
        self.fields['terrassenbelag'].label_from_instance = self.clean_label
        self.fields['stellfuss'].label_from_instance = self.clean_label
        self.fields['montageauswahl'].label_from_instance = self.clean_label
        
    def clean_label(self, obj):
        label = obj.material_name  # Zugriff auf das Feld, das du säubern möchtest
        cleaned_label = re.sub(r'[^\w\s-]', '-', label)
        return cleaned_label

class UploadXLSForm(forms.Form):
    xls_file = forms.FileField(label='XLS File')
    
    