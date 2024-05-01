from django.db.models import DecimalField, ExpressionWrapper, F
from django.shortcuts import render
from .forms import TerrassenPlanerForm
from .models import Material, Kategorie
from math import ceil
from decimal import Decimal

# Wilder Verband
def calculate_material_requirements_wilder_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    
    # Berechnungen für die Unterkonstruktion für Wilden Verband
    balkenlaenge = Decimal(unterkonstruktion.material_laenge)
    balken_abstand = Decimal('0.4')
    gesamt_balken = ceil(deck_breite / balken_abstand) + 2 
    gesamt_lfm = gesamt_balken * deck_laenge
    ben_balken_gesamt = ceil(gesamt_lfm / balkenlaenge)
    balken_pro_reihe = ceil(deck_laenge / balkenlaenge)
    deck_flaeche = deck_laenge * deck_breite

    verbinder_pro_reihe = balken_pro_reihe - 1 if balken_pro_reihe > 1 else 0
    gesamt_verbinder = verbinder_pro_reihe * gesamt_balken

    terrassenbelag_breite = Decimal(terrassenbelag.material_breite) + Decimal('0.007') #Fugenabstand Clip 7mm
    anzahl_dielen_breite = (deck_breite / terrassenbelag_breite)
    anzahl_dielen_lfm = anzahl_dielen_breite * deck_laenge
    anzahl_dielen_stk = ceil(anzahl_dielen_lfm / Decimal(terrassenbelag.material_laenge))
    gesamt_schrauben = 0
    gesamt_befestigungsclip = 0
    

    return ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip

# Englischer Verband
def calculate_material_requirements_englischer_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    
    # Berechnungen für die Unterkonstruktion
    balkenlaenge = Decimal(unterkonstruktion.material_laenge)
    balken_abstand = Decimal('0.4')
    gesamt_balken = ceil(deck_breite / balken_abstand) + 2 
    gesamt_lfm = gesamt_balken * deck_laenge
    ben_balken_gesamt = ceil(gesamt_lfm / balkenlaenge)
    balken_pro_reihe = ceil(deck_laenge / balkenlaenge)
    deck_flaeche = deck_laenge * deck_breite
    gesamt_schrauben = 0
    gesamt_befestigungsclip = 0

    verbinder_pro_reihe = balken_pro_reihe - 1 if balken_pro_reihe > 1 else 0
    gesamt_verbinder = verbinder_pro_reihe * gesamt_balken

    terrassenbelag_breite = Decimal(terrassenbelag.material_breite) + Decimal('0.007') #Fugenabstand Clip 7mm
    anzahl_dielen_breite = (deck_breite / terrassenbelag_breite)
    anzahl_dielen_lfm = anzahl_dielen_breite * deck_laenge
    anzahl_dielen_stk = ceil(anzahl_dielen_lfm / Decimal(terrassenbelag.material_laenge))
    
    # Mehr Material hinzufügen (10-15%) für Englisch Verband
    ben_balken_gesamt = ceil(ben_balken_gesamt * Decimal('1.15'))  # 15% mehr Balken für Englisch
    anzahl_dielen_stk = ceil(anzahl_dielen_stk * Decimal('1.15'))  # 15% mehr Dielen für Englisch
    
    return ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip
    
# Querverbinder 
def calculate_querverbinder(deck_laenge, ben_balken_gesamt):
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    #print("Querstreben gesamt:", querstreben_gesamt)
    return querstreben_gesamt
    
# Bohrschrauben
def calculate_bohrschrauben(deck_laenge, ben_balken_gesamt):
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    bohrschrauben_gesamt = ceil(querstreben_einzel / 2)
    
    #print("Bohrschrauben gesamt:", bohrschrauben_gesamt)
    return bohrschrauben_gesamt

