# app_students.py - Application Flask pour les élèves
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
from functools import wraps  # AJOUT: Import pour le décorateur
from pdf_generator_students import generate_student_style_devis

# Créer l'application Flask
app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis d'autres domaines

# Configuration
app.config['UPLOAD_FOLDER'] = 'generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# AJOUT: Clés API (à stocker dans des variables d'environnement en production)
API_KEY_1 = os.environ.get('API_KEY_1', 'your-secret-key-1-here')
API_KEY_2 = os.environ.get('API_KEY_2', 'your-secret-key-2-here')

# AJOUT: Décorateur pour vérifier les 2 clés API
def require_api_keys(f):
    """Décorateur pour vérifier les 2 clés API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier les headers
        key1 = request.headers.get('X-API-Key-1')
        key2 = request.headers.get('X-API-Key-2')
        
        if not key1 or not key2:
            return jsonify({"error": "Clés API manquantes"}), 401
        
        if key1 != API_KEY_1 or key2 != API_KEY_2:
            return jsonify({"error": "Clés API invalides"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def documentation():
    """
    Page d'accueil avec la documentation de l'API
    """
    doc = {
        "titre": "🧾 API Générateur de Devis - Version Formation",
        "description": "API simple pour générer des devis PDF avec un design professionnel",
        "version": "1.0.0",
        "author": "Formation Développement Web",
        
        "endpoints": {
            "GET /": "Cette documentation",
            "GET /health": "Vérifier l'état de l'API",
            "GET /api/exemple": "Obtenir un exemple de données JSON",
            "POST /api/devis": "Créer un devis personnalisé",
            "POST /api/test": "Générer un devis de test rapide",
            "GET /api/test-auth": "Tester l'authentification avec les clés API"  # AJOUT
        },
        
        # AJOUT: Section authentification
        "authentification": {
            "description": "Cette API nécessite 2 clés API dans les headers",
            "headers_requis": {
                "X-API-Key-1": "Votre première clé API",
                "X-API-Key-2": "Votre deuxième clé API"
            },
            "exemple_curl_auth": """
curl -X GET http://localhost:5000/api/test-auth \\
  -H "X-API-Key-1: your-secret-key-1-here" \\
  -H "X-API-Key-2: your-secret-key-2-here"
            """
        },
        
        "utilisation": {
            "exemple_curl": """
curl -X POST http://localhost:5000/api/devis \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key-1: your-secret-key-1-here" \\
  -H "X-API-Key-2: your-secret-key-2-here" \\
  -d '{
    "client_nom": "Mon Client",
    "client_adresse": "123 Rue Example, Paris",
    "fournisseur_nom": "Ma Société",
    "items": [
      {
        "description": "Formation web",
        "prix_unitaire": 500.0,
        "quantite": 2
      }
    ]
  }' \\
  --output devis.pdf
            """,
            
            "exemple_javascript": """
fetch('/api/devis', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'X-API-Key-1': 'your-secret-key-1-here',
    'X-API-Key-2': 'your-secret-key-2-here'
  },
  body: JSON.stringify({
    client_nom: 'Mon Client',
    items: [{
      description: 'Ma prestation',
      prix_unitaire: 500.0,
      quantite: 1
    }]
  })
})
.then(response => response.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'devis.pdf';
  a.click();
});
            """
        },
        
        "champs_obligatoires": ["client_nom", "items"],
        "note": "📚 Parfait pour apprendre le développement d'API avec Flask !"
    }
    
    return jsonify(doc), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Vérifier que l'API fonctionne correctement
    """
    return jsonify({
        "status": "healthy",
        "message": "✅ API Devis Formation - Tout fonctionne !",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "version": "1.0.0"
    }), 200

