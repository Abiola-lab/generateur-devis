# pdf_generator_students.py - Version VRAIMENT sans tableaux, que des lignes
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
import os
import requests
from io import BytesIO

# Couleurs simples
COULEUR_GRIS_FONCE = colors.HexColor('#2c3e50')
COULEUR_GRIS_MOYEN = colors.HexColor('#7f8c8d')

def download_logo(logo_url):
    """Télécharger le logo depuis une URL - VERSION SIMPLE"""
    if not logo_url:
        return None
    
    try:
        print(f"Téléchargement logo: {logo_url}")
        response = requests.get(logo_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            # Taille fixe simple
            logo.drawHeight = 2 * cm
            logo.drawWidth = 4 * cm
            print("Logo téléchargé avec succès")
            return logo
    except Exception as e:
        print(f"Erreur logo: {e}")
    
    return None

def generate_student_style_devis(devis_data):
    """Générer un devis PDF SIMPLE - QUE DES LIGNES DE TEXTE"""
    
    os.makedirs('generated', exist_ok=True)
    filename = os.path.join('generated', f'devis_{devis_data["numero"]}.pdf')
    
    # Document simple
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    
    elements = []
    
    # 1. LOGO EN HAUT À DROITE (si présent)
    if devis_data.get('logo_url'):
        logo = download_logo(devis_data['logo_url'])
        if logo:
            # Style pour aligner le logo à droite
            logo_style = ParagraphStyle('LogoStyle', alignment=TA_RIGHT)
            elements.append(Paragraph("", logo_style))  # Ligne vide pour l'alignement
            # Ajouter le logo avec un spacer pour le positionner
            elements.append(Spacer(1, -15*mm))  # Remonte le logo
            elements.append(logo)
            elements.append(Spacer(1, 5*mm))
    
    # 2. TITRE
    title_style = ParagraphStyle(
        'TitleStyle',
        fontSize=24,
        textColor=COULEUR_GRIS_FONCE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=10*mm
    )
    elements.append(Paragraph("Devis", title_style))
    
    # 3. INFORMATIONS DU DEVIS - LIGNES SIMPLES
    info_style = ParagraphStyle('InfoStyle', fontSize=11, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold', spaceAfter=2*mm)
    value_style = ParagraphStyle('ValueStyle', fontSize=11, textColor=COULEUR_GRIS_FONCE, spaceAfter=5*mm)
    
    elements.append(Paragraph("Numéro de devis", info_style))
    elements.append(Paragraph(devis_data.get('numero', ''), value_style))
    
    elements.append(Paragraph("Date d'émission", info_style))
    elements.append(Paragraph(devis_data.get('date_emission', ''), value_style))
    
    elements.append(Paragraph("Date d'expiration", info_style))
    elements.append(Paragraph(devis_data.get('date_expiration', ''), value_style))
    
    elements.append(Spacer(1, 8*mm))
    
    # 4. FOURNISSEUR - LIGNES SIMPLES
    section_style = ParagraphStyle('SectionStyle', fontSize=12, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold', spaceAfter=5*mm)
    text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE, spaceAfter=2*mm)
    
    elements.append(Paragraph("FOURNISSEUR", section_style))
    elements.append(Paragraph(devis_data.get('fournisseur_nom', 'INFINYTIA'), text_style))
    elements.append(Paragraph(devis_data.get('fournisseur_adresse', '61 Rue De Lyon'), text_style))
    elements.append(Paragraph(devis_data.get('fournisseur_ville', '75012 Paris, FR'), text_style))
    elements.append(Paragraph(devis_data.get('fournisseur_email', 'contact@infinytia.com'), text_style))
    elements.append(Paragraph(f"SIRET: {devis_data.get('fournisseur_siret', '93968736400017')}", text_style))
    
    elements.append(Spacer(1, 8*mm))
    
    # 5. CLIENT - LIGNES SIMPLES
    elements.append(Paragraph("CLIENT", section_style))
    elements.append(Paragraph(devis_data.get('client_nom', ''), text_style))
    if devis_data.get('client_adresse'):
        elements.append(Paragraph(devis_data.get('client_adresse', ''), text_style))
    if devis_data.get('client_ville'):
        elements.append(Paragraph(devis_data.get('client_ville', ''), text_style))
    elements.append(Paragraph(devis_data.get('client_email', ''), text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    # 6. ARTICLES - LIGNES SIMPLES
    elements.append(Paragraph("PRESTATIONS", section_style))
    
    article_title_style = ParagraphStyle('ArticleTitleStyle', fontSize=11, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold', spaceAfter=3*mm)
    article_price_style = ParagraphStyle('ArticlePriceStyle', fontSize=10, textColor=COULEUR_GRIS_FONCE, spaceAfter=3*mm)
    detail_style = ParagraphStyle('DetailStyle', fontSize=9, textColor=COULEUR_GRIS_MOYEN, leftIndent=5*mm, spaceAfter=2*mm)
    
    for item in devis_data.get('items', []):
        prix_unitaire = item.get('prix_unitaire', 0)
        quantite = item.get('quantite', 1)
        tva_taux = item.get('tva_taux', 20)
        total_ht = prix_unitaire * quantite
        
        # Titre article
        elements.append(Paragraph(item.get('description', ''), article_title_style))
        
        # Prix en ligne simple
        prix_text = f"Quantité: {quantite} | Prix unitaire: {prix_unitaire:.2f}€ | TVA: {tva_taux}% | Total: {total_ht:.2f}€"
        elements.append(Paragraph(prix_text, article_price_style))
        
        # Détails
        if item.get('details'):
            for detail in item.get('details', []):
                elements.append(Paragraph(f"• {detail}", detail_style))
        
        elements.append(Spacer(1, 5*mm))
    
    # 7. TOTAUX - LIGNES ALIGNÉES À DROITE
    total_style = ParagraphStyle('TotalStyle', fontSize=12, textColor=COULEUR_GRIS_FONCE, alignment=TA_RIGHT, spaceAfter=3*mm)
    total_bold_style = ParagraphStyle('TotalBoldStyle', fontSize=14, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold', alignment=TA_RIGHT, spaceAfter=3*mm)
    
    # Calcul
    total_ht = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data.get('items', []))
    total_tva = sum((item.get('prix_unitaire', 0) * item.get('quantite', 1)) * (item.get('tva_taux', 20) / 100) for item in devis_data.get('items', []))
    total_ttc = total_ht + total_tva
    
    # Utiliser les totaux fournis si disponibles
    if 'total_ht' in devis_data:
        total_ht = devis_data['total_ht']
    if 'total_tva' in devis_data:
        total_tva = devis_data['total_tva']
    if 'total_ttc' in devis_data:
        total_ttc = devis_data['total_ttc']
    
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"Total HT: {total_ht:.2f}€", total_style))
    elements.append(Paragraph(f"Montant total de la TVA: {total_tva:.2f}€", total_style))
    elements.append(Paragraph(f"Total TTC: {total_ttc:.2f}€", total_bold_style))
    
    elements.append(Spacer(1, 15*mm))
    
    # 8. CONDITIONS - LIGNES SIMPLES
    elements.append(Paragraph("CONDITIONS DE PAIEMENT", section_style))
    elements.append(Paragraph(devis_data.get('conditions_paiement', '50% à la commande, 50% à la livraison'), text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    elements.append(Paragraph("COORDONNÉES BANCAIRES", section_style))
    elements.append(Paragraph(f"Banque: {devis_data.get('banque_nom', 'Qonto')}", text_style))
    elements.append(Paragraph(f"IBAN: {devis_data.get('banque_iban', 'FR7616958000013234941023663')}", text_style))
    elements.append(Paragraph(f"BIC: {devis_data.get('banque_bic', 'QNTOFRP1XXX')}", text_style))
    
    elements.append(Spacer(1, 10*mm))
    
    conclusion_text = devis_data.get('texte_conclusion', 'Cette proposition reste valable 30 jours. Nous restons à votre entière disposition pour tout complément d\'information.')
    elements.append(Paragraph(conclusion_text, text_style))
    
    elements.append(Spacer(1, 15*mm))
    
    # 9. SIGNATURE - LIGNE SIMPLE
    signature_style = ParagraphStyle('SignatureStyle', fontSize=11, textColor=COULEUR_GRIS_FONCE, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    elements.append(Paragraph("Bon pour accord", signature_style))
    elements.append(Paragraph("Date et signature:", signature_style))
    
    # Construction du PDF
    doc.build(elements)
    return filename

# Test
if __name__ == "__main__":
    test_data = {
        "numero": "D-2025-0927-002",
        "date_emission": "27/09/2025",
        "date_expiration": "27/10/2025",
        "logo_url": "https://example.com/logo.png",
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
                    "Phase 2 : Module de gestion des leads"
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
