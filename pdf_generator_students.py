# pdf_generator_students.py - Version avec design professionnel, thèmes colorés et support logo SANS TABLEAU
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY, TA_LEFT
import os
import requests
from io import BytesIO

# Thèmes de couleurs disponibles
THEMES_COULEURS = {
    'bleu': {
        'principale': colors.HexColor('#2c3e50'),
        'secondaire': colors.HexColor('#34495e'), 
        'accent': colors.HexColor('#3498db'),
        'fond': colors.HexColor('#ecf0f1'),
        'header_bg': colors.HexColor('#2d3436')
    },
    'vert': {
        'principale': colors.HexColor('#27ae60'),
        'secondaire': colors.HexColor('#2d5016'), 
        'accent': colors.HexColor('#58d68d'),
        'fond': colors.HexColor('#e8f8f5'),
        'header_bg': colors.HexColor('#1e8449')
    },
    'rouge': {
        'principale': colors.HexColor('#e74c3c'),
        'secondaire': colors.HexColor('#922b21'), 
        'accent': colors.HexColor('#f1948a'),
        'fond': colors.HexColor('#fadbd8'),
        'header_bg': colors.HexColor('#c0392b')
    },
    'violet': {
        'principale': colors.HexColor('#9b59b6'),
        'secondaire': colors.HexColor('#6c3483'), 
        'accent': colors.HexColor('#d7bde2'),
        'fond': colors.HexColor('#f4ecf7'),
        'header_bg': colors.HexColor('#8e44ad')
    },
    'orange': {
        'principale': colors.HexColor('#e67e22'),
        'secondaire': colors.HexColor('#a04000'), 
        'accent': colors.HexColor('#f5b041'),
        'fond': colors.HexColor('#f8c471'),
        'header_bg': colors.HexColor('#d35400')
    }
}

class CustomCanvas(canvas.Canvas):
    """Canvas personnalisé pour ajouter le footer automatiquement"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.company_info = {}
        self.theme = 'bleu'
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self.draw_footer(idx + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_num, total_pages):
        theme_colors = THEMES_COULEURS[self.theme]
        self.saveState()
        
        # Ligne de séparation
        self.setStrokeColor(theme_colors['accent'])
        self.setLineWidth(1)
        self.line(2*cm, 2.5*cm, A4[0] - 2*cm, 2.5*cm)
        
        # Informations de l'entreprise
        self.setFont("Helvetica", 8)
        self.setFillColor(theme_colors['principale'])
        
        y_pos = 2*cm
        company_name = self.company_info.get('nom', 'Votre Entreprise')
        self.drawString(2*cm, y_pos, f"{company_name}")
        
        # Numéro de page à droite
        self.drawRightString(A4[0] - 2*cm, y_pos, f"Page {page_num}/{total_pages}")
        
        self.restoreState()

def download_logo(url_logo):
    """Télécharge le logo depuis une URL"""
    try:
        response = requests.get(url_logo, timeout=10)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None

def create_header_with_logo(company_info, theme='bleu'):
    """Crée l'en-tête avec logo sans tableau"""
    theme_colors = THEMES_COULEURS[theme]
    elements = []
    
    # Style pour l'en-tête
    header_style = ParagraphStyle(
        'HeaderStyle',
        fontSize=16,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=3*mm
    )
    
    # Style pour les informations de l'entreprise
    company_style = ParagraphStyle(
        'CompanyStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=12
    )
    
    # Gestion du logo
    logo_element = None
    if company_info.get('logo_url'):
        logo_data = download_logo(company_info['logo_url'])
        if logo_data:
            logo_element = Image(logo_data, width=3*cm, height=2*cm)
    elif company_info.get('logo_path') and os.path.exists(company_info['logo_path']):
        logo_element = Image(company_info['logo_path'], width=3*cm, height=2*cm)
    
    if logo_element:
        # Logo et informations côte à côte (sans tableau)
        elements.append(Paragraph(f"<b>{company_info.get('nom', 'Votre Entreprise')}</b>", header_style))
        elements.append(logo_element)
        elements.append(Spacer(1, 5*mm))
    else:
        # Juste le nom de l'entreprise
        elements.append(Paragraph(f"<b>{company_info.get('nom', 'Votre Entreprise')}</b>", header_style))
    
    # Informations de l'entreprise en lignes simples
    info_lines = []
    if company_info.get('adresse'):
        info_lines.append(company_info['adresse'])
    if company_info.get('ville'):
        info_lines.append(f"{company_info.get('code_postal', '')} {company_info['ville']}")
    if company_info.get('telephone'):
        info_lines.append(f"Tél: {company_info['telephone']}")
    if company_info.get('email'):
        info_lines.append(f"Email: {company_info['email']}")
    
    for line in info_lines:
        elements.append(Paragraph(line, company_style))
    
    elements.append(Spacer(1, 10*mm))
    return elements

