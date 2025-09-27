# pdf_generator_students.py - Générateur PDF avec le style de formation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
from datetime import datetime

# Couleurs du design (comme sur votre image)
COULEUR_HEADER = colors.HexColor('#4a90b8')  # Bleu de l'en-tête "Devis N°"
COULEUR_TEXTE = colors.HexColor('#2c3e50')   # Couleur du texte principal
COULEUR_BORDURE = colors.HexColor('#bdc3c7') # Couleur des bordures

def generate_student_style_devis(devis_data):
    """
    Générer un devis PDF avec le style exact de l'image de formation
    """
    # Créer le dossier generated s'il n'existe pas
    os.makedirs('generated', exist_ok=True)
    
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Configuration du document A4
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Style pour l'en-tête "Devis N°"
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0
    )
    
    # 1. EN-TÊTE "DEVIS N°" - Aligné à droite avec fond bleu
    header_table = Table([
        ['', Paragraph(f"Devis N°", header_style)]
    ], colWidths=[14*cm, 4*cm])
    
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), COULEUR_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (1, 0), (1, 0), 8),
        ('BOTTOMPADDING', (1, 0), (1, 0), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # Style pour les informations
    info_style = ParagraphStyle('InfoStyle', fontSize=10, textColor=COULEUR_TEXTE)
    
    # 2. SECTION INFORMATIONS - Deux colonnes comme sur l'image
    # Colonne gauche : Informations du devis
    left_info = [
        ['Date du devis :', devis_data.get('date_emission', '')],
        ['Date de validité du devis :', devis_data.get('date_expiration', '')],
        ['Émis par :', devis_data.get('fournisseur_nom', '')],
        ['Date de début de la prestation :', devis_data.get('date_debut', '')]
    ]
    
    # Colonne droite : Informations destinataire
    right_info = [
        ['Nom du destinataire :', devis_data.get('client_nom', '')],
        ['Adresse :', devis_data.get('client_adresse', '')]
    ]
    
    # Créer le tableau d'informations
    max_rows = max(len(left_info), len(right_info))
    combined_info = []
    
    for i in range(max_rows):
        left_row = left_info[i] if i < len(left_info) else ['', '']
        right_row = right_info[i] if i < len(right_info) else ['', '']
        
        combined_info.append([
            Paragraph(f"<b>{left_row[0]}</b>", info_style),
            Paragraph(left_row[1], info_style),
            Paragraph(f"<b>{right_row[0]}</b>", info_style),
            Paragraph(right_row[1], info_style)
        ])
    
    info_table = Table(combined_info, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15*mm))
    
    # 3. TABLEAU PRINCIPAL DES ARTICLES
    # Style pour l'en-tête du tableau
    table_header_style = ParagraphStyle(
        'TableHeader',
        fontSize=11,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # En-tête du tableau (exactement comme sur l'image)
    articles_data = [
        [
            Paragraph("Description", table_header_style),
            Paragraph("Prix unitaire HT", table_header_style),
            Paragraph("Qté", table_header_style),
            Paragraph("Total HT", table_header_style)
        ]
    ]
    
    # Styles pour les données
    data_style = ParagraphStyle('DataStyle', fontSize=10, textColor=COULEUR_TEXTE)
    data_style_center = ParagraphStyle('DataStyleCenter', fontSize=10, textColor=COULEUR_TEXTE, alignment=TA_CENTER)
    data_style_right = ParagraphStyle('DataStyleRight', fontSize=10, textColor=COULEUR_TEXTE, alignment=TA_RIGHT)
    
    # Ajouter les articles
    for item in devis_data.get('items', []):
        total_ligne = item.get('prix_unitaire', 0) * item.get('quantite', 1)
        articles_data.append([
            Paragraph(item.get('description', ''), data_style),
            Paragraph(f"{item.get('prix_unitaire', 0):.2f} €", data_style_right),
            Paragraph(str(item.get('quantite', 1)), data_style_center),
            Paragraph(f"{total_ligne:.2f} €", data_style_right)
        ])
    
    # Ajouter des lignes vides pour l'espace (comme sur l'image)
    for _ in range(5):
        articles_data.append(['', '', '', ''])
    
    # Créer le tableau des articles
    articles_table = Table(articles_data, colWidths=[8*cm, 3*cm, 2*cm, 3*cm])
    
    # Style du tableau (avec en-tête bleu)
    articles_table.setStyle(TableStyle([
        # En-tête avec fond bleu
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        
        # Bordures pour tout le tableau
        ('GRID', (0, 0), (-1, -1), 1, COULEUR_BORDURE),
        
        # Alignements
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Prix unitaire
        ('ALIGN', (2, 1), (2, -1), 'CENTER'), # Quantité
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Total HT
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        
        # Alignement vertical
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(articles_table)
    elements.append(Spacer(1, 15*mm))
    
    # 4. SECTION TOTAUX
    # Calculer les totaux
    total_ht = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data.get('items', []))
    tva = total_ht * 0.20  # 20% de TVA
    total_ttc = total_ht + tva
    
    # Totaux partiels (alignés à droite)
    totals_style = ParagraphStyle('TotalsStyle', fontSize=11, textColor=COULEUR_TEXTE, alignment=TA_RIGHT)
    
    totals_data = [
        ['', 'Total HT', f"{total_ht:.2f} €"],
        ['', 'TVA', f"{tva:.2f} €"],
        ['', '', '']  # Ligne vide
    ]
    
    totals_table = Table(totals_data, colWidths=[11*cm, 3*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('FONTNAME', (1, 0), (1, 1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 1), 'Helvetica-Bold'),
    ]))
    
    elements.append(totals_table)
    
    # Total TTC dans un encadré bleu (comme sur l'image)
    ttc_data = [['Total TTC', f"{total_ttc:.2f} €"]]
    ttc_table = Table(ttc_data, colWidths=[14*cm, 4*cm])
    ttc_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), COULEUR_HEADER),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, COULEUR_BORDURE),
    ]))
    
    elements.append(ttc_table)
    elements.append(Spacer(1, 20*mm))
    
    # 5. SIGNATURE CLIENT
    signature_style = ParagraphStyle('SignatureStyle', fontSize=10, textColor=COULEUR_TEXTE)
    
    signature_data = [[
        Paragraph("Signature du client<br/>(précédé de la mention \"Bon pour accord\")", signature_style),
        ''
    ]]
    
    signature_table = Table(signature_data, colWidths=[9*cm, 9*cm])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 15*mm))
    
    # 6. SECTIONS FINALES - "Informations" et "Détails bancaires" côte à côte
    section_style = ParagraphStyle('SectionStyle', fontSize=10, textColor=COULEUR_TEXTE)
    section_header = ParagraphStyle('SectionHeader', fontSize=11, textColor=colors.white, 
                                   fontName='Helvetica-Bold', alignment=TA_CENTER)
    
    # Contenu des sections
    info_content = """Informations complémentaires..."""
    
    bank_content = f"""Banque: {devis_data.get('banque_nom', 'BNP Paribas')}<br/>
IBAN: {devis_data.get('banque_iban', 'FR76 3000 4008 2800 0123 4567 890')}<br/>
BIC: {devis_data.get('banque_bic', 'BNPAFRPPXXX')}"""
    
    # Tableau pour les deux sections côte à côte
    bottom_sections = [
        [
            Table([[Paragraph("Informations", section_header)]], colWidths=[8.5*cm]),
            Table([[Paragraph("Détails bancaires", section_header)]], colWidths=[8.5*cm])
        ],
        [
            Paragraph(info_content, section_style),
            Paragraph(bank_content, section_style)
        ]
    ]
    
    bottom_table = Table(bottom_sections, colWidths=[9*cm, 9*cm])
    bottom_table.setStyle(TableStyle([
        # En-têtes colorés
        ('BACKGROUND', (0, 0), (0, 0), COULEUR_HEADER),
        ('BACKGROUND', (1, 0), (1, 0), COULEUR_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(bottom_table)
    elements.append(Spacer(1, 10*mm))
    
    # 7. MESSAGE FINAL "MERCI BEAUCOUP !"
    thank_you_style = ParagraphStyle(
        'ThankYouStyle',
        fontSize=14,
        textColor=COULEUR_HEADER,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Merci beaucoup !", thank_you_style))
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test rapide si on lance le fichier directement
if __name__ == "__main__":
    # Données de test
    test_data = {
        "numero": "TEST-001",
        "date_emission": "27/09/2024",
        "date_expiration": "27/10/2024",
        "date_debut": "01/10/2024",
        "fournisseur_nom": "Formation Web",
        "client_nom": "Client Test",
        "client_adresse": "123 Rue Test, 75001 Paris",
        "items": [
            {"description": "Formation développement", "prix_unitaire": 500, "quantite": 2},
            {"description": "Support technique", "prix_unitaire": 150, "quantite": 1}
        ]
    }
    
    filename = generate_student_style_devis(test_data)
    print(f"Test PDF généré : {filename}")
