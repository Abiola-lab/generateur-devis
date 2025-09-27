# pdf_generator_students.py - Version modèle exact
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import requests
from io import BytesIO

def download_logo(logo_url):
    """Télécharger le logo"""
    if not logo_url:
        return None
    
    try:
        print(f"Téléchargement logo: {logo_url}")
        response = requests.get(logo_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            # Logo rond - taille fixe
            logo.drawHeight = 3 * cm
            logo.drawWidth = 3 * cm
            print("Logo téléchargé avec succès")
            return logo
    except Exception as e:
        print(f"Erreur logo: {e}")
    
    return None

def generate_student_style_devis(devis_data):
    """Générer un devis PDF selon le modèle exact fourni"""
    
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    elements = []
    
    # 1. EN-TÊTE : Titre + Logo
    title_style = ParagraphStyle(
        'TitleStyle',
        fontSize=36,
        textColor=colors.HexColor('#4472C4'),  # Bleu comme le modèle
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    # Créer le logo ou placeholder
    logo = download_logo(devis_data.get('logo_url', ''))
    if not logo:
        # Placeholder logo gris rond
        logo_style = ParagraphStyle('LogoPlaceholder', fontSize=24, textColor=colors.grey, alignment=TA_CENTER, backColor=colors.lightgrey)
        logo = Paragraph("Logo", logo_style)
    
    # En-tête avec titre et logo
    header_data = [
        [Paragraph("Devis", title_style), logo]
    ]
    
    header_table = Table(header_data, colWidths=[14*cm, 4*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 15*mm))
    
    # 2. VENDEUR ET CLIENT
    label_style = ParagraphStyle('LabelStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.black)
    content_style = ParagraphStyle('ContentStyle', fontSize=10, textColor=colors.black, leading=12)
    
    # Données vendeur/client
    vendeur_content = f"""{devis_data.get('fournisseur_nom', 'Mon Entreprise')}<br/>
{devis_data.get('fournisseur_adresse', '22, Avenue Voltaire')}<br/>
{devis_data.get('fournisseur_ville', '13000 Marseille')}"""
    
    client_content = f"""{devis_data.get('client_nom', '')}<br/>
{devis_data.get('client_adresse', '')}<br/>
{devis_data.get('client_ville', '')}"""
    
    vendeur_client_data = [
        [
            Paragraph("Vendeur", label_style),
            Paragraph("Client", label_style)
        ],
        [
            Paragraph(vendeur_content, content_style),
            Paragraph(client_content, content_style)
        ]
    ]
    
    vendeur_client_table = Table(vendeur_client_data, colWidths=[9*cm, 9*cm])
    vendeur_client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(vendeur_client_table)
    elements.append(Spacer(1, 10*mm))
    
    # 3. DATES ET RÉFÉRENCES
    dates_data = [
        [
            Paragraph("Date :", label_style),
            Paragraph("Référence du devis :", label_style),
            Paragraph("Date de validité :", label_style)
        ],
        [
            Paragraph(devis_data.get('date_emission', ''), content_style),
            Paragraph(devis_data.get('numero', ''), content_style),
            Paragraph(devis_data.get('date_expiration', ''), content_style)
        ]
    ]
    
    dates_table = Table(dates_data, colWidths=[6*cm, 6*cm, 6*cm])
    dates_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(dates_table)
    elements.append(Spacer(1, 10*mm))
    
    # 4. INFORMATIONS ADDITIONNELLES (optionnel)
    if devis_data.get('texte_intro'):
        elements.append(Paragraph("Informations additionnelles :", label_style))
        elements.append(Paragraph(devis_data.get('texte_intro'), content_style))
        elements.append(Spacer(1, 10*mm))
    
    # 5. TABLEAU DES ARTICLES
    # En-tête du tableau (bleu comme le modèle)
    header_style = ParagraphStyle('HeaderStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
    
    # Données du tableau
    table_data = []
    
    # Headers
    headers = [
        Paragraph("Description", header_style),
        Paragraph("Quantité", header_style),
        Paragraph("Unité", header_style),
        Paragraph("Prix unitaire HT", header_style),
        Paragraph("% TVA", header_style),
        Paragraph("Total TVA", header_style),
        Paragraph("Total TTC", header_style)
    ]
    table_data.append(headers)
    
    # Style pour les cellules de données
    cell_style = ParagraphStyle('CellStyle', fontSize=9, textColor=colors.black, alignment=TA_CENTER)
    cell_style_left = ParagraphStyle('CellStyleLeft', fontSize=9, textColor=colors.black, alignment=TA_LEFT)
    
    # Articles
    total_ht_calc = 0
    total_tva_calc = 0
    total_ttc_calc = 0
    
    for item in devis_data.get('items', []):
        prix_unitaire = float(item.get('prix_unitaire', 0))
        quantite = int(item.get('quantite', 1))
        tva_taux = float(item.get('tva_taux', 20))
        
        total_ht_item = prix_unitaire * quantite
        total_tva_item = total_ht_item * (tva_taux / 100)
        total_ttc_item = total_ht_item + total_tva_item
        
        total_ht_calc += total_ht_item
        total_tva_calc += total_tva_item
        total_ttc_calc += total_ttc_item
        
        row = [
            Paragraph(item.get('description', ''), cell_style_left),
            Paragraph(str(quantite), cell_style),
            Paragraph(item.get('unite', 'unité'), cell_style),
            Paragraph(f"{prix_unitaire:.2f} €", cell_style),
            Paragraph(f"{tva_taux:.0f} %", cell_style),
            Paragraph(f"{total_tva_item:.2f} €", cell_style),
            Paragraph(f"{total_ttc_item:.2f} €", cell_style)
        ]
        table_data.append(row)
    
    # Utiliser les totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht_calc = float(devis_data['total_ht'])
    if 'total_tva' in devis_data:
        total_tva_calc = float(devis_data['total_tva'])
    if 'total_ttc' in devis_data:
        total_ttc_calc = float(devis_data['total_ttc'])
    
    # Lignes de totaux
    totals_style = ParagraphStyle('TotalsStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_RIGHT)
    
    # Total HT
    table_data.append([
        '', '', '', '', '',
        Paragraph("Total HT", totals_style),
        Paragraph(f"{total_ht_calc:.2f} €", totals_style)
    ])
    
    # Total TVA  
    table_data.append([
        '', '', '', '', '',
        Paragraph("Total TVA", totals_style),
        Paragraph(f"{total_tva_calc:.2f} €", totals_style)
    ])
    
    # Total TTC (en bleu comme le modèle)
    ttc_style = ParagraphStyle('TTCStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#4472C4'), alignment=TA_RIGHT)
    table_data.append([
        '', '', '', '', '',
        Paragraph("Total TTC", ttc_style),
        Paragraph(f"{total_ttc_calc:.2f} €", ttc_style)
    ])
    
    # Créer le tableau
    main_table = Table(table_data, colWidths=[4*cm, 2*cm, 2*cm, 3*cm, 2*cm, 2.5*cm, 2.5*cm])
    
    # Style du tableau
    num_articles = len(devis_data.get('items', []))
    
    table_style = [
        # En-tête bleu
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
        # Bordures
        ('GRID', (0, 0), (-1, num_articles), 1, colors.black),
        
        # Alignements
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        
        # Totaux en gras
        ('FONTNAME', (0, num_articles + 1), (-1, -1), 'Helvetica-Bold'),
    ]
    
    main_table.setStyle(TableStyle(table_style))
    elements.append(main_table)
    elements.append(Spacer(1, 15*mm))
    
    # 6. SIGNATURE (zone grise)
    signature_style = ParagraphStyle('SignatureStyle', fontSize=10, textColor=colors.black, alignment=TA_CENTER)
    
    signature_data = [
        [Paragraph("Signature du client (précédée de la mention « Bon pour accord »)", signature_style)]
    ]
    
    signature_table = Table(signature_data, colWidths=[18*cm])
    signature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 15*mm))
    
    # 7. FOOTER 3 COLONNES
    footer_style = ParagraphStyle('FooterStyle', fontSize=8, textColor=colors.black, leading=10)
    footer_label_style = ParagraphStyle('FooterLabelStyle', fontSize=8, fontName='Helvetica-Bold', textColor=colors.black)
    
    entreprise_content = f"""{devis_data.get('fournisseur_nom', 'Mon Entreprise')}<br/>
{devis_data.get('fournisseur_adresse', '22, Avenue Voltaire')}<br/>
{devis_data.get('fournisseur_ville', '13000 Marseille')}<br/>
N° Siret ou Siren : {devis_data.get('fournisseur_siret', '1234567')}<br/>
N° TVA intra : {devis_data.get('fournisseur_tva', 'FR0X 999999999')}"""
    
    coordonnees_content = f"""Téléphone : {devis_data.get('fournisseur_telephone', '+33 4 92 59 59 59')}<br/>
E-mail : {devis_data.get('fournisseur_email', 'contact@monentreprise.fr')}<br/>
www.monentreprise.com"""
    
    banque_content = f"""Banque: {devis_data.get('banque_nom', 'NP Partbox')}<br/>
IBAN: {devis_data.get('banque_iban', 'FR23 4112 4598 4508 23')}<br/>
BIC/Swift: {devis_data.get('banque_bic', 'FRHCCXX1051')}"""
    
    footer_data = [
        [
            Paragraph(entreprise_content, footer_style),
            Paragraph(coordonnees_content, footer_style),
            Paragraph(banque_content, footer_style)
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[6*cm, 6*cm, 6*cm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
    ]))
    
    elements.append(footer_table)
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test
if __name__ == "__main__":
    test_data = {
        "numero": "143",
        "date_emission": "2.6.2021",
        "date_expiration": "16.6.2021",
        "logo_url": "https://example.com/logo.png",
        "fournisseur_nom": "Mon Entreprise",
        "fournisseur_adresse": "22, Avenue Voltaire",
        "fournisseur_ville": "13000 Marseille",
        "fournisseur_email": "contact@monentreprise.fr",
        "fournisseur_siret": "1234567",
        "client_nom": "Michel Acheteur",
        "client_adresse": "31, rue de la Forêt",
        "client_ville": "13100 Aix-en-Provence",
        "texte_intro": "Service Après Vente : Garantie 1 an.",
        "items": [
            {
                "description": "Main-d'œuvre",
                "quantite": 5,
                "unite": "h",
                "prix_unitaire": 60.0,
                "tva_taux": 20
            },
            {
                "description": "Produit",
                "quantite": 10,
                "unite": "pcs",
                "prix_unitaire": 105.0,
                "tva_taux": 20
            }
        ]
    }
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF généré : {filename}")
