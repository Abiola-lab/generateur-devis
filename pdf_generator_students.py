# pdf_generator_students.py - Modèle turquoise exact
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
import os
import requests
from io import BytesIO

# Couleurs du nouveau modèle turquoise
COULEUR_TURQUOISE = colors.HexColor('#40B5A8')  # Turquoise principal
COULEUR_TEXTE_NOIR = colors.black
COULEUR_GRIS_CLAIR = colors.HexColor('#f0f0f0')
COULEUR_BORDURE = colors.HexColor('#cccccc')

def download_logo(logo_url):
    """Télécharger et traiter le logo depuis une URL"""
    if not logo_url:
        return None
    
    try:
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            
            # Redimensionner le logo (hauteur max 1.5cm pour ce modèle)
            max_height = 1.5 * cm
            logo.drawHeight = max_height
            logo.drawWidth = max_height * logo.imageWidth / logo.imageHeight
            
            # Si le logo est trop large, le redimensionner par la largeur
            max_width = 2.5 * cm
            if logo.drawWidth > max_width:
                logo.drawWidth = max_width
                logo.drawHeight = max_width * logo.imageHeight / logo.imageWidth
            
            return logo
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None
    
    return None

class DevisCanvas(canvas.Canvas):
    """Canvas personnalisé pour ajouter la bande turquoise en bas"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
    
    def showPage(self):
        # Ajouter la bande turquoise en bas avant de montrer la page
        self.saveState()
        self.setFillColor(COULEUR_TURQUOISE)
        self.rect(0, 0, A4[0], 15*mm, fill=1, stroke=0)
        self.restoreState()
        canvas.Canvas.showPage(self)

def generate_student_style_devis(devis_data):
    """
    Générer un devis PDF avec le style turquoise exact de l'image
    """
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Document A4 avec marges et canvas personnalisé
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=25*mm,  # Plus de marge pour la bande turquoise
        canvasmaker=DevisCanvas
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ==========================================
    # 1. EN-TÊTE : "DEVIS n° XXX" + Logo
    # ==========================================
    
    # Télécharger le logo
    logo = download_logo(devis_data.get('logo_url', ''))
    
    # Style pour "DEVIS n° XXX"
    devis_title_style = ParagraphStyle(
        'DevisTitleStyle',
        fontSize=20,
        textColor=COULEUR_TURQUOISE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    if logo:
        # Avec logo : Titre à gauche, logo à droite
        header_data = [
            [Paragraph(f"DEVIS n° {devis_data.get('numero', '')}", devis_title_style), logo]
        ]
        header_table = Table(header_data, colWidths=[15*cm, 3*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
    else:
        # Sans logo : Titre seul
        header_data = [
            [Paragraph(f"DEVIS n° {devis_data.get('numero', '')}", devis_title_style), '']
        ]
        header_table = Table(header_data, colWidths=[15*cm, 3*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 3*mm))
    
    # Ligne turquoise sous l'en-tête
    line_data = [['', '']]
    line_table = Table(line_data, colWidths=[18*cm, 0*cm])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, COULEUR_TURQUOISE),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 5*mm))
    
    # ==========================================
    # 2. SECTION ENTREPRISE ET DESTINATAIRE
    # ==========================================
    
    # Styles
    company_title_style = ParagraphStyle('CompanyTitleStyle', fontSize=12, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
    company_info_style = ParagraphStyle('CompanyInfoStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    dest_title_style = ParagraphStyle('DestTitleStyle', fontSize=10, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
    dest_info_style = ParagraphStyle('DestInfoStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    
    # Contenu entreprise (colonne gauche)
    company_content = f"""<b>{devis_data.get('fournisseur_nom', 'Mon Entreprise')}</b><br/>
{devis_data.get('fournisseur_adresse', '')}<br/>
{devis_data.get('fournisseur_ville', '')}<br/>
Téléphone : {devis_data.get('fournisseur_telephone', '+33 1 23 45 67 89')}"""
    
    # Contenu destinataire (colonne droite)
    dest_content = f"""<b>Destinataire</b><br/>
{devis_data.get('client_nom', '')}<br/>
{devis_data.get('client_adresse', '')}<br/>
{devis_data.get('client_ville', '')}"""
    
    company_dest_data = [
        [
            Paragraph(company_content, company_info_style),
            Paragraph(dest_content, dest_info_style)
        ]
    ]
    
    company_dest_table = Table(company_dest_data, colWidths=[9*cm, 9*cm])
    company_dest_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(company_dest_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==========================================
    # 3. INFORMATIONS DU DEVIS (tableau)
    # ==========================================
    
    info_style = ParagraphStyle('InfoStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    info_bold_style = ParagraphStyle('InfoBoldStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
    
    devis_info_data = [
        [
            Paragraph("Date du devis :", info_bold_style),
            Paragraph(devis_data.get('date_emission', ''), info_style),
            '', ''
        ],
        [
            Paragraph("Référence du devis :", info_bold_style),
            Paragraph(devis_data.get('numero', ''), info_style),
            '', ''
        ],
        [
            Paragraph("Date de validité du devis :", info_bold_style),
            Paragraph(devis_data.get('date_expiration', ''), info_style),
            '', ''
        ],
        [
            Paragraph("Émis par :", info_bold_style),
            Paragraph(devis_data.get('fournisseur_nom', ''), info_style),
            '', ''
        ],
        [
            Paragraph("Contact client :", info_bold_style),
            Paragraph(devis_data.get('client_nom', ''), info_style),
            '', ''
        ],
        [
            Paragraph("Date de début de la prestation :", info_bold_style),
            Paragraph(devis_data.get('date_debut', ''), info_style),
            '', ''
        ]
    ]
    
    devis_info_table = Table(devis_info_data, colWidths=[5*cm, 4*cm, 5*cm, 4*cm])
    devis_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    elements.append(devis_info_table)
    elements.append(Spacer(1, 6*mm))
    
    # Informations additionnelles si présentes
    if devis_data.get('texte_intro'):
        info_add_style = ParagraphStyle('InfoAddStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
        elements.append(Paragraph("Informations additionnelles", info_add_style))
        elements.append(Paragraph(devis_data.get('texte_intro', ''), info_style))
        elements.append(Spacer(1, 5*mm))
    
    # ==========================================
    # 4. TABLEAU PRINCIPAL DES ARTICLES
    # ==========================================
    
    # Style pour les en-têtes
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        fontSize=9,
        textColor=COULEUR_TEXTE_NOIR,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # Styles pour les cellules
    cell_style = ParagraphStyle('CellStyle', fontSize=8, textColor=COULEUR_TEXTE_NOIR)
    cell_center_style = ParagraphStyle('CellCenterStyle', fontSize=8, textColor=COULEUR_TEXTE_NOIR, alignment=TA_CENTER)
    cell_right_style = ParagraphStyle('CellRightStyle', fontSize=8, textColor=COULEUR_TEXTE_NOIR, alignment=TA_RIGHT)
    
    # En-tête du tableau (7 colonnes comme dans l'image)
    table_data = [
        [
            Paragraph("Description", table_header_style),
            Paragraph("Quantité", table_header_style),
            Paragraph("Unité", table_header_style),
            Paragraph("Prix unitaire HT", table_header_style),
            Paragraph("% TVA", table_header_style),
            Paragraph("Total TVA", table_header_style),
            Paragraph("Total TTC", table_header_style)
        ]
    ]
    
    # Ajouter les articles
    for item in devis_data.get('items', []):
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        tva_taux = item.get('tva_taux', 20)
        
        total_ht = prix_unitaire * quantite
        total_tva = total_ht * (tva_taux / 100)
        total_ttc = total_ht + total_tva
        
        table_data.append([
            Paragraph(item.get('description', ''), cell_style),
            Paragraph(str(quantite), cell_center_style),
            Paragraph(item.get('unite', 'pcs'), cell_center_style),
            Paragraph(f"{prix_unitaire:.2f} €", cell_right_style),
            Paragraph(f"{tva_taux} %", cell_center_style),
            Paragraph(f"{total_tva:.2f} €", cell_right_style),
            Paragraph(f"{total_ttc:.2f} €", cell_right_style)
        ])
    
    # Créer le tableau principal
    main_table = Table(table_data, colWidths=[4.5*cm, 1.5*cm, 1.5*cm, 2.5*cm, 1.5*cm, 2*cm, 2.5*cm])
    
    # Style du tableau
    main_table.setStyle(TableStyle([
        # Bordures
        ('GRID', (0, 0), (-1, -1), 0.5, COULEUR_BORDURE),
        
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_GRIS_CLAIR),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
        # Alignements
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Quantité
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Unité
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Prix unitaire
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # % TVA
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Total TVA
        ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Total TTC
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==========================================
    # 5. TOTAUX
    # ==========================================
    
    # Calculer les totaux
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
    
    # Style pour les totaux
    total_style = ParagraphStyle('TotalStyle', fontSize=10, textColor=COULEUR_TEXTE_NOIR, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    total_ttc_style = ParagraphStyle('TotalTTCStyle', fontSize=11, textColor=COULEUR_TURQUOISE, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    
    # Tableau des totaux (aligné à droite)
    totals_data = [
        ['', '', '', '', '', 'Total HT', f"{total_ht:.2f} €"],
        ['', '', '', '', '', 'Total TVA', f"{total_tva:.2f} €"],
        ['', '', '', '', '', 'Total TTC', f"{total_ttc:.2f} €"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4.5*cm, 1.5*cm, 1.5*cm, 2.5*cm, 1.5*cm, 2*cm, 2.5*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (5, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (5, 0), (-1, 1), 10),
        ('FONTSIZE', (5, 2), (-1, 2), 11),
        ('TEXTCOLOR', (5, 2), (-1, 2), COULEUR_TURQUOISE),  # Total TTC en turquoise
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==========================================
    # 6. SIGNATURE (encadré gris)
    # ==========================================
    
    signature_style = ParagraphStyle('SignatureStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, alignment=TA_CENTER)
    
    signature_data = [
        [Paragraph("Signature du client (précédée de la mention « Bon pour accord »)", signature_style)]
    ]
    
    signature_table = Table(signature_data, colWidths=[18*cm])
    signature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COULEUR_GRIS_CLAIR),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, COULEUR_BORDURE),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 10*mm))
    
    # ==========================================
    # 7. FOOTER - 3 colonnes : Siège social / Coordonnées / Détails bancaires
    # ==========================================
    
    footer_title_style = ParagraphStyle('FooterTitleStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
    footer_content_style = ParagraphStyle('FooterContentStyle', fontSize=8, textColor=COULEUR_TEXTE_NOIR)
    
    # Contenu des 3 colonnes
    siege_content = f"""<b>Siège social</b><br/>
{devis_data.get('fournisseur_adresse', '22, Avenue Voltaire')}<br/>
{devis_data.get('fournisseur_ville', '13000 Marseille, France')}<br/>
N° Siret ou Siren : {devis_data.get('fournisseur_siret', 'xxxx•DEVIS n° 123')}<br/>
N° TVA Intra : {devis_data.get('client_tva', 'FRXX 999999999')}"""
    
    coordonnees_content = f"""<b>Coordonnées</b><br/>
{devis_data.get('fournisseur_nom', 'Pierre Fournisseur')}<br/>
Phone : {devis_data.get('fournisseur_telephone', '+33 30 12345678')}<br/>
E-mail : {devis_data.get('fournisseur_email', 'pierre@macompagnie.fr')}<br/>
www.macompagnie.fr"""
    
    banque_content = f"""<b>Détails bancaires</b><br/>
