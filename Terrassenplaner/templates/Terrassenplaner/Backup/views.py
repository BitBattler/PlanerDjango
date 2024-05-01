from django.db.models import DecimalField, ExpressionWrapper, F
from django.shortcuts import render
from .forms import TerrassenPlanerForm
from .models import Material, Kategorie
from math import ceil
from decimal import Decimal
from django.shortcuts import render
from .forms import TerrassenPlanerForm
from math import ceil
from decimal import Decimal


def terrassen_planer_view(request):
    if request.method == 'POST':
        form = TerrassenPlanerForm(request.POST)
        if form.is_valid():
                        
            # Formulardaten abrufen
            deck_laenge = form.cleaned_data['deck_laenge'] / 1000
            deck_breite = form.cleaned_data['deck_breite'] / 1000
            unterkonstruktion = form.cleaned_data['unterkonstruktion']
            terrassenbelag = form.cleaned_data['terrassenbelag']
            ausgewaehlte_schrauben = form.cleaned_data['zubehoer']
            deck_flaeche = (deck_laenge * deck_breite )
            
            # Verlegemuster aus dem Formular abrufen
            verlegemuster = form.cleaned_data['verlegemuster']

            # Berechnungen für die Unterkonstruktion
            balkenlaenge = unterkonstruktion.material_laenge  # Balkenlänge aus der ausgewählten Unterstützung abrufen
            balken_abstand = Decimal('0.4')
            gesamt_balken = ceil(deck_breite / balken_abstand) + 2  # +2 für Balken an den Rändern
            gesamt_lfm = gesamt_balken * deck_laenge
            ben_balken_gesamt = ceil(gesamt_lfm / balkenlaenge)
            balken_pro_reihe = ceil(deck_laenge / balkenlaenge)
            
            # Gesamtanzahl der Verbinder
            verbinder_pro_reihe = balken_pro_reihe - 1 if balken_pro_reihe > 1 else 0
            gesamt_verbinder = verbinder_pro_reihe * gesamt_balken

            # Berechnungen für den Terrassenbelag
            terrassenbelag_breite = terrassenbelag.material_breite + Decimal('0.007')
            terrassenbelag_laenge = terrassenbelag.material_laenge
            anzahl_dielen_breite = ceil(deck_breite / terrassenbelag_breite) 
            anzahl_dielen_lfm = (anzahl_dielen_breite * deck_laenge) 
            anzahl_dielen_stk = ceil((anzahl_dielen_lfm / terrassenbelag.material_laenge) * 1000)

            # Berechnungen für die Schrauben
            gesamt_schrauben = {}
            for schraube in ausgewaehlte_schrauben:
                anzahl_schrauben_pro_m2 = Decimal('1') / (terrassenbelag.material_breite + Decimal('0.01')) * Decimal('2') / balken_abstand
                gesamt_schrauben[schraube] = ceil(deck_flaeche * anzahl_dielen_breite * anzahl_schrauben_pro_m2)

            verbinder = Material.objects.filter(material_kategorie__name='Zubehoer', material_name__icontains='verbinder').first()


            context = {
                'form': form,
                'ben_balken_gesamt': ben_balken_gesamt,
                'unterkonstruktion': unterkonstruktion,
                'terrassenbelag': terrassenbelag,
                'anzahl_dielen_stk': anzahl_dielen_stk,
                'deck_flaeche': deck_flaeche,
                'gesamt_schrauben': gesamt_schrauben,
                'gesamt_verbinder': gesamt_verbinder,
            }
            return render(request, 'Terrassenplaner/ergebnis.html', context)
    else:
        form = TerrassenPlanerForm()
    return render(request, 'Terrassenplaner/planer_form.html', {'form': form})

def calculate_material_requirements_englischer_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    # Berechnungen für die Unterkonstruktion für Englischen Verband
    # Füge hier deine Berechnungen für den Englischen Verband hinzu
    pass

def calculate_material_requirements_wilder_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    # Berechnungen für die Unterkonstruktion für Wilder Verband
    # Füge hier deine Berechnungen für den Wilden Verband hinzu
    pass

def material_list(request):
    kategorien = Kategorie.objects.all().prefetch_related('materialien')
    return render(request, 'Terrassenplaner/material_list.html', {'kategorien': kategorien})