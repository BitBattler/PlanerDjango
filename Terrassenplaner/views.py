from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, F
from django.shortcuts import render
from .forms import TerrassenPlanerForm, UploadXLSForm
from .models import Material, Kategorie
from math import ceil
from decimal import Decimal
import pandas as pd
import io
import os
import xlsxwriter
from django.http import HttpResponse

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

            verbinder = Material.objects.filter(material_kategorie__name='Zubehoer', material_name__icontains='Verbinder')
            schrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Schraube').exclude(material_name__icontains='Bohrschraube')
            bohrschrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Bohrschrauben').first()
            befestigungsclips = Material.objects.filter(material_kategorie__name='Clips', material_name__icontains='Befestigungsclip')
            print("Anzahl der Befestigungsclips:", befestigungsclips.count())
            print("Inhalt von befestigungsclips:", befestigungsclips)

            
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
                'montageauswahl': montageauswahl,
                'befestigungsclips': befestigungsclips,
                'gesamt_befestigungsclip': gesamt_befestigungsclip, 
                              
                # Verbinder
                'verbinder': verbinder,
                'gesamt_verbinder': gesamt_verbinder,
                
                # Querstreben
                'querverbinder': querverbinder,
                'querstreben_einzel': querstreben_einzel,
                'querstreben_gesamt': querstreben_gesamt
            }
            return render(request, 'Terrassenplaner/ergebnis.html', context)
    else:
        form = TerrassenPlanerForm()
    return render(request, 'Terrassenplaner/planer_form.html', {'form': form})

def add_xls(request):
    if request.method == 'POST':
        form = UploadXLSForm(request.POST, request.FILES)
        if form.is_valid():
            # Hochgeladene Datei laden
            xls_file = request.FILES['xls_file']
            df_uploaded = pd.read_excel(xls_file)
            
            # Liste der auszuschließenden Begriffe
            exclude_terms = [
                'Diversartikel', 
                'megawood', 
                'Pfostenanker', 
                'Osmo', 
                'Element',
                'öle',
                'Entgrauer',
                'Pfähle',
                'Palisaden',
                'Latten',
                'Schwellen',
                'bretter',
                'Zaun',
                'Stämme',
                'Muster',
                'Fun-Deck',
                'Stirn',
                'Montage',
                'Bangkirai',
                'Fibertex',
                'Bohrer',
                'Kombi',
                ]

            # Filtern der Zeilen in verschiedenen Spalten basierend auf Ausschlussbegriffen
            for term in exclude_terms:
                df_uploaded = df_uploaded[~df_uploaded['Beschreibung'].str.contains(term, case=False, na=False)]
                df_uploaded = df_uploaded[~df_uploaded['Beschreibung 2'].str.contains(term, case=False, na=False)]

            # Masken-Datei (Vorlagendatei) laden
            mask_path = os.path.join(settings.STATIC_ROOT, 'Mask_Material.xlsx')
            df_mask = pd.read_excel(mask_path)

            # Spaltenzuordnung gemäß der Vorlagendatei
            column_mapping = {
                'Nr.': 'artikelnummer',
                'Beschreibung 2': 'material_name',
                'Länge (Basis)': 'material_laenge',
                'Breite (Basis)': 'material_breite',
                'Stärke (Basis)': 'material_hoehe',
                'Menge pro Paket': 'verpackungseinheit',
            }

            # Kopieren der Werte aus der hochgeladenen Datei entsprechend des Mappings
            for original_col, new_col in column_mapping.items():
                if original_col in df_uploaded.columns and new_col in df_mask.columns:
                    df_mask[new_col] = df_uploaded[original_col]

            # Initialisieren der Kategorie-Spalte mit einem Standardwert (z.B. 0)
            df_mask['material_kategorie'] = 0

            # Kategorien (zur Referenz im Kommentar):
            # 1: ['Unterkonstruktion', 'Untergrund'],
            # 2: ['Belag', 'Platten'],
            # 3: ['Zubehör', 'Extras'],
            # 4: ['Schraube', 'Nägel'],
            # 5: ['Clip', 'Halterung'],
            # 6: ['Stellfuss', 'Verstellfuß']

            # Erstellen der herunterladbaren Datei
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_mask.to_excel(writer, index=False)

            output.seek(0)

            # Erstellen der HttpResponse für die herunterladbare Datei
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=converted.xlsx'
            return response

    else:
        form = UploadXLSForm()
    return render(request, 'Terrassenplaner/add_xls.html', {'form': form})

# Material Liste
def material_list(request):
    kategorien = Kategorie.objects.all().prefetch_related('materialien')
    return render(request, 'Terrassenplaner/material_list.html', {'kategorien': kategorien})