# Terrassen Planer View
def terrassen_planer_view(request):
    if request.method == 'POST':
        form = TerrassenPlanerForm(request.POST)
        if form.is_valid():
            deck_laenge = form.cleaned_data['deck_laenge'] / Decimal('1000')  # Konvertiere in Meter
            deck_breite = form.cleaned_data['deck_breite'] / Decimal('1000')  # Konvertiere in Meter
            deck_laenge_mm = form.cleaned_data['deck_laenge']  # Angenommen, die Eingabe ist bereits in Millimeter
            deck_breite_mm = form.cleaned_data['deck_breite']  # Angenommen, die Eingabe ist bereits in Millimeter
            unterkonstruktion = form.cleaned_data['unterkonstruktion']
            terrassenbelag = form.cleaned_data['terrassenbelag']
            

            verlegemuster = form.cleaned_data['verlegemuster']
            querverbinder = form.cleaned_data['querverbinder']
            montageauswahl = form.cleaned_data['montageauswahl']
            querstreben_einzel = 0
            querstreben_gesamt = 0  
            bohrschrauben_gesamt = 0 
            befestigungsclip = 0

            # Verlegemuster berechnung
            if verlegemuster == 'wilder_verband':
                ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip = calculate_material_requirements_wilder_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag)
                
                if montageauswahl == 'clips':
                    gesamt_schrauben = 0
                    gesamt_befestigungsclip = ceil(deck_laenge * deck_breite * 17)
                    #print("Befestigungsclip gesamt:", gesamt_befestigungsclip)
                else:
                    gesamt_befestigungsclip = 0
                    gesamt_schrauben = ceil(deck_laenge * deck_breite * 17 * 2)
                    #print("Schrauben gesamt:", gesamt_schrauben)  
                    
                # Querverbinder If Abfrage
                if querverbinder == 'ja':
                    querstreben_gesamt = calculate_querverbinder(deck_laenge, ben_balken_gesamt)
                    bohrschrauben_gesamt = calculate_bohrschrauben(deck_laenge, ben_balken_gesamt)
                else:
                    querstreben_gesamt = 0
                    querstreben_einzel = 0 
                    bohrschrauben_gesamt = 0
            
            elif verlegemuster == 'englischer_verband':
                ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip = calculate_material_requirements_englischer_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag)
                
                if montageauswahl == 'clips':
                    gesamt_schrauben = 0
                    gesamt_befestigungsclip = ceil(deck_laenge * deck_breite * 17)
                    print("Befestigungsclip gesamt:", gesamt_befestigungsclip)
                else:
                    gesamt_befestigungsclip = 0
                    gesamt_schrauben = ceil(deck_laenge * deck_breite * 17 * 2)
                    print("Schrauben gesamt:", gesamt_schrauben) 
                    
                # Querverbinder If Abfrage
                if querverbinder == 'ja':
                    querstreben_gesamt = calculate_querverbinder(deck_laenge, ben_balken_gesamt)
                    bohrschrauben_gesamt = calculate_bohrschrauben(deck_laenge, ben_balken_gesamt)
                else:
                    querstreben_gesamt = 0
                    querstreben_einzel = 0 
                    bohrschrauben_gesamt = 0

            verbinder = Material.objects.filter(material_kategorie__name='Zubehoer', material_name__icontains='verbinder').first()
            schrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='A2').first()
            bohrschrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Bohrschrauben').first()
            befestigunsclip = Material.objects.filter(material_kategorie__name='Befestigungsclip', material_name__icontains='Befestigungsclip').first()

            context = {
                
                'form': form,
                
                # Deck Variabeln
                'deck_laenge_mm': deck_laenge_mm,
                'deck_breite_mm': deck_breite_mm,
                'verlegemuster': verlegemuster,
                
                # Deckberechnung
                'ben_balken_gesamt': ben_balken_gesamt,
                'unterkonstruktion': unterkonstruktion,
                'terrassenbelag': terrassenbelag,
                'anzahl_dielen_stk': anzahl_dielen_stk,
                
                # Befestigung 
                'schrauben': schrauben,
                'bohrschrauben': bohrschrauben,
                'bohrschrauben_gesamt': bohrschrauben_gesamt,
                'gesamt_schrauben': gesamt_schrauben,
                'befestigungsclip': befestigungsclip,
                'gesamt_befestigungsclip': gesamt_befestigungsclip,  
                              
                # Verbinder
                'verbinder': verbinder,
                'gesamt_verbinder': gesamt_verbinder,
                
                # Querstreben
                'querverbinder': querverbinder,
                'querstreben_einzel': querstreben_einzel,
                'querstreben_gesamt': querstreben_gesamt
            }
            print("Befestigungsclip gesamt:", gesamt_befestigungsclip)
            return render(request, 'Terrassenplaner/ergebnis.html', context)
    else:
        form = TerrassenPlanerForm()
    return render(request, 'Terrassenplaner/planer_form.html', {'form': form})

# Material Liste
def material_list(request):
    kategorien = Kategorie.objects.all().prefetch_related('materialien')
    return render(request, 'Terrassenplaner/material_list.html', {'kategorien': kategorien})

