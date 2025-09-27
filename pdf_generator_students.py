# pdf_generator_students.py - Version avec design professionnel, thèmes colorés et support logo SANS TABLEAU
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY
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

def download_logo(logo_url):
    """Télécharge le logo depuis une URL et retourne un objet Image"""
    if not logo_url:
        return None
    
    try:
        print(f"Tentative de téléchargement du logo depuis: {logo_url}")
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        
        img_data = BytesIO(response.content)
        print(f"Logo téléchargé avec succès, taille: {len(response.content)} bytes")
        return img_data
        
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None

def create_header_with_logo_from_devis(devis_data):
    """Crée l'en-tête avec logo depuis les données du devis - LIGNES SIMPLES SEULEMENT"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # Style pour l'en-tête
    company_style = ParagraphStyle(
        'CompanyStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=12,
        spaceAfter=3*mm
    )
    
    # Gestion du logo si présent
    logo_element = None
    if devis_data.get('logo_url'):
        logo_data = download_logo(devis_data['logo_url'])
        if logo_data:
            try:
                logo_element = Image(logo_data, width=4*cm, height=3*cm)
                # Logo en haut à droite - utilisation d'un tableau simple juste pour le positionnement
                logo_table = Table([["", logo_element]], colWidths=[14*cm, 5*cm])
                logo_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ]))
                elements.append(logo_table)
                elements.append(Spacer(1, 5*mm))
            except Exception as e:
                print(f"Erreur logo: {e}")
                # Si le logo ne marche pas, on continue sans
                pass
    
    # Informations de l'entreprise en lignes simples
    if devis_data.get('fournisseur_nom'):
        elements.append(Paragraph(devis_data['fournisseur_nom'], company_style))
    if devis_data.get('fournisseur_adresse'):
        elements.append(Paragraph(devis_data['fournisseur_adresse'], company_style))
    if devis_data.get('fournisseur_ville'):
        elements.append(Paragraph(devis_data['fournisseur_ville'], company_style))
    if devis_data.get('fournisseur_email'):
        elements.append(Paragraph(devis_data['fournisseur_email'], company_style))
    if devis_data.get('fournisseur_siret'):
        elements.append(Paragraph(f"SIRET: {devis_data['fournisseur_siret']}", company_style))
    
    elements.append(Spacer(1, 10*mm))
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
    """Crée les articles VRAIMENT en lignes simples - AUCUN tableau"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # Titre des articles
    title_style = ParagraphStyle(
        'ArticlesTitleStyle',
        fontSize=14,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=8*mm
    )
    
    # Style pour chaque article
    article_style = ParagraphStyle(
        'ArticleStyle',
        fontSize=11,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=3*mm
    )
    
    # Style pour les détails
    detail_style = ParagraphStyle(
        'DetailStyle',
        fontSize=9,
        textColor=theme_colors['secondaire'],
        alignment=TA_LEFT,
        leftIndent=10*mm,
        spaceAfter=2*mm
    )
    
    # Style pour les prix
    price_style = ParagraphStyle(
        'PriceStyle',
        fontSize=10,
        textColor=theme_colors['secondaire'],
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=5*mm
    )
    
    elements.append(Paragraph("ARTICLES", title_style))
    
    # Chaque article en lignes simples
    for item in items:
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        tva_taux = item.get('tva_taux', 20)
        total_ht = prix_unitaire * quantite
        
        # Titre de l'article
        elements.append(Paragraph(f"<b>{item.get('description', '')}</b>", article_style))
        
        # Prix en ligne simple
        prix_line = f"Quantité: {quantite} • Prix unitaire: {prix_unitaire:.2f}€ • TVA: {tva_taux}% • Total: {total_ht:.2f}€"
        elements.append(Paragraph(prix_line, price_style))
        
        # Détails de l'article en lignes simples
        if item.get('details'):
            for detail in item.get('details', []):
                elements.append(Paragraph(f"• {detail}", detail_style))
        
        elements.append(Spacer(1, 8*mm))
    
    return elements

