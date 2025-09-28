# City-Road3d-Generator

🏙️ **Générateur 3D de réseau routier de ville** avec zones de densités variées

Création d'un générateur 3D de réseau routier d'une ville à taille variable avec des zones de densités variées comme des zones commerciales, business, résidentiels, loisirs, parcs. Cette génération 3D est voulue pour créer un jeu de divertissement qui permet de vivre une expérience dans une ville (à peupler) qui n'est pas encore construite.

## ✨ Fonctionnalités

- 🌐 **Interface Web Interactive** - Configuration et visualisation en temps réel
- 🏗️ **Génération Procédurale** - Villes uniques à chaque génération
- 🏙️ **6 Types de Zones** - Résidentiel, Commercial, Business, Loisirs, Parcs, Industriel
- 🛣️ **Réseau Routier Complexe** - Routes principales, secondaires et locales
- 🏢 **Bâtiments Variés** - Hauteurs et densités adaptées aux zones
- 📊 **Statistiques Détaillées** - Analyse complète de la ville générée
- 💾 **Export Multiple** - JSON pour données, OBJ pour modèles 3D
- 🖼️ **Aperçu 2D** - Visualisation immédiate du résultat

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation automatique
```bash
# Cloner le repository
git clone https://github.com/ciscoshepard/City-Road3d-Generator.git
cd City-Road3d-Generator

# Installer les dépendances
pip install -r requirements.txt

# Ou installer le package complet
pip install -e .
```

## 🎮 Utilisation

### Interface Web (Recommandé)
```bash
# Lancer l'interface web
python -m city_generator.main --web

# Ou avec des options personnalisées
python -m city_generator.main --web --host 0.0.0.0 --port 8080
```

Ouvrir http://localhost:5000 dans votre navigateur.

### Mode Ligne de Commande
```bash
# Génération basique
python -m city_generator.main --cli

# Ville personnalisée
python -m city_generator.main --cli --width 2000 --height 1500 \
    --residential 0.4 --commercial 0.2 --business 0.25

# Avec export direct
python -m city_generator.main --cli --export ville.json --preview apercu.png
```

### Depuis Python
```python
from city_generator.config import CityConfig
from city_generator.generator import CityGenerator

# Configuration personnalisée
config = CityConfig(
    width=1000,
    height=1000,
    main_road_width=20.0
)

# Génération
generator = CityGenerator(config)
generator.generate_city()

# Export
generator.export_to_json("ma_ville.json")
generator.export_to_obj("ma_ville.obj")
```

## 🏗️ Architecture

### Structure du Projet
```
city_generator/
├── __init__.py          # Package principal
├── config.py           # Configuration et paramètres
├── zones.py            # Gestion des zones urbaines
├── roads.py            # Réseau routier
├── generator.py        # Générateur principal
├── app.py              # Application web Flask
└── main.py             # Point d'entrée CLI

static/
├── css/style.css       # Interface utilisateur
└── js/app.js           # Logique frontend

templates/
└── index.html          # Template principal
```

### Types de Zones

| Zone | Icône | Densité | Hauteur Bâtiments | Caractéristiques |
|------|-------|---------|-------------------|------------------|
| 🏠 Résidentiel | 🏠 | Moyenne | 6-25m | Quartiers d'habitation |
| 🏪 Commercial | 🏪 | Élevée | 8-40m | Magasins et centres commerciaux |
| 🏢 Business | 🏢 | Très élevée | 20-80m | Bureaux et gratte-ciels |
| 🎪 Loisirs | 🎪 | Faible | 3-15m | Divertissement et culture |
| 🌳 Parcs | 🌳 | Très faible | 0-5m | Espaces verts |
| 🏭 Industriel | 🏭 | Élevée | 8-20m | Usines et entrepôts |

## 🔧 Configuration Avancée

### Paramètres Principaux

```python
config = CityConfig(
    # Dimensions
    width=1000,              # Largeur en mètres
    height=1000,             # Hauteur en mètres
    
    # Routes
    main_road_width=20.0,     # Largeur routes principales
    secondary_road_width=12.0, # Largeur routes secondaires
    local_road_width=8.0,     # Largeur routes locales
    
    # Grille urbaine
    main_grid_size=200,       # Espacement grille principale
    secondary_grid_size=100,  # Espacement grille secondaire
    
    # Distribution des zones (%)
    zone_distribution={
        ZoneType.RESIDENTIAL: 0.35,
        ZoneType.COMMERCIAL: 0.15,
        ZoneType.BUSINESS: 0.20,
        ZoneType.LEISURE: 0.10,
        ZoneType.PARKS: 0.15,
        ZoneType.INDUSTRIAL: 0.05
    }
)
```

## 📊 Formats d'Export

### JSON - Données Complètes
```json
{
  "config": { "width": 1000, "height": 1000 },
  "zones": [
    {
      "type": "residential",
      "x": 100, "y": 150,
      "width": 80, "height": 60,
      "density": 0.6,
      "color": [0.8, 0.8, 0.6]
    }
  ],
  "roads": [
    {
      "start": [0, 200], "end": [1000, 200],
      "width": 20.0, "type": "main"
    }
  ],
  "buildings": [
    {
      "x": 110, "y": 160,
      "width": 15, "height": 20,
      "floors": 3, "building_height": 10.5,
      "zone_type": "residential"
    }
  ]
}
```

### OBJ - Modèle 3D
Format standard pour l'import dans Blender, Unity, ou autres logiciels 3D.

## 🧪 Tests

```bash
# Tester l'installation
python test_generator.py

# Tests avec différentes tailles
python -m city_generator.main --cli --width 500 --height 500 --export test.json
```

## 🔍 Exemples d'Utilisation

### Ville Dense Urbaine
```bash
python -m city_generator.main --cli \
    --width 2000 --height 2000 \
    --business 0.30 --commercial 0.25 --residential 0.35 \
    --export ville_dense.json
```

### Ville Avec Beaucoup d'Espaces Verts
```bash
python -m city_generator.main --cli \
    --parks 0.30 --leisure 0.15 --residential 0.40 \
    --export ville_verte.json
```

### Petite Ville Industrielle
```bash
python -m city_generator.main --cli \
    --width 800 --height 600 \
    --industrial 0.20 --residential 0.50 --commercial 0.20 \
    --export ville_industrielle.json
```

**Exemple de sortie pour une ville de 800x600m:**
- 🏙️ 45 zones générées  
- 🏢 18 bâtiments créés
- 🛣️ 466 routes tracées
- ⚡ 27 intersections
- 📦 Export JSON: 85KB

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :

1. Forker le projet
2. Créer une branche pour votre fonctionnalité
3. Committer vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🛠️ Développement Futur

- [ ] Visualisation 3D interactive avec Three.js
- [ ] Génération de trafic routier
- [ ] Export vers formats de jeux (Unity, Unreal)
- [ ] Génération de population et d'activités
- [ ] Système météorologique
- [ ] Éditeur de zones manuel

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les exemples fournis
