#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm, Inches
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
import requests  # AJOUT: Pour télécharger les logos
from io import BytesIO  # AJOUT: Pour gérer les images en mémoire

# AJOUT: Thèmes de couleurs disponibles
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
        'fond': colors.HexColor('#fdeaa7'),
        'header_bg': colors.HexColor('#d35400')
    },
    'noir': {
        'principale': colors.HexColor('#2c3e50'),
        'secondaire': colors.HexColor('#34495e'), 
        'accent': colors.HexColor('#95a5a6'),
        'fond': colors.HexColor('#ecf0f1'),
        'header_bg': colors.HexColor('#2c3e50')
    }
}

# Couleurs personnalisées par défaut (pour compatibilité)
COULEUR_ACCENT = colors.Color(0.176, 0.208, 0.212)  # Bleu foncé #2d3436
COULEUR_SECTION = colors.Color(0.146, 0.341, 0.886)  # Bleu #2563eb

# AJOUT: Fonction pour télécharger et traiter le logo
def download_logo(logo_url):
    """Télécharger et traiter le logo depuis une URL"""
    if not logo_url:
        return None
    
    try:
        # Télécharger l'image avec un timeout
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            
            # Redimensionner le logo (hauteur max 2.5cm)
            max_height = 2.5 * cm
            logo.drawHeight = max_height
            logo.drawWidth = max_height * logo.imageWidth / logo.imageHeight
            
            # Si le logo est trop large, le redimensionner par la largeur
            max_width = 4 * cm
            if logo.drawWidth > max_width:
                logo.drawWidth = max_width
                logo.drawHeight = max_width * logo.imageHeight / logo.imageWidth
            
            return logo
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None
    
    return None

# AJOUT: Fonction pour créer l'en-tête avec logo
def create_header_with_logo(logo_url, title, title_size=18):
    """Créer l'en-tête avec logo et titre"""
    logo = download_logo(logo_url)
    
    title_paragraph = Paragraph(title, ParagraphStyle('Title', 
        fontSize=title_size, textColor=colors.black, fontName='Helvetica-Bold', leftIndent=0))
    
    if logo:
        # Créer un tableau avec titre à gauche et logo à droite
        header_data = [[title_paragraph, logo]]
        header_table = Table(header_data, colWidths=[14*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        return header_table
    else:
        # Pas de logo, titre seul dans un tableau
        title_data = [[title_paragraph]]
        title_table = Table(title_data, colWidths=[18*cm])
        title_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        return title_table

def create_styles(couleurs=None):  # MODIFIÉ: Accepte les couleurs du thème
    """Créer les styles personnalisés pour le document"""
    # Si pas de couleurs spécifiées, utiliser les valeurs par défaut
    if not couleurs:
        couleurs = {
            'principale': COULEUR_ACCENT,
            'header_bg': COULEUR_ACCENT
        }
    
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=couleurs['principale'],  # MODIFIÉ: Utilise la couleur du thème
        spaceAfter=8,
        alignment=TA_LEFT,
        leftIndent=0
    ))
    
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=couleurs['principale'],  # MODIFIÉ: Utilise la couleur du thème
        alignment=TA_RIGHT
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        name='CustomNormal',
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.black
    ))
    
    styles.add(ParagraphStyle(
        name='ItemDescription',
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='ItemDetail',
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.black,
        leftIndent=10,
        spaceAfter=2
    ))
    
    return styles

class NumberedCanvas(canvas.Canvas):
    """Canvas personnalisé avec footer"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.company_info = {}
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        num_pages = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_footer(page_num, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_footer(self, page_num, num_pages):
        """Dessiner le footer avec les informations de l'entreprise"""
        self.setFont('Helvetica', 8)
        
        # Informations de l'entreprise
        company_name = self.company_info.get('nom', 'INFINYTIA, SAS')
        
        # Footer gauche - nom de l'entreprise
        self.drawString(2*cm, 1.5*cm, company_name)
        
        # Footer droite - numéro de page
        page_text = f"{self.company_info.get('numero', 'D-2025-0927-001')} · {page_num}/{num_pages}"  # MODIFIÉ
        text_width = self.stringWidth(page_text, 'Helvetica', 8)
        self.drawString(A4[0] - 2*cm - text_width, 1.5*cm, page_text)