def create_totaux_from_devis(devis_data):
    """Crée les totaux en lignes simples alignées à droite - AUCUN tableau"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    # Style aligné à droite
    totals_style = ParagraphStyle(
        'TotalsStyle',
        fontSize=12,
        textColor=theme_colors['principale'],
        fontName='Helvetica',
        alignment=TA_RIGHT,
        spaceAfter=3*mm
    )
    
    totals_bold = ParagraphStyle(
        'TotalsBold',
        fontSize=14,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        spaceAfter=3*mm
    )
    
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
    
    elements.append(Spacer(1, 10*mm))
    
    # Totaux en lignes simples
    elements.append(Paragraph(f"Total HT: {total_ht:.2f}€", totals_style))
    elements.append(Paragraph(f"Montant total de la TVA: {total_tva:.2f}€", totals_style))
    
    # Ligne de séparation simple
    elements.append(HRFlowable(width="30%", thickness=1, lineCap='round', color=theme_colors['principale'], hAlign='RIGHT'))
    
    elements.append(Paragraph(f"Total TTC: {total_ttc:.2f}€", totals_bold))
    
    elements.append(Spacer(1, 15*mm))
    return elements

def create_footer_sections(devis_data):
    """Crée les sections finales du devis - AUCUN tableau, AUCUN HTML"""
    theme_colors = THEMES_COULEURS['bleu']
    elements = []
    
    section_title_style = ParagraphStyle(
        'SectionTitleStyle', 
        fontSize=12, 
        textColor=theme_colors['principale'], 
        fontName='Helvetica-Bold',
        spaceAfter=5*mm
    )
    
    section_content_style = ParagraphStyle(
        'SectionContentStyle', 
        fontSize=10, 
        textColor=theme_colors['secondaire'],
        spaceAfter=8*mm
    )
    
    small_text_style = ParagraphStyle(
        'SmallTextStyle', 
        fontSize=8, 
        textColor=theme_colors['accent'],
        spaceAfter=8*mm
    )
    
    # Conditions de paiement
    elements.append(Paragraph("CONDITIONS DE PAIEMENT", section_title_style))
    elements.append(Paragraph(devis_data.get('conditions_paiement', '50% à la commande, 50% à la livraison'), section_content_style))
    
    if devis_data.get('penalites_retard'):
        elements.append(Paragraph(devis_data.get('penalites_retard'), small_text_style))
    
    # Coordonnées bancaires
    elements.append(Paragraph("COORDONNÉES BANCAIRES", section_title_style))
    
    # Informations bancaires en lignes simples
    elements.append(Paragraph(f"Banque: {devis_data.get('banque_nom', 'Qonto')}", section_content_style))
    elements.append(Paragraph(f"IBAN: {devis_data.get('banque_iban', 'FR7616958000013234941023663')}", section_content_style))
    elements.append(Paragraph(f"BIC: {devis_data.get('banque_bic', 'QNTOFRP1XXX')}", section_content_style))
    
    # Texte de conclusion
    if devis_data.get('texte_conclusion'):
        elements.append(Paragraph(devis_data.get('texte_conclusion'), section_content_style))
    else:
        elements.append(Paragraph("Cette proposition reste valable 30 jours. Nous restons à votre entière disposition pour tout complément d'information.", section_content_style))
    
    elements.append(Spacer(1, 15*mm))
    
    # Bon pour accord - EN TEXTE SIMPLE
    signature_style = ParagraphStyle(
        'SignatureStyle',
        fontSize=11,
        textColor=theme_colors['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        spaceAfter=10*mm
    )
    
    elements.append(Paragraph("Bon pour accord", signature_style))
    elements.append(Paragraph("Date et signature:", signature_style))
    
    return elements

# Fonction principale compatible avec Railway
def generate_student_style_devis(devis_data):
    """
    Génère un devis PDF avec la structure du modèle rouge mais sans couleurs
    """
    theme_colors = THEMES_COULEURS['bleu']
    
    # Créer le dossier s'il n'existe pas
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    
    # 1. EN-TÊTE : Logo + Titre + Infos entreprise (comme le modèle rouge)
    # Télécharger le logo
    logo_element = None
    if devis_data.get('logo_url'):
        try:
            logo_data = download_logo(devis_data['logo_url'])
            if logo_data:
                logo_element = Image(logo_data, width=3*cm, height=2*cm)
        except:
            pass
    
    # Si pas de logo, créer un placeholder
    if not logo_element:
        logo_placeholder = Paragraph("Logo", ParagraphStyle('LogoStyle', fontSize=12, alignment=TA_CENTER, fontName='Helvetica-Bold'))
    
    # En-tête avec logo à droite et titre au centre
    header_data = [
        [
            Paragraph(f"<b>{devis_data.get('fournisseur_nom', 'INFINYTIA')}</b><br/>{devis_data.get('fournisseur_adresse', '61 Rue De Lyon')}<br/>{devis_data.get('fournisseur_ville', '75012 Paris, FR')}", 
                     ParagraphStyle('CompanyStyle', fontSize=9, textColor=colors.black)),
            Paragraph("<b>Devis</b>", ParagraphStyle('TitleStyle', fontSize=24, textColor=colors.black, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            logo_element if logo_element else logo_placeholder
        ]
    ]
    
    header_table = Table(header_data, colWidths=[6*cm, 6*cm, 5*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # 2. INFORMATIONS CLIENT ET DEVIS (comme le modèle rouge)
    # Partie gauche : Client
    client_content = f"""<b>Client :</b><br/>
