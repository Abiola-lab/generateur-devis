# models.py - Classes pour les données du devis
class DevisItem:
    """Classe pour représenter un article/prestation dans le devis"""
    def __init__(self, description, prix_unitaire=0, quantite=1, details=None):
        self.description = description
        self.prix_unitaire = float(prix_unitaire)
        self.quantite = int(quantite)
        self.details = details or []
        self.total_ht = self.prix_unitaire * self.quantite

class Devis:
    """Classe principale pour représenter un devis complet"""
    def __init__(self, numero, date_emission, date_expiration, 
                 fournisseur_nom, client_nom, client_adresse, **kwargs):
        # Informations obligatoires
        self.numero = numero
        self.date_emission = date_emission
        self.date_expiration = date_expiration
        self.date_debut = kwargs.get('date_debut', '')
        
        # Informations fournisseur
        self.fournisseur_nom = fournisseur_nom
        self.fournisseur_adresse = kwargs.get('fournisseur_adresse', '')
        self.fournisseur_ville = kwargs.get('fournisseur_ville', '')
        self.fournisseur_email = kwargs.get('fournisseur_email', '')
        self.fournisseur_siret = kwargs.get('fournisseur_siret', '')
        self.fournisseur_telephone = kwargs.get('fournisseur_telephone', '')
        
        # Informations client
        self.client_nom = client_nom
        self.client_adresse = client_adresse
        self.client_ville = kwargs.get('client_ville', '')
        self.client_email = kwargs.get('client_email', '')
        self.client_siret = kwargs.get('client_siret', '')
        self.client_telephone = kwargs.get('client_telephone', '')
        
        # Informations bancaires
        self.banque_nom = kwargs.get('banque_nom', '')
        self.banque_iban = kwargs.get('banque_iban', '')
        self.banque_bic = kwargs.get('banque_bic', '')
        
        # Conditions
        self.conditions_paiement = kwargs.get('conditions_paiement', 'Paiement à 30 jours')
        self.penalites_retard = kwargs.get('penalites_retard', 'En cas de retard de paiement, une pénalité de 3 fois le taux d\'intérêt légal sera appliquée')
        
        # Articles et totaux
        self.items = []
        self.total_ht = 0
        self.total_tva = 0
        self.total_ttc = 0
    
    def add_item(self, item):
        """Ajouter un article au devis"""
        self.items.append(item)
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculer les totaux HT, TVA et TTC"""
        self.total_ht = sum(item.total_ht for item in self.items)
        self.total_tva = self.total_ht * 0.20  # TVA à 20%
        self.total_ttc = self.total_ht + self.total_tva
    
    def to_dict(self):
        """Convertir le devis en dictionnaire (utile pour JSON)"""
        return {
            'numero': self.numero,
            'date_emission': self.date_emission,
            'date_expiration': self.date_expiration,
            'date_debut': self.date_debut,
            'fournisseur': {
                'nom': self.fournisseur_nom,
                'adresse': self.fournisseur_adresse,
                'ville': self.fournisseur_ville,
                'email': self.fournisseur_email,
                'siret': self.fournisseur_siret,
                'telephone': self.fournisseur_telephone
            },
            'client': {
                'nom': self.client_nom,
                'adresse': self.client_adresse,
                'ville': self.client_ville,
                'email': self.client_email,
                'siret': self.client_siret,
                'telephone': self.client_telephone
            },
            'banque': {
                'nom': self.banque_nom,
                'iban': self.banque_iban,
                'bic': self.banque_bic
            },
            'items': [
                {
                    'description': item.description,
                    'prix_unitaire': item.prix_unitaire,
                    'quantite': item.quantite,
                    'total_ht': item.total_ht
                } for item in self.items
            ],
            'totaux': {
                'total_ht': self.total_ht,
                'total_tva': self.total_tva,
                'total_ttc': self.total_ttc
            }
        }