def create_document_info_lines(devis_data, theme='bleu'):
    """Crée les informations du document en lignes simples"""
    theme_colors = THEMES_COULEURS[theme]
    elements = []
    
    # Styles
    label_style = ParagraphStyle(
        'LabelStyle',
        fontSize=10,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=2*mm
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=5*mm
    )
    
    # Numéro de devis
    elements.append(Paragraph("Numéro de devis", label_style))
    elements.append(Paragraph(devis_data.get('numero', ''), value_style))
    
    # Date d'émission
    elements.append(Paragraph("Date d'émission", label_style))
    elements.append(Paragraph(devis_data.get('date_emission', ''), value_style))
    
    # Date d'expiration
    elements.append(Paragraph("Date d'expiration", label_style))
    elements.append(Paragraph(devis_data.get('date_expiration', ''), value_style))
    
    elements.append(Spacer(1, 10*mm))
    return elements

def create_client_info_lines(client_info, theme='bleu'):
    """Crée les informations client en lignes simples"""
    theme_colors = THEMES_COULEURS[theme]
    elements = []
    
    # Style pour le titre
    title_style = ParagraphStyle(
        'ClientTitleStyle',
        fontSize=12,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5*mm
    )
    
    # Style pour les informations
    info_style = ParagraphStyle(
        'ClientInfoStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=12
    )
    
    elements.append(Paragraph("Facturé à :", title_style))
    
    # Informations client en lignes simples
    if client_info.get('nom'):
        elements.append(Paragraph(f"<b>{client_info['nom']}</b>", info_style))
    if client_info.get('adresse'):
        elements.append(Paragraph(client_info['adresse'], info_style))
    if client_info.get('ville'):
        ville_line = f"{client_info.get('code_postal', '')} {client_info['ville']}"
        elements.append(Paragraph(ville_line, info_style))
    if client_info.get('telephone'):
        elements.append(Paragraph(f"Tél: {client_info['telephone']}", info_style))
    if client_info.get('email'):
        elements.append(Paragraph(f"Email: {client_info['email']}", info_style))
    
    elements.append(Spacer(1, 10*mm))
    return elements

def create_items_lines(items, theme='bleu'):
    """Crée la liste des articles en lignes simples (pas de tableau)"""
    theme_colors = THEMES_COULEURS[theme]
    elements = []
    
    # Style pour le titre
    title_style = ParagraphStyle(
        'ItemsTitleStyle',
        fontSize=12,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=8*mm
    )
    
    # Style pour les en-têtes
    header_style = ParagraphStyle(
        'ItemsHeaderStyle',
        fontSize=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        backColor=theme_colors['principale']
    )
    
    # Style pour les articles
    item_style = ParagraphStyle(
        'ItemStyle',
        fontSize=9,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=3*mm
    )
    
    elements.append(Paragraph("Articles", title_style))
    
    # En-têtes en lignes simples
    elements.append(Paragraph("Description | Quantité | Prix unitaire | Prix total", header_style))
    elements.append(Spacer(1, 3*mm))
    
    # Articles en lignes simples
    for item in items:
        description = item.get('description', '')
        quantite = item.get('quantite', 1)
        prix_unitaire = item.get('prix_unitaire', 0)
        prix_total = quantite * prix_unitaire
        
        item_line = f"{description} | {quantite} | {prix_unitaire:.2f}€ | {prix_total:.2f}€"
        elements.append(Paragraph(item_line, item_style))
    
    elements.append(Spacer(1, 10*mm))
    return elements

def create_totals_lines(devis_data, theme='bleu'):
    """Crée les totaux en lignes simples alignées à droite"""
    theme_colors = THEMES_COULEURS[theme]
    elements = []
    
    # Styles alignés à droite
    totals_style = ParagraphStyle(
        'TotalsStyle',
        fontSize=10,
        textColor=theme_colors['principale'],
        fontName='Helvetica',
        alignment=TA_RIGHT,
        spaceAfter=2*mm
    )
    
    totals_bold = ParagraphStyle(
        'TotalsBold',
        fontSize=10,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        spaceAfter=2*mm
    )
    
    # Calculs des totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht = devis_data['total_ht']
    else:
        total_ht = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data.get('items', []))
    
    if 'total_tva' in devis_data:
        total_tva = devis_data['total_tva']
    else:
        total_tva = sum(
            (item.get('prix_unitaire', 0) * item.get('quantite', 1)) * (item.get('tva_taux', 0.20)) 
            for item in devis_data.get('items', [])
        )
    
    if 'total_ttc' in devis_data:
        total_ttc = devis_data['total_ttc']
    else:
        total_ttc = total_ht + total_tva
    
    # Totaux alignés à droite
    elements.append(Paragraph(f"Total HT: {total_ht:.2f}€", totals_style))
    elements.append(Paragraph(f"Total TVA: {total_tva:.2f}€", totals_style))
    elements.append(HRFlowable(width="30%", thickness=1, lineCap='round', color=theme_colors['accent'], hAlign='RIGHT'))
    elements.append(Paragraph(f"<b>Total TTC: {total_ttc:.2f}€</b>", totals_bold))
    
    elements.append(Spacer(1, 15*mm))
    return elements