<b>{devis_data.get('client_nom', '')}</b><br/>
{devis_data.get('client_adresse', '')}<br/>
{devis_data.get('client_ville', '')}<br/>
{devis_data.get('client_email', '')}"""
    
    # Partie droite : Infos devis
    devis_content = f"""<b>Date :</b> {devis_data.get('date_emission', '')}<br/>
<b>Référence :</b> {devis_data.get('numero', '')}<br/>
<b>Date de validité :</b> {devis_data.get('date_expiration', '')}"""
    
    client_devis_data = [
        [
            Paragraph(client_content, ParagraphStyle('ClientStyle', fontSize=9, textColor=colors.black)),
            Paragraph(devis_content, ParagraphStyle('DevisStyle', fontSize=9, textColor=colors.black))
        ]
    ]
    
    client_devis_table = Table(client_devis_data, colWidths=[10*cm, 7*cm])
    client_devis_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(client_devis_table)
    elements.append(Spacer(1, 10*mm))
    
    # 3. INFORMATIONS ADDITIONNELLES (optionnel)
    if devis_data.get('texte_intro'):
        elements.append(Paragraph(f"<b>Informations additionnelles :</b><br/>{devis_data.get('texte_intro')}", 
                                 ParagraphStyle('InfoStyle', fontSize=9, textColor=colors.black, spaceAfter=10)))
    
    # 4. TABLEAU DES ARTICLES (exactement comme le modèle rouge)
    # En-tête du tableau
    articles_data = []
    
    # Headers
    headers = [
        "Description",
        "Quantité", 
        "Unité",
        "Prix unitaire HT",
        "% TVA",
        "Total TVA",
        "Total TTC"
    ]
    
    header_style = ParagraphStyle('HeaderStyle', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER)
    headers_formatted = [Paragraph(h, header_style) for h in headers]
    articles_data.append(headers_formatted)
    
    # Articles
    article_style = ParagraphStyle('ArticleStyle', fontSize=9, textColor=colors.black)
    number_style = ParagraphStyle('NumberStyle', fontSize=9, textColor=colors.black, alignment=TA_CENTER)
    
    for item in devis_data.get('items', []):
        prix_unitaire = float(item.get('prix_unitaire', 0))
        quantite = int(item.get('quantite', 1))
        tva_taux = float(item.get('tva_taux', 20))
        
        total_ht = prix_unitaire * quantite
        total_tva = total_ht * (tva_taux / 100)
        total_ttc = total_ht + total_tva
        
        row = [
            Paragraph(item.get('description', ''), article_style),
            Paragraph(str(quantite), number_style),
            Paragraph("unité", number_style),  # Unité par défaut
            Paragraph(f"{prix_unitaire:.2f} €", number_style),
            Paragraph(f"{tva_taux:.0f} %", number_style),
            Paragraph(f"{total_tva:.2f} €", number_style),
            Paragraph(f"{total_ttc:.2f} €", number_style)
        ]
        articles_data.append(row)
    
    # Calcul des totaux
    total_ht = sum(float(item.get('prix_unitaire', 0)) * int(item.get('quantite', 1)) for item in devis_data.get('items', []))
    total_tva_calc = sum((float(item.get('prix_unitaire', 0)) * int(item.get('quantite', 1))) * (float(item.get('tva_taux', 20)) / 100) for item in devis_data.get('items', []))
    total_ttc_calc = total_ht + total_tva_calc
    
    # Utiliser les totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht = float(devis_data['total_ht'])
    if 'total_tva' in devis_data:
        total_tva_calc = float(devis_data['total_tva'])
    if 'total_ttc' in devis_data:
        total_ttc_calc = float(devis_data['total_ttc'])
    
    # Lignes de totaux
    totals_style = ParagraphStyle('TotalsStyle', fontSize=9, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    
    # Total HT
    articles_data.append([
        "", "", "", "", "", 
        Paragraph("Total HT", totals_style),
        Paragraph(f"{total_ht:.2f} €", totals_style)
    ])
    
    # Total TVA
    articles_data.append([
        "", "", "", "", "",
        Paragraph("Total TVA", totals_style),
        Paragraph(f"{total_tva_calc:.2f} €", totals_style)
    ])
    
    # Total TTC
    articles_data.append([
        "", "", "", "", "",
        Paragraph("Total TTC", totals_style),
        Paragraph(f"{total_ttc_calc:.2f} €", totals_style)
    ])
    
    # Créer le tableau
    articles_table = Table(articles_data, colWidths=[5*cm, 2*cm, 2*cm, 2.5*cm, 1.5*cm, 2*cm, 2*cm])
    
    # Style du tableau
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
        # Grille
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alignement
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Colonnes numériques centrées
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        # Totaux en gras
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
    ]
    
    articles_table.setStyle(TableStyle(table_style))
    elements.append(articles_table)
    
    elements.append(Spacer(1, 15*mm))
    
    # 5. FOOTER avec signature (comme le modèle rouge)
    footer_content = f"""<b>Coordonnées</b><br/>
{devis_data.get('fournisseur_nom', 'INFINYTIA')}<br/>
Téléphone : {devis_data.get('fournisseur_telephone', '+33 1 42 92 59 59')}<br/>
E-mail : {devis_data.get('fournisseur_email', 'contact@infinytia.com')}"""
    
    bank_content = f"""<b>Détails bancaires</b><br/>
