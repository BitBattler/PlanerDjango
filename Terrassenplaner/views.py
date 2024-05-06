import io
import os
import xlsxwriter
import tempfile
import pandas as pd
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, F
from django.shortcuts import render, redirect
from .forms import TerrassenPlanerForm, UploadXLSForm, LoginForm
from .models import Material, Kategorie
from math import ceil
from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponse

# Wilder Verband
def calculate_material_requirements_wilder_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    
    # Berechnungen für die Unterkonstruktion für Wilden Verband
    balkenlaenge = unterkonstruktion.material_laenge
    balken_abstand = Decimal('0.4')  # in Meter
    gesamt_balken = ceil(deck_breite / balken_abstand) + 2 
    gesamt_lfm = gesamt_balken * deck_laenge
    ben_balken_gesamt = ceil(gesamt_lfm / balkenlaenge)
    balken_pro_reihe = ceil(deck_laenge / balkenlaenge)
    deck_flaeche = deck_laenge * deck_breite

    verbinder_pro_reihe = balken_pro_reihe - 1 if balken_pro_reihe > 1 else 0
    gesamt_verbinder = verbinder_pro_reihe * gesamt_balken

    terrassenbelag_breite = terrassenbelag.material_breite + Decimal('0.007') # Fugenabstand Clip 7mm
    anzahl_dielen_breite = (deck_breite / terrassenbelag_breite)
    anzahl_dielen_lfm = anzahl_dielen_breite * deck_laenge
    anzahl_dielen_stk = ceil(anzahl_dielen_lfm / terrassenbelag.material_laenge)
    gesamt_schrauben = 0
    gesamt_befestigungsclip = 0
    
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    bohrschrauben_gesamt = ceil(querstreben_einzel / 2)
    
    return ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip, querstreben_gesamt, bohrschrauben_gesamt

# Englischer Verband
def calculate_material_requirements_englischer_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    
    # Berechnungen für die Unterkonstruktion
    balkenlaenge = unterkonstruktion.material_laenge
    balken_abstand = Decimal('0.4')  # in Meter
    gesamt_balken = ceil(deck_breite / balken_abstand) + 2 
    gesamt_lfm = gesamt_balken * deck_laenge
    ben_balken_gesamt = ceil(gesamt_lfm / balkenlaenge)
    balken_pro_reihe = ceil(deck_laenge / balkenlaenge)
    deck_flaeche = deck_laenge * deck_breite
    gesamt_schrauben = 0
    gesamt_befestigungsclip = 0

    verbinder_pro_reihe = balken_pro_reihe - 1 if balken_pro_reihe > 1 else 0
    gesamt_verbinder = verbinder_pro_reihe * gesamt_balken

    terrassenbelag_breite = terrassenbelag.material_breite + Decimal('0.007') # Fugenabstand Clip 7mm
    anzahl_dielen_breite = (deck_breite / terrassenbelag_breite)
    anzahl_dielen_lfm = anzahl_dielen_breite * deck_laenge
    anzahl_dielen_stk = ceil(anzahl_dielen_lfm / terrassenbelag.material_laenge)
    
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    achsmass_querstreben = Decimal('1.1')  # in Meter
    querstreben_pro_laenge = ceil(deck_laenge / achsmass_querstreben) + 2
    querstreben_einzel = querstreben_pro_laenge * ben_balken_gesamt / 4
    querstreben_gesamt = round(querstreben_einzel)
    
    bohrschrauben_gesamt = ceil(querstreben_einzel / 2)
    
    # Mehr Material hinzufügen (10-15%) für Englisch Verband
    ben_balken_gesamt = ceil(ben_balken_gesamt * Decimal('1.15'))  # 15% mehr Balken für Englisch
    anzahl_dielen_stk = ceil(anzahl_dielen_stk * Decimal('1.15'))  # 15% mehr Dielen für Englisch
    
    return ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip, querstreben_gesamt, bohrschrauben_gesamt
    
    

