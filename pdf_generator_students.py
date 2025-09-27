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

# Fonction principale compatible avec Railway
def generate_student_style_devis(devis_data):
    """
    Fonction principale compatible avec votre système Railway
    Génère un devis PDF avec le nouveau design sans tableaux
    """
    theme_colors = THEMES_COULEURS['bleu']  # Utilise le thème bleu par défaut
    
    # Créer le dossier s'il n'existe pas
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
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
    
    # Configuration du canvas
    doc.canvasmaker.company_info = {
        'nom': devis_data.get('fournisseur_nom', 'INFINYTIA')
    }
    doc.canvasmaker.theme = 'bleu'
    
    elements = []
    
    # En-tête avec logo
    elements.extend(create_header_with_logo_from_devis(devis_data))
    
    # Titre du document
    title_style = ParagraphStyle(
        'TitleStyle',
        fontSize=24,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=8*mm
    )
    elements.append(Paragraph("Devis", title_style))
    
    # Informations du devis en lignes simples
    elements.extend(create_devis_info_lines(devis_data))
    
    # Fournisseur et client
    elements.extend(create_fournisseur_client_lines(devis_data))
    
    # Texte d'introduction
    if devis_data.get('texte_intro'):
        intro_style = ParagraphStyle('IntroStyle', fontSize=10, textColor=theme_colors['secondaire'], alignment=TA_JUSTIFY, spaceAfter=8*mm)
        elements.append(Paragraph(devis_data.get('texte_intro'), intro_style))
    
    # Articles avec en-tête
    elements.extend(create_articles_with_header(devis_data.get('items', [])))
    
    # Totaux
    elements.extend(create_totaux_from_devis(devis_data))
    
    # Conditions et informations finales
    elements.extend(create_footer_sections(devis_data))
    
    # Construction du PDF
    doc.build(elements)
    return filename

def create_header_with_logo_from_devis(devis_data):
    """Crée l'en-tête avec logo depuis les données du devis"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # Style pour l'en-tête
    company_style = ParagraphStyle(
        'CompanyStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=12
    )
    
    # Gestion du logo si présent
    logo_element = None
    if devis_data.get('logo_url'):
        logo_data = download_logo(devis_data['logo_url'])
        if logo_data:
            logo_element = Image(logo_data, width=3*cm, height=2*cm)
    
    if logo_element:
        # Table simple pour aligner logo et titre côte à côte
        header_data = [["", logo_element]]
        header_table = Table(header_data, colWidths=[15*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 5*mm))
    
    return elements

def create_devis_info_lines(devis_data):
    """Crée les informations du devis en lignes simples"""
    theme_colors = THEMES_COULEURS['bleu']
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
    
    # Informations en lignes simples
    elements.append(Paragraph("Numéro de devis", label_style))
    elements.append(Paragraph(devis_data.get('numero', ''), value_style))
    
    elements.append(Paragraph("Date d'émission", label_style))
    elements.append(Paragraph(devis_data.get('date_emission', ''), value_style))
    
    elements.append(Paragraph("Date d'expiration", label_style))
    elements.append(Paragraph(devis_data.get('date_expiration', ''), value_style))
    
    elements.append(Spacer(1, 8*mm))
    return elements

def create_fournisseur_client_lines(devis_data):
    """Crée les informations fournisseur et client en lignes simples"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    address_style = ParagraphStyle('AddressStyle', fontSize=9, textColor=theme_colors['secondaire'])
    
    # Fournisseur
    fournisseur_content = f"""<b>{devis_data.get('fournisseur_nom', 'INFINYTIA')}</b><br/>
{devis_data.get('fournisseur_adresse', '61 Rue De Lyon')}<br/>
{devis_data.get('fournisseur_ville', '75012 Paris, FR')}<br/>
{devis_data.get('fournisseur_email', 'contact@infinytia.com')}<br/>
{devis_data.get('fournisseur_siret', '93968736400017')}"""
    
    # Client
    client_content = f"""<b>{devis_data.get('client_nom', '')}</b><br/>
{devis_data.get('client_email', '')}<br/>"""
    
    if devis_data.get('client_tva'):
        client_content += f"Numéro de TVA: {devis_data.get('client_tva', '')}"
    
    # Table invisible pour aligner côte à côte
    company_client_data = [
        [
            Paragraph(fournisseur_content, address_style),
            Paragraph(client_content, address_style)
        ]
    ]
    
    company_client_table = Table(company_client_data, colWidths=[9*cm, 9*cm])
    company_client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(company_client_table)
    elements.append(Spacer(1, 10*mm))
    
    return elements