def generate_pdf_without_tables(company_info, devis_data, client_info, filename, theme='bleu'):
    """
    Génère un PDF professionnel SANS TABLEAUX - seulement des lignes simples
    
    Fonctionnalités conservées:
    - Design épuré sans tableau (comme le PDF Infinytia qu'on a développé plus tôt)
    - Gestion du logo automatique
    - Articles avec détails en dessous
    - Footer automatique avec pagination
    - Compatible avec tous vos champs JSON
    """
    theme_colors = THEMES_COULEURS.get(theme, THEMES_COULEURS['bleu'])
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=3*cm,
        canvasmaker=CustomCanvas
    )
    
    # Configuration du canvas personnalisé
    doc.canvasmaker.company_info = company_info
    doc.canvasmaker.theme = theme
    
    elements = []
    
    # En-tête avec logo
    elements.extend(create_header_with_logo(company_info, theme))
    
    # Titre du document
    title_style = ParagraphStyle(
        'TitleStyle',
        fontSize=18,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=10*mm
    )
    elements.append(Paragraph("DEVIS", title_style))
    
    # Informations du devis
    elements.extend(create_document_info_lines(devis_data, theme))
    
    # Informations client
    elements.extend(create_client_info_lines(client_info, theme))
    
    # Articles
    elements.extend(create_items_lines(devis_data.get('items', []), theme))
    
    # Totaux
    elements.extend(create_totals_lines(devis_data, theme))
    
    # Construction du PDF
    doc.build(elements)
    
    return filename

# Fonction de compatibilité avec l'ancienne API
def generate_devis_pdf(company_info, devis_data, client_info, filename="devis.pdf", theme='bleu'):
    """Fonction de compatibilité - génère un devis PDF sans tableaux"""
    return generate_pdf_without_tables(company_info, devis_data, client_info, filename, theme)

def generate_facture_pdf(company_info, facture_data, client_info, filename="facture.pdf", theme='bleu'):
    """Génère une facture PDF sans tableaux"""
    # Remplace le titre par "FACTURE"
    original_generate = generate_pdf_without_tables
    
    def modified_generate(company_info, facture_data, client_info, filename, theme):
        # On utilise la même fonction mais on change juste le titre
        theme_colors = THEMES_COULEURS.get(theme, THEMES_COULEURS['bleu'])
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=3*cm,
            canvasmaker=CustomCanvas
        )
        
        doc.canvasmaker.company_info = company_info
        doc.canvasmaker.theme = theme
        
        elements = []
        
        # En-tête avec logo
        elements.extend(create_header_with_logo(company_info, theme))
        
        # Titre FACTURE au lieu de DEVIS
        title_style = ParagraphStyle(
            'TitleStyle',
            fontSize=18,
            textColor=theme_colors['principale'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=10*mm
        )
        elements.append(Paragraph("FACTURE", title_style))
        
        # Le reste identique
        elements.extend(create_document_info_lines(facture_data, theme))
        elements.extend(create_client_info_lines(client_info, theme))
        elements.extend(create_items_lines(facture_data.get('items', []), theme))
        elements.extend(create_totals_lines(facture_data, theme))
        
        doc.build(elements)
        return filename
    
    return modified_generate(company_info, facture_data, client_info, filename, theme)

if __name__ == "__main__":
    # Exemple d'utilisation
    company_info = {
        'nom': 'Mon Entreprise',
        'adresse': '123 Rue de l\'Exemple',
        'ville': 'Paris',
        'code_postal': '75001',
        'telephone': '01 23 45 67 89',
        'email': 'contact@monentreprise.fr',
        'logo_url': 'https://example.com/logo.png'  # ou 'logo_path': '/path/to/logo.png'
    }
    
    devis_data = {
        'numero': 'DEV-2024-001',
        'date_emission': '27/09/2025',
        'date_expiration': '27/10/2025',
        'items': [
            {
                'description': 'Formation Python avancée',
                'quantite': 5,
                'prix_unitaire': 500.0,
                'tva_taux': 0.20
            },
            {
                'description': 'Support technique',
                'quantite': 10,
                'prix_unitaire': 150.0,
                'tva_taux': 0.20
            }
        ]
    }
    
    client_info = {
        'nom': 'Client Test SARL',
        'adresse': '456 Avenue du Client',
        'ville': 'Lyon',
        'code_postal': '69000',
        'telephone': '04 12 34 56 78',
        'email': 'client@test.fr'
    }
    
    # Génération du PDF
    print("Génération du devis sans tableaux...")
    generate_devis_pdf(company_info, devis_data, client_info, "devis_sans_tableaux.pdf", theme='bleu')
    print("✅ Devis généré : devis_sans_tableaux.pdf")
    
    print("Génération de la facture sans tableaux...")
    generate_facture_pdf(company_info, devis_data, client_info, "facture_sans_tableaux.pdf", theme='vert')
    print("✅ Facture générée : facture_sans_tableaux.pdf")
