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

# Vorlage Funktion 
def calculate_material_requirements_neutral (deck_laenge, deck_breite, unterkonstruktion, terrassenbelag):
    
    # Unterkonstruktion 
    balken_achsmass = Decimal("0.4")
    balken_stk_breite = Decimal(deck_breite / balken_achsmass ) + 2
    balken_lfm = (balken_stk_breite * deck_laenge)
    ben_balken_gesamt = ceil(balken_lfm / ( unterkonstruktion.material_laenge / 1000))
    
    #print ("UK Länge:",unterkonstruktion.material_laenge, "Balken gesamt:",ben_balken_gesamt, "Balken Stk. Breite:",balken_stk_breite, "Balken Laufmeter:",balken_lfm)
    
    # Terrassenbelag
    dielen_breite = terrassenbelag.material_breite + Decimal('7')
    anzahl_dielen_breite = (deck_laenge / terrassenbelag.material_breite) * 1000
    anzahl_dielen_lfm = ceil(anzahl_dielen_breite * deck_laenge)
    anzahl_dielen = ceil((anzahl_dielen_lfm / terrassenbelag.material_laenge) * 1000)
    
    #print ("Anzahl Dielen Gesamt", anzahl_dielen)
    
    # Querstreben
    querstreben_sprung = 1.1 
    querstreben_gesamt = ceil(float(balken_lfm) / querstreben_sprung)
    querstreben_stk = ceil((querstreben_gesamt * balken_achsmass) / ( unterkonstruktion.material_laenge / 1000))
    
    #print ("Querstreben STK", querstreben_stk)
    
    
    # Verbinder
    verbinder_pro_reihe = ceil(balken_lfm / ( unterkonstruktion.material_laenge / 1000)) - 1 
    verbinder_querstreben = querstreben_gesamt / 4
    gesamt_verbinder = ceil(verbinder_pro_reihe + verbinder_querstreben)
    bohrschrauben = ceil(verbinder_querstreben / 2 )
    #print ("Verbinder", gesamt_verbinder)
    
    # Schrauben
    gesamt_befestigungsclip = ceil(deck_laenge * deck_breite * 17)
    gesamt_schrauben = ceil(deck_laenge * deck_breite * 17 * 2)
        
    #print ("Befestigunsgclip", gesamt_befestigungsclip, "gesamt_schrauben", gesamt_schrauben)

    return ben_balken_gesamt, anzahl_dielen, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip

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
            clip = 0

            # Verlegemuster berechnung
            if verlegemuster == 'neutral':
                ben_balken_gesamt, anzahl_dielen, gesamt_verbinder, gesamt_schrauben, gesamt_befestigungsclip = calculate_material_requirements_neutral(deck_laenge, deck_breite, unterkonstruktion, terrassenbelag)
                
                if montageauswahl == 'clips':
                    gesamt_clip = gesamt_befestigungsclip
                else:
                    schrauben = gesamt_schrauben
                    
                # Querverbinder If Abfrage
                if querverbinder == 'ja':
                    pass
                else:
                    pass
            
            
        
            else: 
                pass
            

            # Filter    
            verbinder = Material.objects.filter(material_kategorie__name='Zubehoer', material_name__icontains='Verbinder')
            schrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Schraube').exclude(material_name__icontains='Bohrschraube')
            bohrschrauben = Material.objects.filter(material_kategorie__name='Schrauben', material_name__icontains='Bohrschrauben').first()
            befestigungsclips = Material.objects.filter(material_kategorie__name='Clips', material_name__icontains='Befestigungsclip')

            context = {
                'form': form,
                'deck_laenge_mm': deck_laenge_mm,
                'deck_breite_mm': deck_breite_mm,
                'verlegemuster': verlegemuster,
                'ben_balken_gesamt': ben_balken_gesamt,
                'unterkonstruktion': unterkonstruktion,
                'terrassenbelag': terrassenbelag,
                'anzahl_dielen': anzahl_dielen,
                'schrauben': schrauben,
                'bohrschrauben': bohrschrauben,
                'bohrschrauben_gesamt': bohrschrauben_gesamt,
                'schrauben': schrauben,
                'montageauswahl': montageauswahl,
                'befestigungsclips': befestigungsclips,
                'clip': clip, 
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

            mask_path = os.path.join(settings.STATIC_ROOT, 'xls/Mask_Material.xlsx')
            
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

#xlsx Downloader 
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

# Login / Logout
def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "Du bist angemeldet.")
                # Redirect to add_xls view upon successful login
                return redirect('add_xls')
            else:
                messages.error(request, "Fehler bei der Anmeldung. Versuche es erneut.")
                # Render login page with error message
                return render(request, 'login', {"form": form})
        else:
            messages.error(request, "Fehler die Seite ist nicht verfügbar.")
            return render(request, 'Terrassenplaner/planer_form.html', {})
    
    else:
        # Render login page for GET request
        return render(request, 'Terrassenplaner/login.html', {})
def logout_user(request):
    logout(request)
    return redirect('planer_view')