def create_articles_with_header(items):
    """Crée les articles avec en-tête mais sans tableaux encadrés"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # En-tête des articles (on garde le tableau pour l'en-tête car c'est plus propre)
    header_style = ParagraphStyle('HeaderStyle', fontSize=11, textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_CENTER)
    
    table_header_data = [
        [
            Paragraph("Description", header_style),
            Paragraph("Qté", header_style),
            Paragraph("Prix unitaire", header_style),
            Paragraph("TVA (%)", header_style),
            Paragraph("Total HT", header_style)
        ]
    ]
    
    table_header = Table(table_header_data, colWidths=[7*cm, 2*cm, 3*cm, 2*cm, 3*cm])
    table_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), theme_colors['principale']),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
    ]))
    
    elements.append(table_header)
    
    # Articles en lignes simples avec détails
    article_style = ParagraphStyle('ArticleStyle', fontSize=10, textColor=theme_colors['secondaire'], fontName='Helvetica-Bold')
    detail_style = ParagraphStyle('DetailStyle', fontSize=9, textColor=theme_colors['secondaire'], leftIndent=0, alignment=TA_JUSTIFY)
    
    for item in items:
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        tva_taux = item.get('tva_taux', 20)
        total_ht = prix_unitaire * quantite
        
        # Ligne article en format tableau mais avec bordures subtiles
        article_data = [
            [
                Paragraph(item.get('description', ''), article_style),
                Paragraph(str(quantite), article_style),
                Paragraph(f"{prix_unitaire:.2f} €", article_style),
                Paragraph(f"{tva_taux} %", article_style),
                Paragraph(f"{total_ht:.2f} €", article_style)
            ]
        ]
        
        article_table = Table(article_data, colWidths=[7*cm, 2*cm, 3*cm, 2*cm, 3*cm])
        article_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, theme_colors['accent']),
        ]))
        
        elements.append(article_table)
        
        # Détails en lignes simples
        if item.get('details'):
            details_text = ""
            for detail in item.get('details', []):
                details_text += f"{detail}<br/>"
            
            elements.append(Paragraph(details_text, detail_style))
        
        elements.append(Spacer(1, 5*mm))
    
    elements.append(Spacer(1, 5*mm))
    return elements

def create_totaux_from_devis(devis_data):
    """Crée les totaux depuis les données du devis"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # Calcul des totaux
    total_ht = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data.get('items', []))
    total_tva = sum(
        (item.get('prix_unitaire', 0) * item.get('quantite', 1)) * (item.get('tva_taux', 20) / 100)
        for item in devis_data.get('items', [])
    )
    total_ttc = total_ht + total_tva
    
    # Utiliser les totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht = devis_data['total_ht']
    if 'total_tva' in devis_data:
        total_tva = devis_data['total_tva']
    if 'total_ttc' in devis_data:
        total_ttc = devis_data['total_ttc']
    
    # Table des totaux alignée à droite
    totals_data = [
        ['', 'Total HT', f"{total_ht:.2f} €"],
        ['', 'Montant total de la TVA', f"{total_tva:.2f} €"],
        ['', 'Total TTC', f"{total_ttc:.2f} €"]
    ]
    
    totals_table = Table(totals_data, colWidths=[12*cm, 4*cm, 3*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (1, 2), (-1, 2), 1, theme_colors['principale']),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))
    
    return elements

def create_footer_sections(devis_data):
    """Crée les sections finales du devis"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    section_title_style = ParagraphStyle('SectionTitleStyle', fontSize=12, textColor=theme_colors['principale'], fontName='Helvetica-Bold')
    section_content_style = ParagraphStyle('SectionContentStyle', fontSize=10, textColor=theme_colors['secondaire'])
    small_text_style = ParagraphStyle('SmallTextStyle', fontSize=8, textColor=theme_colors['accent'])
    
    # Conditions de paiement
    elements.append(Paragraph("CONDITIONS DE PAIEMENT", section_title_style))
    elements.append(Paragraph(devis_data.get('conditions_paiement', '50% à la commande, 50% à la livraison'), section_content_style))
    elements.append(Spacer(1, 3*mm))
    
    if devis_data.get('penalites_retard'):
        elements.append(Paragraph(devis_data.get('penalites_retard'), small_text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    # Coordonnées bancaires
    elements.append(Paragraph("COORDONNÉES BANCAIRES", section_title_style))
    
    bank_content = f"""Banque: {devis_data.get('banque_nom', 'Qonto')}<br/>
IBAN: {devis_data.get('banque_iban', 'FR7616958000013234941023663')}<br/>
BIC: {devis_data.get('banque_bic', 'QNTOFRP1XXX')}"""
    
    elements.append(Paragraph(bank_content, section_content_style))
    elements.append(Spacer(1, 8*mm))
    
    # Texte de conclusion
    if devis_data.get('texte_conclusion'):
        elements.append(Paragraph(devis_data.get('texte_conclusion'), section_content_style))
    else:
        elements.append(Paragraph("Cette proposition reste valable 30 jours. Nous restons à votre entière disposition pour tout complément d'information.", section_content_style))
    
    elements.append(Spacer(1, 15*mm))
    
    # Bon pour accord
    signature_data = [
        ['', 'Bon pour accord<br/>Date et signature:']
    ]
    
    signature_table = Table(signature_data, colWidths=[12*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
    ]))
    
    elements.append(signature_table)
    
    return elements

# Fonctions de compatibilité supplémentaires
def generate_devis_pdf(company_info, devis_data, client_info, filename="devis.pdf", theme='bleu'):
    """Fonction de compatibilité - génère un devis PDF sans tableaux"""
    return generate_pdf_without_tables(company_info, devis_data, client_info, filename, theme)

def generate_facture_pdf(company_info, facture_data, client_info, filename="facture.pdf", theme='bleu'):
    """Génère une facture PDF sans tableaux"""
    return generate_pdf_without_tables(company_info, facture_data, client_info, filename, theme)

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