# Terrassen Planer View
def terrassen_planer_view(request):
    if request.method == 'POST':
        form = TerrassenPlanerForm(request.POST)
        if form.is_valid():
                
            deck_laenge_mm = form.cleaned_data['deck_laenge']  # Angenommen, die Eingabe ist bereits in Millimeter
            deck_breite_mm = form.cleaned_data['deck_breite']  # Angenommen, die Eingabe ist bereits in Millimeter
            
            deck_laenge = deck_laenge_mm / Decimal('1000')  # Konvertiere in Meter
            deck_breite = deck_breite_mm / Decimal('1000')  # Konvertiere in Meter
            
            unterkonstruktion = form.cleaned_data['unterkonstruktion']
            terrassenbelag = form.cleaned_data['terrassenbelag']
            
            verlegemuster = form.cleaned_data['verlegemuster']
            querverbinder = form.cleaned_data['querverbinder']
            montageauswahl = form.cleaned_data['montageauswahl']
            
            querstreben_einzel = 0
            querstreben_gesamt = 0  
            bohrschrauben_gesamt = 0 
            befestigungsclip = 0
            ben_balken_gesamt = 0  
            anzahl_dielen_stk = 0
            gesamt_schrauben = 0
            gesamt_befestigungsclip = 0
            gesamt_verbinder = 0
            

            # Verlegemuster berechnung
            if verlegemuster == 'wilder_verband':
                ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip, querstreben_gesamt, bohrschrauben_gesamt = calculate_material_requirements_wilder_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag)
                
                if montageauswahl == 'clips':
                    gesamt_schrauben = 0
                    gesamt_befestigungsclip = ceil(deck_laenge * deck_breite * 17)
                else:
                    gesamt_befestigungsclip = 0
                    gesamt_schrauben = ceil(deck_laenge * deck_breite * 17 * 2)
                        
            elif verlegemuster == 'englischer_verband':
                ben_balken_gesamt, anzahl_dielen_stk, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip, querstreben_gesamt, bohrschrauben_gesamt = calculate_material_requirements_englischer_verband(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag)
                
                if montageauswahl == 'clips':
                    gesamt_schrauben = 0
                    gesamt_befestigungsclip = ceil(deck_laenge * deck_breite * 17)
                else:
                    gesamt_befestigungsclip = 0
                    gesamt_schrauben = ceil(deck_laenge * deck_breite * 17 * 2)
                    

            verbinder = Material.objects.filter(material_kategorie__name='Zubehoer', material_name__icontains='Verbinder')
            schrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Schraube').exclude(material_name__icontains='Bohrschraube')
            bohrschrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Bohrschrauben silber 5 x 70').first()
            befestigungsclips = Material.objects.filter(material_kategorie__name='Clips', material_name__icontains='Befestigungsclip')

            context = {
                'form': form,
                'deck_laenge_mm': deck_laenge_mm,
                'deck_breite_mm': deck_breite_mm,
                'verlegemuster': verlegemuster,
                'ben_balken_gesamt': ben_balken_gesamt,
                'unterkonstruktion': unterkonstruktion,
                'terrassenbelag': terrassenbelag,
                'anzahl_dielen_stk': anzahl_dielen_stk,
                'schrauben': schrauben,
                'bohrschrauben': bohrschrauben,
                'bohrschrauben_gesamt': bohrschrauben_gesamt,
                'gesamt_schrauben': gesamt_schrauben,
                'montageauswahl': montageauswahl,
                'befestigungsclips': befestigungsclips,
                'gesamt_befestigungsclip': gesamt_befestigungsclip, 
                'verbinder': verbinder,
                'gesamt_verbinder': gesamt_verbinder,
                'querverbinder': querverbinder,
                'querstreben_einzel': querstreben_einzel,
                'querstreben_gesamt': querstreben_gesamt
            }
            return render(request, 'Terrassenplaner/ergebnis.html', context)
    else:
        form = TerrassenPlanerForm()
    return render(request, 'Terrassenplaner/planer_form.html', {'form': form})

