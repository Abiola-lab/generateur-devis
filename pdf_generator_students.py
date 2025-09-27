# pdf_generator_students.py - Version avec VRAIMENT que des lignes (sauf tableau articles)
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
    """Télécharger le logo - VERSION SIMPLIFIÉE"""
    if not logo_url:
        return None
    
    try:
        print(f"Téléchargement logo: {logo_url}")
        # Headers plus complets pour éviter les blocages
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(logo_url, timeout=15, headers=headers, verify=False, allow_redirects=True)
        response.raise_for_status()
        
        if response.status_code == 200 and len(response.content) > 100:  # Vérifier qu'on a bien du contenu
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            # Taille simple
            logo.drawHeight = 3 * cm
            logo.drawWidth = 3 * cm
            print(f"Logo téléchargé avec succès - Taille: {len(response.content)} bytes")
            return logo
        else:
            print(f"Contenu invalide: {len(response.content)} bytes")
            
    except Exception as e:
        print(f"Erreur logo: {str(e)}")
    
    print("Utilisation du placeholder logo")
    return None

def generate_student_style_devis(devis_data):
    """Générer un devis PDF - QUE DES LIGNES SAUF TABLEAU ARTICLES"""
    
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
    
    # STYLES
    title_style = ParagraphStyle('TitleStyle', fontSize=36, textColor=colors.HexColor('#4472C4'), fontName='Helvetica-Bold', alignment=TA_LEFT, spaceAfter=10*mm)
    logo_style = ParagraphStyle('LogoStyle', fontSize=18, textColor=colors.grey, alignment=TA_RIGHT, backColor=colors.lightgrey, spaceAfter=10*mm)
    label_style = ParagraphStyle('LabelStyle', fontSize=11, fontName='Helvetica-Bold', textColor=colors.black, spaceAfter=3*mm)
    content_style = ParagraphStyle('ContentStyle', fontSize=10, textColor=colors.black, spaceAfter=2*mm)
    
    # 1. TITRE ET LOGO EN HAUT
    # Essayer de télécharger le logo
    logo = download_logo(devis_data.get('logo_url', ''))
    
    if logo:
        # Table simple juste pour aligner titre et logo
        header_data = [[Paragraph("Devis", title_style), logo]]
        header_table = Table(header_data, colWidths=[14*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
    else:
        # Juste le titre si pas de logo
        elements.append(Paragraph("Devis", title_style))
        elements.append(Paragraph("Logo", logo_style))
    
    elements.append(Spacer(1, 10*mm))
    
    # 2. VENDEUR - LIGNES SIMPLES
    elements.append(Paragraph("Vendeur", label_style))
    elements.append(Paragraph(devis_data.get('fournisseur_nom', 'Mon Entreprise'), content_style))
    elements.append(Paragraph(devis_data.get('fournisseur_adresse', '22, Avenue Voltaire'), content_style))
    elements.append(Paragraph(devis_data.get('fournisseur_ville', '13000 Marseille'), content_style))
    elements.append(Spacer(1, 5*mm))
    
    # 3. CLIENT - LIGNES SIMPLES  
    elements.append(Paragraph("Client", label_style))
    elements.append(Paragraph(devis_data.get('client_nom', ''), content_style))
    if devis_data.get('client_adresse'):
        elements.append(Paragraph(devis_data.get('client_adresse', ''), content_style))
    if devis_data.get('client_ville'):
        elements.append(Paragraph(devis_data.get('client_ville', ''), content_style))
    elements.append(Spacer(1, 8*mm))
    
    # 4. DATES - LIGNES SIMPLES
    elements.append(Paragraph(f"Date : {devis_data.get('date_emission', '')}", content_style))
    elements.append(Paragraph(f"Référence du devis : {devis_data.get('numero', '')}", content_style))
    elements.append(Paragraph(f"Date de validité : {devis_data.get('date_expiration', '')}", content_style))
    elements.append(Spacer(1, 10*mm))
    
    # 5. INFORMATIONS ADDITIONNELLES
    if devis_data.get('texte_intro'):
        elements.append(Paragraph("Informations additionnelles :", label_style))
        elements.append(Paragraph(devis_data.get('texte_intro'), content_style))
        elements.append(Spacer(1, 10*mm))
    
    # 6. TABLEAU DES ARTICLES (LE SEUL TABLEAU)
    header_style = ParagraphStyle('HeaderStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
    cell_style = ParagraphStyle('CellStyle', fontSize=9, textColor=colors.black, alignment=TA_CENTER)
    cell_style_left = ParagraphStyle('CellStyleLeft', fontSize=9, textColor=colors.black, alignment=TA_LEFT)
    
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
    
    # Utiliser totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht_calc = float(devis_data['total_ht'])
    if 'total_tva' in devis_data:
        total_tva_calc = float(devis_data['total_tva'])
    if 'total_ttc' in devis_data:
        total_ttc_calc = float(devis_data['total_ttc'])
    
    # Totaux dans le tableau
    totals_style = ParagraphStyle('TotalsStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_RIGHT)
    ttc_style = ParagraphStyle('TTCStyle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#4472C4'), alignment=TA_RIGHT)
    
    table_data.append(['', '', '', '', '', Paragraph("Total HT", totals_style), Paragraph(f"{total_ht_calc:.2f} €", totals_style)])
    table_data.append(['', '', '', '', '', Paragraph("Total TVA", totals_style), Paragraph(f"{total_tva_calc:.2f} €", totals_style)])
    table_data.append(['', '', '', '', '', Paragraph("Total TTC", ttc_style), Paragraph(f"{total_ttc_calc:.2f} €", ttc_style)])
    
    # Créer le tableau
    main_table = Table(table_data, colWidths=[4*cm, 2*cm, 2*cm, 3*cm, 2*cm, 2.5*cm, 2.5*cm])
    
    num_articles = len(devis_data.get('items', []))
    
    main_table.setStyle(TableStyle([
        # En-tête bleu
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        # Bordures articles
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
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 15*mm))
    
    # 7. SIGNATURE - LIGNE SIMPLE
    signature_style = ParagraphStyle('SignatureStyle', fontSize=10, textColor=colors.black, alignment=TA_CENTER, backColor=colors.lightgrey, borderPadding=20)
    elements.append(Paragraph("Signature du client (précédée de la mention « Bon pour accord »)", signature_style))
    elements.append(Spacer(1, 15*mm))
    
    # 8. FOOTER - LIGNES SIMPLES (pas de tableau)
    footer_style = ParagraphStyle('FooterStyle', fontSize=8, textColor=colors.white, leading=10, backColor=colors.HexColor('#4472C4'), borderPadding=8)
    
    # Colonne 1 - Entreprise
    elements.append(Paragraph(f"{devis_data.get('fournisseur_nom', 'Mon Entreprise')}", footer_style))
    elements.append(Paragraph(f"{devis_data.get('fournisseur_adresse', '22, Avenue Voltaire')}", footer_style))
    elements.append(Paragraph(f"{devis_data.get('fournisseur_ville', '13000 Marseille')}", footer_style))
    elements.append(Paragraph(f"N° Siret ou Siren : {devis_data.get('fournisseur_siret', '1234567')}", footer_style))
    elements.append(Paragraph(f"N° TVA intra : {devis_data.get('fournisseur_tva', 'FR0X 999999999')}", footer_style))
    
    elements.append(Spacer(1, 5*mm))
    
    # Colonne 2 - Coordonnées
    elements.append(Paragraph(f"Téléphone : {devis_data.get('fournisseur_telephone', '+33 4 92 59 59 59')}", footer_style))
    elements.append(Paragraph(f"E-mail : {devis_data.get('fournisseur_email', 'contact@monentreprise.fr')}", footer_style))
    elements.append(Paragraph("www.monentreprise.com", footer_style))
    
    elements.append(Spacer(1, 5*mm))
    
    # Colonne 3 - Banque
    elements.append(Paragraph(f"Banque: {devis_data.get('banque_nom', 'Qonto')}", footer_style))
    elements.append(Paragraph(f"IBAN: {devis_data.get('banque_iban', 'FR7616958000013234941023663')}", footer_style))
    elements.append(Paragraph(f"BIC/Swift: {devis_data.get('banque_bic', 'QNTOFRP1XXX')}", footer_style))
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test
if __name__ == "__main__":
    test_data = {
        "numero": "143",
        "date_emission": "2.6.2021", 
        "date_expiration": "16.6.2021",
        "logo_url": "https://via.placeholder.com/150x150/4472C4/FFFFFF?text=LOGO",  # URL de test qui marche
        "fournisseur_nom": "Mon Entreprise",
        "fournisseur_adresse": "22, Avenue Voltaire",
        "fournisseur_ville": "13000 Marseille",
        "client_nom": "Michel Acheteur",
        "client_adresse": "31, rue de la Forêt", 
        "client_ville": "13100 Aix-en-Provence",
        "items": [
            {
                "description": "Main-d'œuvre",
                "quantite": 5,
                "prix_unitaire": 60.0,
                "tva_taux": 20
            }
        ]
    }
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF généré : {filename}")