@app.route('/api/exemple', methods=['GET'])
def get_exemple():
    """
    Retourner un exemple complet de données JSON pour créer un devis
    """
    exemple = {
        "numero": f"FORM-{datetime.now().strftime('%Y%m%d')}-001",
        "date_emission": datetime.now().strftime('%d/%m/%Y'),
        "date_expiration": (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
        "date_debut": (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
        
        # Informations fournisseur (modifiables)
        "fournisseur_nom": "Formation Web Academy",
        "fournisseur_adresse": "123 Rue de la Formation",
        "fournisseur_ville": "75001 Paris, France",
        "fournisseur_email": "contact@formation-web.fr",
        "fournisseur_siret": "12345678901234",
        "fournisseur_telephone": "+33 1 23 45 67 89",
        
        # Informations client
        "client_nom": "Entreprise Cliente SARL",
        "client_adresse": "456 Avenue du Commerce",
        "client_ville": "69000 Lyon, France",
        "client_email": "client@entreprise.com",
        "client_siret": "98765432109876",
        "client_telephone": "+33 4 56 78 90 12",
        
        # Informations bancaires
        "banque_nom": "Banque Populaire",
        "banque_iban": "FR76 1234 5678 9012 3456 7890 123",
        "banque_bic": "CCBPFRPPXXX",
        
        # Articles/prestations
        "items": [
            {
                "description": "Formation développement web complète",
                "prix_unitaire": 800.0,
                "quantite": 5
            },
            {
                "description": "Support technique post-formation",
                "prix_unitaire": 150.0,
                "quantite": 2
            },
            {
                "description": "Accès plateforme e-learning (1 an)",
                "prix_unitaire": 299.0,
                "quantite": 1
            }
        ]
    }
    
    return jsonify({
        "message": "📝 Exemple de données pour créer un devis",
        "exemple_donnees": exemple,
        "total_exemple": sum(item['prix_unitaire'] * item['quantite'] for item in exemple['items']),
        "instructions": {
            "endpoint": "/api/devis",
            "methode": "POST",
            "content_type": "application/json",
            "champs_requis": ["client_nom", "items"],
            "note": "💡 Les autres champs ont des valeurs par défaut si non spécifiés"
        }
    }), 200

@app.route('/api/devis', methods=['POST'])
@require_api_keys  # AJOUT: Décorateur d'authentification
def create_devis():
    """
    Créer un devis personnalisé avec les données fournies
    
    Exemple de données JSON à envoyer :
    {
        "client_nom": "Mon Client",
        "client_adresse": "123 Rue Example",
        "fournisseur_nom": "Ma Société", 
        "items": [
            {
                "description": "Ma prestation",
                "prix_unitaire": 500.0,
                "quantite": 1
            }
        ]
    }
    """
    try:
        # Récupérer les données JSON
        data = request.json
        
        if not data:
            return jsonify({"error": "❌ Aucune donnée reçue"}), 400
        
        # Valider les champs obligatoires
        if not data.get('client_nom'):
            return jsonify({"error": "❌ Le champ 'client_nom' est obligatoire"}), 400
        
        if not data.get('items') or len(data.get('items', [])) == 0:
            return jsonify({"error": "❌ Au moins un article est requis"}), 400
        
        # Valider les articles
        for i, item in enumerate(data.get('items', [])):
            if not item.get('description'):
                return jsonify({"error": f"❌ L'article {i+1} doit avoir une description"}), 400
            
            try:
                prix = float(item.get('prix_unitaire', 0))
                if prix <= 0:
                    return jsonify({"error": f"❌ L'article {i+1} doit avoir un prix positif"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": f"❌ L'article {i+1} a un prix invalide"}), 400
            
            try:
                qty = int(item.get('quantite', 1))
                if qty <= 0:
                    return jsonify({"error": f"❌ L'article {i+1} doit avoir une quantité positive"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": f"❌ L'article {i+1} a une quantité invalide"}), 400
        
        # Préparer les données avec valeurs par défaut
        devis_data = {
            "numero": data.get('numero', f"D-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"),
            "date_emission": data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            "date_expiration": data.get('date_expiration', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            "date_debut": data.get('date_debut', ''),
            
            # Informations fournisseur (modifiables)
            "fournisseur_nom": data.get('fournisseur_nom', 'Votre Entreprise'),
            "fournisseur_adresse": data.get('fournisseur_adresse', ''),
            "fournisseur_ville": data.get('fournisseur_ville', ''),
            "fournisseur_email": data.get('fournisseur_email', ''),
            "fournisseur_siret": data.get('fournisseur_siret', ''),
            "fournisseur_telephone": data.get('fournisseur_telephone', ''),
            
            # Informations client
            "client_nom": data.get('client_nom'),
            "client_adresse": data.get('client_adresse', ''),
            "client_ville": data.get('client_ville', ''),
            "client_email": data.get('client_email', ''),
            "client_siret": data.get('client_siret', ''),
            "client_telephone": data.get('client_telephone', ''),
            
            # Informations bancaires
            "banque_nom": data.get('banque_nom', 'Votre Banque'),
            "banque_iban": data.get('banque_iban', 'FR76 0000 0000 0000 0000 0000 000'),
            "banque_bic": data.get('banque_bic', 'XXXXXXXX'),
            
            # Articles (validation déjà faite)
            "items": data.get('items', [])
        }
        
        # Générer le PDF
        filename = generate_student_style_devis(devis_data)
        
        # Vérifier que le fichier a été créé
        if not os.path.exists(filename):
            return jsonify({"error": "❌ Erreur lors de la génération du PDF"}), 500
        
        # Calculer le total pour le log
        total = sum(item.get('prix_unitaire', 0) * item.get('quantite', 1) for item in devis_data['items'])
        
        print(f"✅ Devis généré : {devis_data['numero']} - {devis_data['client_nom']} - {total:.2f}€")
        
        # Retourner le fichier PDF
        return send_file(
            filename,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"devis_{devis_data['numero']}.pdf"
        )
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du devis: {str(e)}")
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

@app.route('/api/test', methods=['POST'])
@require_api_keys  # AJOUT: Décorateur d'authentification
def test_devis():
    """
    Générer un devis de test rapidement (sans paramètres)
    """
    try:
        # Données de test prédéfinies
        test_data = {
            "numero": f"TEST-{datetime.now().strftime('%H%M%S')}",
            "date_emission": datetime.now().strftime('%d/%m/%Y'),
            "date_expiration": (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
            "date_debut": (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
            
            "fournisseur_nom": "Formation Test Academy",
            "fournisseur_adresse": "123 Rue de Test",
            "fournisseur_ville": "75001 Paris, France",
            "fournisseur_email": "test@formation.fr",
            
            "client_nom": "Client de Test",
            "client_adresse": "456 Avenue du Test, 69000 Lyon",
            "client_email": "client.test@exemple.com",
            
            "banque_nom": "Banque de Test",
            "banque_iban": "FR76 1234 5678 9012 3456 7890 123",
            "banque_bic": "TESTFRPP",
            
            "items": [
                {
                    "description": "Formation développement web",
                    "prix_unitaire": 750.0,
                    "quantite": 3
                },
                {
                    "description": "Support technique",
                    "prix_unitaire": 100.0,
                    "quantite": 1
                }
            ]
        }
        
        # Générer le PDF
        filename = generate_student_style_devis(test_data)
        
        print(f"🧪 Devis de test généré : {test_data['numero']}")
        
        return send_file(
            filename,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"devis_test_{test_data['numero']}.pdf"
        )
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return jsonify({"error": f"Erreur lors du test: {str(e)}"}), 500

# AJOUT: Endpoint pour tester l'authentification
@app.route('/api/test-auth', methods=['GET'])
@require_api_keys
def test_auth():
    """Endpoint pour tester l'authentification"""
    return jsonify({"message": "Authentification réussie!"}), 200

# Gestionnaire d'erreur 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "❌ Endpoint non trouvé",
        "message": "Consultez la documentation sur '/' pour voir les endpoints disponibles",
        "endpoints_disponibles": ["/", "/health", "/api/exemple", "/api/devis", "/api/test", "/api/test-auth"]  # MODIFIÉ: Ajout de test-auth
    }), 404

# Gestionnaire d'erreur 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "❌ Erreur serveur",
        "message": "Une erreur interne s'est produite"
    }), 500

# Point d'entrée de l'application
if __name__ == '__main__':
    # Configuration pour le développement local
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Démarrage de l'API Générateur de Devis...")
    print(f"📍 URL: http://localhost:{port}")
    print(f"📚 Documentation: http://localhost:{port}/")
    print(f"🧪 Test rapide: POST http://localhost:{port}/api/test")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