Banque: {devis_data.get('banque_nom', 'Qonto')}<br/>
IBAN: {devis_data.get('banque_iban', 'FR7616958000013234941023663')}<br/>
BIC/Swift: {devis_data.get('banque_bic', 'QNTOFRP1XXX')}"""
    
    signature_content = """Signature du client (précédée de la mention « Bon pour accord »)"""
    
    footer_data = [
        [
            Paragraph(footer_content, ParagraphStyle('FooterStyle', fontSize=8, textColor=colors.black)),
            Paragraph(bank_content, ParagraphStyle('FooterStyle', fontSize=8, textColor=colors.black)),
            Paragraph(signature_content, ParagraphStyle('FooterStyle', fontSize=8, textColor=colors.black, alignment=TA_CENTER))
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[5.5*cm, 5.5*cm, 6*cm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(footer_table)
    
    # Construction du PDF
    doc.build(elements)
    return filename

# Test de compatibilité Railway
if __name__ == "__main__":
    # Test avec les données du format Railway
    test_data = {
        "numero": "D-2025-0927-002",
        "date_emission": "27/09/2025",
        "date_expiration": "27/10/2025",
        "fournisseur_nom": "INFINYTIA",
        "fournisseur_adresse": "61 Rue De Lyon",
        "fournisseur_ville": "75012 Paris, FR",
        "fournisseur_email": "tony@infinytia.com",
        "fournisseur_siret": "93968736400017",
        "client_nom": "Teddy Carrillo - Efficity",
        "client_email": "tcarrillo@efficity.com",
        "items": [
            {
                "description": "Développement CRM complet",
                "quantite": 1,
                "prix_unitaire": 2700.0,
                "tva_taux": 20,
                "details": [
                    "Phase 1 : Architecture et conception",
                    "Phase 2 : Module de gestion des leads",
                    "Livrables : CRM fonctionnel, support 1 mois"
                ]
            }
        ],
        "conditions_paiement": "50% à la commande, 50% à la livraison",
        "banque_nom": "Qonto",
        "banque_iban": "FR7616958000013234941023663",
        "banque_bic": "QNTOFRP1XXX"
    }
    
    print("Test de la fonction Railway compatible...")
    filename = generate_student_style_devis(test_data)
    print(f"✅ PDF généré : {filename}")