# xlsx Converter
def add_xls(request):
    if request.method == 'POST':
        form = UploadXLSForm(request.POST, request.FILES)
        if form.is_valid():
            xls_file = request.FILES['xls_file']
            df_uploaded = pd.read_excel(xls_file)

            exclude_terms = [
                'Diversartikel', 'megawood', 'Pfostenanker', 'Osmo', 'Element', 'öle', 
                'Entgrauer', 'Pfähle', 'Palisaden', 'Latten', 'Schwellen', 'bretter', 
                'Zaun', 'Stämme', 'Muster', 'Fun-Deck', 'Stirn', 'Montage', 'Bangkirai', 
                'Fibertex', 'Bohrer', 'Kombi'
            ]

            # Entfernen von Zeilen, die die unerwünschten Begriffe in den Spalten 'Beschreibung' und 'Beschreibung 2' enthalten
            for term in exclude_terms:
                df_uploaded = df_uploaded[~df_uploaded['Beschreibung'].str.contains(term, case=False, na=False)]
                df_uploaded = df_uploaded[~df_uploaded['Beschreibung 2'].str.contains(term, case=False, na=False)]

            mask_path = os.path.join(settings.STATIC_ROOT, 'Mask_Material.xlsx')
            df_mask = pd.read_excel(mask_path)

            column_mapping = {
                'Nr.': 'artikelnummer',
                'Beschreibung 2': 'material_name',
                'Länge (Basis)': 'material_laenge',
                'Breite (Basis)': 'material_breite',
                'Stärke (Basis)': 'material_hoehe',
                'Menge pro Paket': 'verpackungseinheit',
            }

            # Umbenennen und Reihenfolge der Spalten entsprechend der Maskendatei
            df_uploaded = df_uploaded.rename(columns=column_mapping)

            # Überprüfen, ob die benötigten Spalten im DataFrame vorhanden sind
            required_columns = ['artikelnummer', 'material_name', 'material_laenge', 'material_breite', 'material_hoehe', 'verpackungseinheit']
            if not all(col in df_uploaded.columns for col in required_columns):
                return HttpResponse("Fehler: Nicht alle benötigten Spalten sind im hochgeladenen Excel vorhanden.")

            # Auswahl und Reihenfolge der Spalten basierend auf der Maskendatei
            df_uploaded = df_uploaded[required_columns]

            temp_dir = settings.CUSTOM_TEMP_DIR
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = os.path.join(temp_dir, 'temp_converted.xlsx')
            df_uploaded.to_excel(temp_file_path, index=False)

            request.session['temp_file_path'] = temp_file_path
            
            return render(request, 'Terrassenplaner/categorize_xls.html', {
                'articles': df_uploaded.to_dict('records')
            })

    else:
        form = UploadXLSForm()
    return render(request, 'Terrassenplaner/add_xls.html', {'form': form})

#xlsx downloader 
def finalize_xls(request):
    if request.method == 'POST':
        temp_dir = settings.CUSTOM_TEMP_DIR
        temp_file_path = os.path.join(temp_dir, 'temp_converted.xlsx')
        
        if not os.path.exists(temp_file_path):
            return HttpResponse("Fehler: Temporäre Datei nicht gefunden.", status=404)

        # Kategorien aus dem Formular aktualisieren
        df = pd.read_excel(temp_file_path)
        for key, value in request.POST.items():
            if key.startswith('category_'):
                index = int(key.split('_')[-1]) - 1  # Konvertieren 'category_1' zu 0 (Index)
                # Annahme: Ihre Excel-Datei hat eine Spalte 'Kategorie'
                df.at[index, 'material_kategorie'] = value

        # Speichern der aktualisierten Excel-Datei in einem BytesIO-Stream
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Setzen des Dateinamens und des Content-Types für den Download
        response = HttpResponse(
            output, 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="updated_file.xlsx"'

        # Aufräumen: Löschen der temporären Datei
        os.remove(temp_file_path)

        return response
    else:
        # Wenn keine POST-Anfrage, umleiten zum Formular
        return redirect('planer_view')    

# Material Liste
def material_list(request):
    kategorien = Kategorie.objects.all().prefetch_related('materialien')
    return render(request, 'Terrassenplaner/material_list.html', {'kategorien': kategorien})

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                #messages.success(request, "Du bist angemeldet.")
                # Redirect to add_xls view upon successful login
                return redirect('/')
            else:
                #messages.error(request, "Fehler bei der Anmeldung. Versuche es erneut.")
                # Render login page with error message
                return render(request, 'login', {"form": form})
        else:
            #messages.error(request, "Fehler die Seite ist nicht verfügbar.")
            return render(request, 'Terrassenplaner/planer_form.html', {})
    
    else:
        # Render login page for GET request
        return render(request, 'Terrassenplaner/login.html', {})

def logout_user(request):
    logout(request)
    return redirect('planer_view')

def messages(request):
    return redirect('messages')