Banque : {devis_data.get('banque_nom', 'NP Paribas')}<br/>
Code banque : 10000000<br/>
N° de compte : 12345678<br/>
IBAN : {devis_data.get('banque_iban', 'FR2341124099234')}<br/>
SWIFT/BIC : {devis_data.get('banque_bic', 'FRHICXXX1001')}"""
    
    footer_data = [
        [
            Paragraph(siege_content, footer_content_style),
            Paragraph(coordonnees_content, footer_content_style),
            Paragraph(banque_content, footer_content_style)
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[6*cm, 6*cm, 6*cm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(footer_table)
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test si lancé directement
if __name__ == "__main__":
    test_data = {
        "numero": "123",
        "date_emission": "21/11/2019",
        "date_expiration": "21/12/2019",
        "date_debut": "21/1/2020",
        "fournisseur_nom": "Mon Entreprise",
        "fournisseur_adresse": "22, Avenue Voltaire",
        "fournisseur_ville": "13000 Marseille, France",
        "fournisseur_telephone": "+33 4 92 99 99 99",
        "fournisseur_email": "pierre@macompagnie.fr",
        "client_nom": "Acheteur SA",
        "client_adresse": "31, rue de la Forêt",
        "client_ville": "13100 Aix-en-Provence France",
        "logo_url": "https://via.placeholder.com/80x80/ff9500/ffffff?text=Logo",
        "texte_intro": "Service après-vente - Garantie : 1 an",
        "items": [
            {
                "description": "Client work",
                "quantite": 5,
                "unite": "h",
                "prix_unitaire": 60.00,
                "tva_taux": 20
            },
            {
                "description": "Products",
                "quantite": 10,
                "unite": "pcs",
                "prix_unitaire": 105.00,
                "tva_taux": 20
            }
        ]
    }
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF test généré : {filename}")
