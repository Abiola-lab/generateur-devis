# pdf_generator_students.py - VERSION COMPLÈTE avec logo et bon design
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import requests
from io import BytesIO

# Couleurs exactes de votre image
COULEUR_HEADER_BLEU = colors.HexColor('#4a90b8')  # Bleu de "Devis N°"
COULEUR_TEXTE_NOIR = colors.black
COULEUR_BORDURE_GRIS = colors.HexColor('#cccccc')

def download_logo(logo_url):
    """Télécharger et traiter le logo depuis une URL"""
    if not logo_url:
        return None
    
    try:
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            
            # Redimensionner le logo (hauteur max 2cm)
            max_height = 2 * cm
            logo.drawHeight = max_height
            logo.drawWidth = max_height * logo.imageWidth / logo.imageHeight
            
            # Si le logo est trop large, le redimensionner par la largeur
            max_width = 3 * cm
            if logo.drawWidth > max_width:
                logo.drawWidth = max_width
                logo.drawHeight = max_width * logo.imageHeight / logo.imageWidth
            
            return logo
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None
    
    return None

def generate_student_style_devis(devis_data):
    """
    Générer un devis PDF avec le style EXACT de votre image + gestion du logo
    """
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Document A4 avec marges
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ==========================================
    # 1. EN-TÊTE "DEVIS N°" + LOGO - Style exact de votre image
    # ==========================================
    
    # Télécharger le logo si une URL est fournie
    logo = download_logo(devis_data.get('logo_url', ''))
    
    # Créer un style pour "Devis N°"
    devis_header_style = ParagraphStyle(
        'DevisHeader',
        fontSize=14,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leftIndent=0,
        rightIndent=0
    )
    
    if logo:
        # Avec logo : Tableau avec logo à gauche et "Devis N°" à droite
        header_data = [
            [logo, Paragraph("Devis N°", devis_header_style)]
        ]
        header_table = Table(header_data, colWidths=[15*cm, 3*cm])
        header_table.setStyle(TableStyle([
            # Fond bleu pour "Devis N°"
            ('BACKGROUND', (1, 0), (1, 0), COULEUR_HEADER_BLEU),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Logo aligné à gauche
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # "Devis N°" centré
            ('TOPPADDING', (1, 0), (1, 0), 8),
            ('BOTTOMPADDING', (1, 0), (1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # Pas de bordures
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ]))
    else:
        # Sans logo : Tableau simple avec "Devis N°" à droite
        header_data = [
            ['', Paragraph("Devis N°", devis_header_style)]
        ]
        header_table = Table(header_data, colWidths=[15*cm, 3*cm])
        header_table.setStyle(TableStyle([
            # Fond bleu pour "Devis N°"
            ('BACKGROUND', (1, 0), (1, 0), COULEUR_HEADER_BLEU),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (1, 0), (1, 0), 8),
            ('BOTTOMPADDING', (1, 0), (1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # Pas de bordures
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 5*mm))
    
    # ==========================================
    # 2. SECTION INFORMATIONS - Layout exact
    # ==========================================
    
    info_style = ParagraphStyle('InfoStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica')
    info_bold_style = ParagraphStyle('InfoBoldStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, fontName='Helvetica-Bold')
    
    # Données côte à côte comme dans votre image
    info_data = [
        [
            Paragraph("Date du devis :", info_bold_style),
            Paragraph(devis_data.get('date_emission', ''), info_style),
            Paragraph("Nom du destinataire :", info_bold_style),
            Paragraph(devis_data.get('client_nom', ''), info_style)
        ],
        [
            Paragraph("Date de validité du devis :", info_bold_style),
            Paragraph(devis_data.get('date_expiration', ''), info_style),
            Paragraph("Adresse :", info_bold_style),
            Paragraph(devis_data.get('client_adresse', ''), info_style)
        ],
        [
            Paragraph("Émis par :", info_bold_style),
            Paragraph(devis_data.get('fournisseur_nom', ''), info_style),
            Paragraph("", info_style),
            Paragraph("", info_style)
        ],
        [
            Paragraph("Date de début de la prestation :", info_bold_style),
            Paragraph(devis_data.get('date_debut', ''), info_style),
            Paragraph("", info_style),
            Paragraph("", info_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[4.5*cm, 4.5*cm, 4*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==========================================
    # 3. TABLEAU PRINCIPAL - Style exact de votre image
    # ==========================================
    
    # Style pour les en-têtes du tableau
    table_header_style = ParagraphStyle(
        'TableHeader',
        fontSize=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # Style pour les données
    cell_style = ParagraphStyle('CellStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    cell_center_style = ParagraphStyle('CellCenterStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, alignment=TA_CENTER)
    cell_right_style = ParagraphStyle('CellRightStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR, alignment=TA_RIGHT)
    
    # En-tête du tableau (colonnes exactes de votre image)
    table_data = [
        [
            Paragraph("Description", table_header_style),
            Paragraph("Prix unitaire HT", table_header_style),
            Paragraph("Qté", table_header_style),
            Paragraph("Total HT", table_header_style)
        ]
    ]
    
    # Ajouter les articles
    for item in devis_data.get('items', []):
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        total_ligne = prix_unitaire * quantite
        
        table_data.append([
            Paragraph(item.get('description', ''), cell_style),
            Paragraph(f"{prix_unitaire:.2f} €", cell_right_style),
            Paragraph(str(quantite), cell_center_style),
            Paragraph(f"{total_ligne:.2f} €", cell_right_style)
        ])
    
    # Ajouter des lignes vides pour remplir le tableau (comme dans votre image)
    for _ in range(6):  # 6 lignes vides
        table_data.append([
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style)
        ])
    
    # Créer le tableau avec les bonnes largeurs
    main_table = Table(table_data, colWidths=[8*cm, 3.5*cm, 2*cm, 3*cm])
    
    # Style du tableau identique à votre image
    main_table.setStyle(TableStyle([
        # En-tête avec fond bleu
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_HEADER_BLEU),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        
        # Bordures grises pour tout le tableau
        ('GRID', (0, 0), (-1, -1), 0.5, COULEUR_BORDURE_GRIS),
        
        # Alignements
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),   # Prix unitaire
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Quantité
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Total HT
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        
        # Alignement vertical
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==========================================
    # 4. TOTAUX - Style exact de votre image
    # ==========================================
    
    # Calculer les totaux
    total_ht = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data.get('items', []))
    tva = total_ht * 0.20  # 20% de TVA
    total_ttc = total_ht + tva
    
    # Style pour les totaux
    total_style = ParagraphStyle('TotalStyle', fontSize=10, textColor=COULEUR_TEXTE_NOIR, alignment=TA_RIGHT)
    total_bold_style = ParagraphStyle('TotalBoldStyle', fontSize=11, textColor=COULEUR_TEXTE_NOIR, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    
    # Tableau des totaux (aligné à droite)
    totals_data = [
        ['', '', 'Total HT', f"{total_ht:.2f} €"],
        ['', '', 'TVA', f"{tva:.2f} €"]
    ]
    
    totals_table = Table(totals_data, colWidths=[8*cm, 3.5*cm, 3*cm, 2*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 3*mm))
    
    # Total TTC dans un encadré bleu (comme dans votre image)
    ttc_data = [['', '', 'Total TTC', f"{total_ttc:.2f} €"]]
    ttc_table = Table(ttc_data, colWidths=[8*cm, 3.5*cm, 3*cm, 2*cm])
    ttc_table.setStyle(TableStyle([
        ('BACKGROUND', (2, 0), (-1, 0), COULEUR_HEADER_BLEU),
        ('TEXTCOLOR', (2, 0), (-1, 0), colors.white),
        ('FONTNAME', (2, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, 0), 11),
        ('ALIGN', (2, 0), (-1, 0), 'RIGHT'),
        ('TOPPADDING', (2, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (2, 0), (-1, 0), 6),
        ('GRID', (2, 0), (-1, 0), 0.5, COULEUR_BORDURE_GRIS),
    ]))
    
    elements.append(ttc_table)
    elements.append(Spacer(1, 15*mm))
    
    # ==========================================
    # 5. SIGNATURE CLIENT
    # ==========================================
    
    signature_style = ParagraphStyle('SignatureStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    
    signature_data = [
        [Paragraph("Signature du client<br/>(précédé de la mention \"Bon pour accord\")", signature_style), '']
    ]
    
    signature_table = Table(signature_data, colWidths=[9*cm, 9*cm])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 15*mm))
    
    # ==========================================
    # 6. SECTIONS FINALES - "Informations" et "Détails bancaires"
    # ==========================================
    
    section_header_style = ParagraphStyle(
        'SectionHeaderStyle',
        fontSize=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    section_content_style = ParagraphStyle('SectionContentStyle', fontSize=9, textColor=COULEUR_TEXTE_NOIR)
    
    # Contenu des sections
    info_content = "Informations complémentaires..."
    
    bank_content = f"""Banque: {devis_data.get('banque_nom', 'Qonto')}<br/>
IBAN: {devis_data.get('banque_iban', 'FR761699000013234410233663')}<br/>
BIC: {devis_data.get('banque_bic', 'QNTOFR21XXX')}"""
    
    # Tableau pour les deux sections côte à côte
    sections_data = [
        # En-têtes
        [
            Paragraph("Informations", section_header_style),
            Paragraph("Détails bancaires", section_header_style)
        ],
        # Contenus
        [
            Paragraph(info_content, section_content_style),
            Paragraph(bank_content, section_content_style)
        ]
    ]
    
    sections_table = Table(sections_data, colWidths=[9*cm, 9*cm])
    sections_table.setStyle(TableStyle([
        # En-têtes avec fond bleu
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_HEADER_BLEU),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(sections_table)
    elements.append(Spacer(1, 10*mm))
    
    # ==========================================
    # 7. MESSAGE FINAL "MERCI BEAUCOUP !"
    # ==========================================
    
    thank_you_style = ParagraphStyle(
        'ThankYouStyle',
        fontSize=14,
        textColor=COULEUR_HEADER_BLEU,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Merci beaucoup !", thank_you_style))
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test si lancé directement
if __name__ == "__main__":
    test_data = {
        "numero": "2025_0927_001",
        "date_emission": "27/09/2025",
        "date_expiration": "27/10/2025",
        "date_debut": "01/10/2025",
        "fournisseur_nom": "INFINYTIA",
        "client_nom": "BMW France",
        "client_adresse": "3 Avenue Ampère",
        "logo_url": "https://via.placeholder.com/150x100/4a90b8/ffffff?text=LOGO",  # Logo de test
        "banque_nom": "Qonto",
        "banque_iban": "FR761699000013234410233663",
        "banque_bic": "QNTOFR21XXX",
        "items": [
            {
                "description": "Automatisation des e-mails marketing et commerciaux",
                "prix_unitaire": 1000.0,
                "quantite": 1
            },
            {
                "description": "Automatisation WhatsApp pour envoi de véhicules avec reconnaissance de plaques",
                "prix_unitaire": 2000.0,
                "quantite": 1
            },
            {
                "description": "Automatisation de publication Linkedin",
                "prix_unitaire": 1500.0,
                "quantite": 1
            }
        ]
    }
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF test généré : {filename}")
