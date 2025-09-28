````markdown
name=README.md
# City-Road3d-Generator (MVP)

Projet Godot 4 — génération procédurale de routes en tuiles (MVP).

Quick start:
1. Copier les fichiers fournis dans votre dépôt local.
2. Ouvrir le projet dans Godot 4.
3. Assigner quelques `PackedScene` de tuiles dans la propriété `tile_scenes` du noeud `TileGenerator` (scène principale).
4. Activer le plugin dans Project > Project Settings > Plugins > "City Generator".
5. Dans l'éditeur, utiliser le panneau "City Generator" (dock à droite) pour `Generate City` / `Clear City`.

Notes:
- Les scripts sont marqués `tool` pour être utilisables dans l'éditeur.
- LSystem.gd fournit une base pour générer des motifs L-System ; il faut écrire un interpréteur pour convertir les symboles en tuiles/coups de route.
````
