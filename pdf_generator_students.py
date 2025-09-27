#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas

# Couleurs personnalisées
COULEUR_ACCENT = colors.Color(0.176, 0.208, 0.212)  # Bleu foncé #2d3436
COULEUR_SECTION = colors.Color(0.146, 0.341, 0.886)  # Bleu #2563eb

def create_styles():
    """Créer les styles personnalisés pour le document"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=COULEUR_ACCENT,
        spaceAfter=8,
        alignment=TA_LEFT,  # Aligné à gauche
        leftIndent=0
    ))
    
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=COULEUR_ACCENT,
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
        page_text = f"D-2025-0927-001 · {page_num}/{num_pages}"
        text_width = self.stringWidth(page_text, 'Helvetica', 8)
        self.drawString(A4[0] - 2*cm - text_width, 1.5*cm, page_text)

def calculate_totals(items):
    """Calculer les totaux du devis"""
    total_ht = 0
    total_tva = 0
    
    for item in items:
        item_total = item['quantite'] * item['prix_unitaire']
        if 'remise' in item:
            item_total -= item['remise']
        
        total_ht += item_total
        tva_amount = item_total * (item['tva_taux'] / 100)
        total_tva += tva_amount
    
    total_ttc = total_ht + total_tva
    
    return {
        'total_ht': total_ht,
        'total_tva': total_tva,
        'total_ttc': total_ttc
    }

def generate_student_style_devis(data):
    """Générer un PDF de devis avec le style étudiant"""
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs('generated', exist_ok=True)
    
    filename = os.path.join('generated', f'devis_{data["numero"]}.pdf')
    
    # Configuration du document avec marges réduites en haut
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1*cm,  # Marge réduite
        bottomMargin=4*cm
    )
    
    styles = create_styles()
    elements = []
    
    # En-tête avec titre et nom de l'entreprise
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
    
    # Ligne de séparation colorée
    elements.append(HRFlowable(width="100%", thickness=3, color=COULEUR_ACCENT))
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
         Paragraph(data['client_siret'], styles['CustomNormal'])],
        [Paragraph(data['fournisseur_siret'], styles['CustomNormal']),
         Paragraph(f"Numéro de TVA: {data['client_tva']}", styles['CustomNormal'])]
    ]
    
    company_table = Table(company_info, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Texte d'introduction
    if 'texte_intro' in data:
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
        total_item = item['quantite'] * item['prix_unitaire']
        if 'remise' in item and item['remise'] > 0:
            total_item -= item['remise']
        
        # Ligne principale avec fond bleu foncé
        main_row = [
            Paragraph(item['description'], styles['ItemDescription']),
            Paragraph(str(item['quantite']), styles['ItemDescription']),
            Paragraph(f"{item['prix_unitaire']:.2f} €", styles['ItemDescription']),
            Paragraph(f"{item['tva_taux']} %", styles['ItemDescription']),
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
    
    # Créer le tableau avec les bonnes largeurs
    col_widths = [8*cm, 1.5*cm, 2.5*cm, 2*cm, 2.5*cm]
    items_table = Table(table_data, colWidths=col_widths)
    
    # Style du tableau
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_ACCENT),
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
    
    # Appliquer le fond bleu foncé aux lignes principales des items
    row_index = 1
    for item in data['items']:
        # Ligne principale (description) en bleu foncé
        table_style.extend([
            ('BACKGROUND', (0, row_index), (-1, row_index), COULEUR_ACCENT),
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
    
    # Ligne bleu foncé sous les totaux
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=2, color=COULEUR_ACCENT))
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
    penalites_text = Paragraph(
        "En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée ainsi qu'une indemnité forfaitaire de 40€.",
        ParagraphStyle('SmallText', fontSize=8, textColor=colors.grey, fontName='Helvetica')
    )
    elements.append(penalites_text)
    elements.append(Spacer(1, 10*mm))
    
    # Coordonnées bancaires
    if 'coordonnees_bancaires' in data:
        bank_title = Paragraph("<b>COORDONNÉES BANCAIRES</b>", styles['SectionHeader'])
        elements.append(bank_title)
        
        bank_info = f"""Banque: {data['coordonnees_bancaires'].get('banque', 'Qonto')}<br/>
IBAN: {data['coordonnees_bancaires'].get('iban', 'FR7616958000013234941023663')}<br/>
BIC: {data['coordonnees_bancaires'].get('bic', 'QNTOFRP1XXX')}"""
        
        bank_text = Paragraph(bank_info, styles['CustomNormal'])
        elements.append(bank_text)
        elements.append(Spacer(1, 10*mm))
    
    # Validité et signature
    validity_text = Paragraph(
        f"Cette proposition reste valable 30 jours. Nous restons à votre entière disposition pour toute question ou adaptation de ces solutions à vos besoins spécifiques.",
        styles['CustomNormal']
    )
    elements.append(validity_text)
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
        ('BOTTOMPADDING', (1, 2), (1, 2), 20),  # Espace pour signature
    ]))
    
    elements.append(signature_table)
    
    # Construire le PDF avec le canvas personnalisé
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.company_info = {
            'nom': data['fournisseur_nom'],
            'siret': data['fournisseur_siret'],
            'email': data['fournisseur_email']
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
        "coordonnees_bancaires": {
            "banque": "Qonto",
            "iban": "FR7616958000013234941023663",
            "bic": "QNTOFRP1XXX"
        },
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
    
    filename = generate_student_style_devis(test_data)
    print(f"PDF généré : {filename}")
