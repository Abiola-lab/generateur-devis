# pdf_generator_students.py - Version finale corrigée
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import os
import requests
from io import BytesIO

# Couleurs du design épuré Infinytia
COULEUR_GRIS_FONCE = colors.HexColor('#2c3e50')
COULEUR_GRIS_MOYEN = colors.HexColor('#7f8c8d')
COULEUR_GRIS_CLAIR = colors.HexColor('#ecf0f1')
COULEUR_BORDURE = colors.HexColor('#bdc3c7')

def download_logo(logo_url):
    """Télécharger et traiter le logo depuis une URL - VERSION CORRIGÉE"""
    if not logo_url:
        return None
    
    try:
        print(f"Téléchargement du logo depuis: {logo_url}")
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            
            # Redimensionner le logo
            max_height = 2 * cm
            logo.drawHeight = max_height
            logo.drawWidth = max_height * logo.imageWidth / logo.imageHeight
            
            # Largeur maximale
            max_width = 4 * cm
            if logo.drawWidth > max_width:
                logo.drawWidth = max_width
                logo.drawHeight = max_width * logo.imageHeight / logo.imageWidth
            
            print(f"Logo téléchargé avec succès - Taille: {logo.drawWidth}x{logo.drawHeight}")
            return logo
            
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None
    
    return None

class CleanCanvas(canvas.Canvas):
    """Canvas avec footer personnalisé"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.company_name = ""
        self.doc_number = ""
    
    def showPage(self):
        self.draw_footer()
        canvas.Canvas.showPage(self)
    
    def draw_footer(self):
        """Dessiner le footer en bas de page"""
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        
        # Footer gauche : nom entreprise
        self.drawString(2*cm, 1.5*cm, f"{self.company_name}, SAS")
        
        # Footer droite : numéro document
        self.drawRightString(A4[0] - 2*cm, 1.5*cm, f"{self.doc_number} · 1/2")
        
        self.restoreState()

def generate_student_style_devis(devis_data):
    """Générer un devis PDF avec le design épuré d'Infinytia - UTILISE TON CODE ORIGINAL"""
    
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Canvas personnalisé
    def make_canvas(*args, **kwargs):
        canvas_obj = CleanCanvas(*args, **kwargs)
        canvas_obj.company_name = devis_data.get('fournisseur_nom', 'INFINYTIA')
        canvas_obj.doc_number = devis_data.get('numero', '')
        return canvas_obj
    
    # Document A4
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=30*mm,
        canvasmaker=make_canvas
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # 1. EN-TÊTE : "Devis" + Logo
    logo = download_logo(devis_data.get('logo_url', ''))
    
    devis_title_style = ParagraphStyle(
        'DevisTitleStyle',
        fontSize=24,
        textColor=COULEUR_GRIS_FONCE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    if logo:
        header_data = [[Paragraph("Devis", devis_title_style), logo]]
        header_table = Table(header_data, colWidths=[14*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
    else:
        header_data = [[Paragraph("Devis", devis_title_style)]]
        header_table = Table(header_data, colWidths=[18*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))
    
    # 2. INFORMATIONS DU DEVIS
    info_label_style = ParagraphStyle('InfoLabelStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold')
    info_value_style = ParagraphStyle('InfoValueStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE)
    
    devis_info_data = [
        [Paragraph("Numéro de devis", info_label_style), Paragraph(devis_data.get('numero', ''), info_value_style)],
        [Paragraph("Date d'émission", info_label_style), Paragraph(devis_data.get('date_emission', ''), info_value_style)],
        [Paragraph("Date d'expiration", info_label_style), Paragraph(devis_data.get('date_expiration', ''), info_value_style)]
    ]
    
    devis_info_table = Table(devis_info_data, colWidths=[4*cm, 6*cm])
    devis_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(devis_info_table)
    elements.append(Spacer(1, 8*mm))
    
    # 3. FOURNISSEUR ET CLIENT
    address_style = ParagraphStyle('AddressStyle', fontSize=9, textColor=COULEUR_GRIS_FONCE)
    
    fournisseur_content = f"""<b>{devis_data.get('fournisseur_nom', 'INFINYTIA')}</b><br/>
{devis_data.get('fournisseur_adresse', '61 Rue De Lyon')}<br/>
{devis_data.get('fournisseur_ville', '75012 Paris, FR')}<br/>
{devis_data.get('fournisseur_email', 'contact@infinytia.com')}<br/>
{devis_data.get('fournisseur_siret', '93968736400017')}"""
    
    client_content = f"""<b>{devis_data.get('client_nom', '')}</b><br/>
{devis_data.get('client_email', '')}<br/>"""
    
    if devis_data.get('client_tva'):
        client_content += f"Numéro de TVA: {devis_data.get('client_tva', '')}"
    
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
    
    # 4. TEXTE D'INTRODUCTION
    if devis_data.get('texte_intro'):
        intro_style = ParagraphStyle('IntroStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE, alignment=TA_JUSTIFY)
        elements.append(Paragraph(devis_data.get('texte_intro'), intro_style))
        elements.append(Spacer(1, 8*mm))
    
    # 5. EN-TÊTE ARTICLES
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
        ('BACKGROUND', (0, 0), (-1, -1), COULEUR_GRIS_FONCE),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
    ]))
    
    elements.append(table_header)
    
    # 6. ARTICLES EN LIGNES
    article_style = ParagraphStyle('ArticleStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold')
    detail_style = ParagraphStyle('DetailStyle', fontSize=9, textColor=COULEUR_GRIS_FONCE, leftIndent=0, alignment=TA_JUSTIFY)
    
    for item in devis_data.get('items', []):
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        tva_taux = item.get('tva_taux', 20)
        total_ht = prix_unitaire * quantite
        
        # Ligne principale article
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
            ('GRID', (0, 0), (-1, -1), 0.5, COULEUR_BORDURE),
        ]))
        
        elements.append(article_table)
        
        # Détails de l'article
        if item.get('details'):
            details_text = ""
            for detail in item.get('details', []):
                details_text += f"{detail}<br/>"
            
            elements.append(Paragraph(details_text, detail_style))
        
        elements.append(Spacer(1, 5*mm))
    
    elements.append(Spacer(1, 5*mm))
    
    # 7. TOTAUX
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
        ('LINEBELOW', (1, 2), (-1, 2), 1, COULEUR_GRIS_FONCE),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))
    
    # 8. CONDITIONS DE PAIEMENT
    section_title_style = ParagraphStyle('SectionTitleStyle', fontSize=12, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold')
    section_content_style = ParagraphStyle('SectionContentStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE)
    small_text_style = ParagraphStyle('SmallTextStyle', fontSize=8, textColor=COULEUR_GRIS_MOYEN)
    
    elements.append(Paragraph("CONDITIONS DE PAIEMENT", section_title_style))
    elements.append(Paragraph(devis_data.get('conditions_paiement', '50% à la commande, 50% à la livraison'), section_content_style))
    elements.append(Spacer(1, 3*mm))
    
    if devis_data.get('penalites_retard'):
        elements.append(Paragraph(devis_data.get('penalites_retard'), small_text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    # 9. COORDONNÉES BANCAIRES
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
    
    # 10. BON POUR ACCORD
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
    
    # Construire le PDF
    doc.build(elements)
    return filename

# Test
if __name__ == "__main__":
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
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF généré : {filename}")