def calculate_totals(items):
    """Calculer les totaux du devis"""
    total_ht = 0
    total_tva = 0
    
    for item in items:
        item_total = item.get('quantite', 1) * item.get('prix_unitaire', 0)
        if 'remise' in item and item['remise'] > 0:  # MODIFIÉ: Support des remises
            item_total -= item['remise']
        
        total_ht += item_total
        tva_taux = item.get('tva_taux', 20)  # MODIFIÉ: TVA variable
        tva_amount = item_total * (tva_taux / 100)
        total_tva += tva_amount
    
    total_ttc = total_ht + total_tva
    
    return {
        'total_ht': total_ht,
        'total_tva': total_tva,
        'total_ttc': total_ttc
    }

def generate_student_style_devis(data, theme='bleu'):  # MODIFIÉ: Ajout du paramètre theme
    """Générer un PDF de devis avec le style étudiant et le thème choisi"""
    
    # AJOUT: Récupérer les couleurs du thème
    couleurs = THEMES_COULEURS.get(theme, THEMES_COULEURS['bleu'])
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs('generated', exist_ok=True)
    
    filename = os.path.join('generated', f'devis_{data["numero"]}_{theme}.pdf')  # MODIFIÉ: Ajout du thème dans le nom
    
    # Configuration du document avec marges réduites en haut
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1*cm,
        bottomMargin=4*cm
    )
    
    styles = create_styles(couleurs)  # MODIFIÉ: Passer les couleurs du thème
    elements = []
    
    # MODIFIÉ: En-tête avec titre et logo si disponible
    if 'logo_url' in data and data['logo_url']:
        header_table = create_header_with_logo(data['logo_url'], "Devis", 24)
        elements.append(header_table)
    else:
        # En-tête original sans logo
        header_data = [
            [Paragraph("Devis", styles['MainTitle']), 
             Paragraph(data['fournisseur_nom'].upper(), styles['CompanyName'])]
        ]
        header_table = Table(header_data, colWidths=[10*cm, 8*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
    
    elements.append(Spacer(1, 5*mm))
    
    # Ligne de séparation colorée avec la couleur du thème
    elements.append(HRFlowable(width="100%", thickness=3, color=couleurs['principale']))  # MODIFIÉ
    elements.append(Spacer(1, 10*mm))
    
    # Informations du devis
    info_data = [
        [Paragraph("<b>Numéro de devis</b>", styles['SectionHeader']), 
         Paragraph(data['numero'], styles['CustomNormal'])],
        [Paragraph("<b>Date d'émission</b>", styles['SectionHeader']), 
         Paragraph(data['date_emission'], styles['CustomNormal'])],
        [Paragraph("<b>Date d'expiration</b>", styles['SectionHeader']), 
         Paragraph(data['date_expiration'], styles['CustomNormal'])]
    ]
    
    info_table = Table(info_data, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15*mm))
    
    # Informations fournisseur et client
    company_info = [
        [Paragraph(f"<b>{data['fournisseur_nom']}</b>", styles['CustomNormal']),
         Paragraph(f"<b>{data['client_nom']}</b>", styles['CustomNormal'])],
        [Paragraph(data['fournisseur_adresse'], styles['CustomNormal']),
         Paragraph(data['client_adresse'], styles['CustomNormal'])],
        [Paragraph(data['fournisseur_ville'], styles['CustomNormal']),
         Paragraph(data['client_ville'], styles['CustomNormal'])],
        [Paragraph(data['fournisseur_email'], styles['CustomNormal']),
         Paragraph(data.get('client_email', ''), styles['CustomNormal'])],  # MODIFIÉ
        [Paragraph(data['fournisseur_siret'], styles['CustomNormal']),
         Paragraph(data.get('client_siret', ''), styles['CustomNormal'])]
    ]
    
    # AJOUT: Ajouter les téléphones s'ils existent
    if data.get('fournisseur_telephone'):
        company_info[3][0] = Paragraph(f"{data['fournisseur_email']}<br/>Tél: {data['fournisseur_telephone']}", styles['CustomNormal'])
    if data.get('client_telephone'):
        company_info[3][1] = Paragraph(f"{data.get('client_email', '')}<br/>Tél: {data['client_telephone']}", styles['CustomNormal'])
    
    company_table = Table(company_info, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # AJOUT: Texte d'introduction
    if 'texte_intro' in data and data['texte_intro']:
        intro_text = Paragraph(data['texte_intro'], styles['CustomNormal'])
        elements.append(intro_text)
        elements.append(Spacer(1, 15*mm))
    
    # Tableau des articles
    table_data = [
        [Paragraph("<b>Description</b>", styles['SectionHeader']),
         Paragraph("<b>Qté</b>", styles['SectionHeader']),
         Paragraph("<b>Prix unitaire</b>", styles['SectionHeader']),
         Paragraph("<b>TVA (%)</b>", styles['SectionHeader']),
         Paragraph("<b>Total HT</b>", styles['SectionHeader'])]
    ]
    
    for item in data['items']:
        # Calcul du total HT pour l'article
        total_item = item.get('quantite', 1) * item.get('prix_unitaire', 0)
        if 'remise' in item and item['remise'] > 0:
            total_item -= item['remise']
        
        # Ligne principale avec fond coloré selon le thème
        main_row = [
            Paragraph(item['description'], styles['ItemDescription']),
            Paragraph(str(item.get('quantite', 1)), styles['ItemDescription']),
            Paragraph(f"{item.get('prix_unitaire', 0):.2f} €", styles['ItemDescription']),
            Paragraph(f"{item.get('tva_taux', 20)} %", styles['ItemDescription']),  # MODIFIÉ
            Paragraph(f"{total_item:.2f} €", styles['ItemDescription'])
        ]
        table_data.append(main_row)
        
        # Lignes de détails en blanc
        if 'details' in item and item['details']:
            details_content = []
            for detail in item['details']:
                details_content.append(detail)
            
            details_text = '<br/>'.join(details_content)
            details_row = [
                Paragraph(details_text, styles['ItemDetail']),
                '', '', '', ''
            ]
            table_data.append(details_row)
        
        # AJOUT: Ligne de remise si applicable
        if 'remise' in item and item['remise'] > 0:
            remise_row = [
                '', '', '',
                Paragraph("Remise", styles['ItemDetail']),
                Paragraph(f"-{item['remise']:.2f} €", styles['ItemDetail'])
            ]
            table_data.append(remise_row)
    
    # Créer le tableau avec les bonnes largeurs
    col_widths = [8*cm, 1.5*cm, 2.5*cm, 2*cm, 2.5*cm]
    items_table = Table(table_data, colWidths=col_widths)
    
    # Style du tableau avec la couleur du thème
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), couleurs['header_bg']),  # MODIFIÉ: Couleur du thème
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Bordures
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]
    
    # Appliquer le fond coloré aux lignes principales des items
    row_index = 1
    for item in data['items']:
        # Ligne principale en couleur du thème
        table_style.extend([
            ('BACKGROUND', (0, row_index), (-1, row_index), couleurs['header_bg']),  # MODIFIÉ
            ('TEXTCOLOR', (0, row_index), (-1, row_index), colors.white),
        ])
        row_index += 1
        
        # Ligne des détails en blanc (si elle existe)
        if 'details' in item and item['details']:
            table_style.extend([
                ('BACKGROUND', (0, row_index), (-1, row_index), colors.white),
                ('TEXTCOLOR', (0, row_index), (-1, row_index), colors.black),
            ])
            row_index += 1
        
        # AJOUT: Style pour la ligne de remise
        if 'remise' in item and item['remise'] > 0:
            table_style.extend([
                ('BACKGROUND', (0, row_index), (-1, row_index), colors.white),
                ('TEXTCOLOR', (3, row_index), (4, row_index), colors.red),
            ])
            row_index += 1
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 15*mm))
    
    # Calcul des totaux
    totals = calculate_totals(data['items'])
    
    # Tableau des totaux
    totals_data = [
        ['', '', '', Paragraph('<b>Total HT</b>', styles['SectionHeader']), 
         Paragraph(f"<b>{totals['total_ht']:.2f} €</b>", styles['SectionHeader'])],
        ['', '', '', Paragraph('<b>Montant total de la TVA</b>', styles['SectionHeader']), 
         Paragraph(f"<b>{totals['total_tva']:.2f} €</b>", styles['SectionHeader'])],
        ['', '', '', Paragraph('<b>Total TTC</b>', styles['SectionHeader']), 
         Paragraph(f"<b>{totals['total_ttc']:.2f} €</b>", styles['SectionHeader'])]
    ]
    
    totals_table = Table(totals_data, colWidths=col_widths)
    totals_table.setStyle(TableStyle([
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (3, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (3, 0), (-1, -1), 4),
        ('TOPPADDING', (3, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    
    # Ligne colorée sous les totaux
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=2, color=couleurs['principale']))  # MODIFIÉ
    elements.append(Spacer(1, 15))
    
    # Conditions de paiement
    conditions_title = Paragraph("<b>CONDITIONS DE PAIEMENT</b>", styles['SectionHeader'])
    elements.append(conditions_title)
    
    if 'conditions_paiement' in data:
        conditions_text = Paragraph(data['conditions_paiement'], styles['CustomNormal'])
    else:
        conditions_text = Paragraph("Paiement à 30 jours date de facture par virement bancaire", styles['CustomNormal'])
    
    elements.append(conditions_text)
    elements.append(Spacer(1, 8*mm))
    
    # Pénalités de retard
    if 'penalites_retard' in data and data['penalites_retard']:
        penalites_text = Paragraph(
            data['penalites_retard'],
            ParagraphStyle('SmallText', fontSize=8, textColor=colors.grey, fontName='Helvetica')
        )
    else:
        penalites_text = Paragraph(
            "En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée ainsi qu'une indemnité forfaitaire de 40€.",
            ParagraphStyle('SmallText', fontSize=8, textColor=colors.grey, fontName='Helvetica')
        )
    elements.append(penalites_text)
    elements.append(Spacer(1, 10*mm))
    
    # Coordonnées bancaires
    if data.get('banque_nom'):  # MODIFIÉ: Utiliser les données fournies
        bank_title = Paragraph("<b>COORDONNÉES BANCAIRES</b>", styles['SectionHeader'])
        elements.append(bank_title)
        
        bank_info = f"""Banque: {data.get('banque_nom', 'Qonto')}<br/>
IBAN: {data.get('banque_iban', 'FR7616958000013234941023663')}<br/>
BIC: {data.get('banque_bic', 'QNTOFRP1XXX')}"""
        
        bank_text = Paragraph(bank_info, styles['CustomNormal'])
        elements.append(bank_text)
        elements.append(Spacer(1, 10*mm))
    
    # AJOUT: Texte de conclusion
    if 'texte_conclusion' in data and data['texte_conclusion']:
        conclusion_text = Paragraph(data['texte_conclusion'], styles['CustomNormal'])
        elements.append(conclusion_text)
        elements.append(Spacer(1, 15*mm))
    
    # Zone de signature
    signature_data = [
        ['', Paragraph('<b>Bon pour accord</b>', styles['SectionHeader'])],
        ['', Paragraph('Date et signature:', styles['CustomNormal'])],
        ['', '']  # Espace pour la signature
    ]
    
    signature_table = Table(signature_data, colWidths=[12*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (1, 2), (1, 2), 20),
    ]))
    
    elements.append(signature_table)
    
    # Construire le PDF avec le canvas personnalisé
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.company_info = {
            'nom': data['fournisseur_nom'],
            'siret': data['fournisseur_siret'],
            'email': data['fournisseur_email'],
            'numero': data['numero']  # AJOUT: Pour le footer
        }
    
    doc.build(elements, canvasmaker=NumberedCanvas, onFirstPage=build_with_canvas, onLaterPages=build_with_canvas)
    
    return filename

# Test avec les données du devis INFINYTIA
if __name__ == "__main__":
    test_data = {
        "numero": "D-2025-0927-001",
        "date_emission": "27/09/2025",
        "date_expiration": "27/10/2025",
        "fournisseur_nom": "INFINYTIA",
        "fournisseur_adresse": "61 Rue De Lyon",
        "fournisseur_ville": "75012 Paris, FR",
        "fournisseur_email": "tony@infinytia.com",
        "fournisseur_siret": "93968736400017",
        "client_nom": "EDENAUTO PREMIUM BORDEAUX (EDENAUTO - BMW)",
        "client_adresse": "28 AVENUE DU PRESIDENT J.F. KENNEDY",
        "client_ville": "33310 LORMONT, FR",
        "client_siret": "332 333 426 00044",
        "client_tva": "FR49332333426",
        "texte_intro": "Suite à notre entretien, nous avons le plaisir de vous proposer nos solutions d'automatisation pour optimiser votre activité commerciale automobile.",
        "logo_url": "https://example.com/logo.png",  # AJOUT: Test avec un logo
        "banque_nom": "Qonto",
        "banque_iban": "FR7616958000013234941023663",
        "banque_bic": "QNTOFRP1XXX",
        "items": [
            {
                "description": "Automatisation pour création de postes sur LinkedIn",
                "quantite": 1,
                "prix_unitaire": 1000.0,
                "tva_taux": 20,
                "details": [
                    "Création automatique de posts LinkedIn personnalisés",
                    "Planification et publication automatisée",
                    "Génération de contenu adapté au secteur automobile",
                    "Intégration avec votre stratégie marketing digitale",
                    "Suivi des performances et analytics",
                    "Formation à l'utilisation de l'outil"
                ]
            },
            {
                "description": "Automatisation pour gestion d'emails",
                "quantite": 1,
                "prix_unitaire": 1000.0,
                "tva_taux": 20,
                "details": [
                    "Système de réponses automatiques intelligentes",
                    "Classification et tri automatique des emails",
                    "Suivi des prospects et clients par email",
                    "Templates personnalisés pour le secteur automobile",
                    "Intégration avec votre CRM existant",
                    "Rapports de performance et statistiques"
                ]
            },
            {
                "description": "Automatisation pour recherche de véhicules sur sites d'annonces",
                "quantite": 1,
                "prix_unitaire": 1000.0,
                "tva_taux": 20,
                "remise": 100,  # AJOUT: Test avec une remise
                "details": [
                    "Scraping automatisé des principaux sites d'annonces",
                    "Veille concurrentielle sur les prix et disponibilités",
                    "Alertes automatiques sur les opportunités d'achat",
                    "Analyse comparative des offres du marché",
                    "Base de données centralisée des véhicules",
                    "Rapports quotidiens personnalisés"
                ]
            }
        ]
    }
    
    # AJOUT: Tester avec différents thèmes
    for theme in ['bleu', 'vert', 'rouge']:
        filename = generate_student_style_devis(test_data, theme=theme)
        print(f"PDF généré avec thème {theme}: {filename}")
