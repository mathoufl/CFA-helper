# CLAUDE.md — Contexte projet
 
Ce fichier donne le contexte du projet à Claude lors d'une nouvelle session.
 
## Projet
 
Système personnel d'étude du CFA Level 1. L'objectif est de transformer les cours verbeux en synthèses denses et structurées, adaptées à un profil ingénieur francophone.
 
## Profil utilisateur
 
- Ingénieur : à l'aise avec les équations, les raisonnements formels, les implications logiques
- Francophone : synthèses en français, noms de concepts et notations en anglais (tels qu'ils apparaissent dans le cours)
- Pas de background finance : les concepts financiers nouveaux doivent être définis précisément
- Examen en anglais : toujours indiquer le nom anglais exact des concepts et leur notation officielle
## Format de synthèse validé
 
Structure de type "cours de maths", appliquée à chaque concept nouveau :
 
1. **Définition** : nom anglais exact (+ notation officielle si elle existe), définition précise, conditions et hypothèses
2. **Raisonnement** : chaîne d'implications A ⟹ B ⟹ C, posée avant l'équation. Toute variable introduite est définie au point d'introduction
3. **Proposition** : équation(s), chaque variable définie sur place si elle ne l'a pas déjà été
4. **Corollaires** : conséquences directes, conditions limites, mises en garde notables
Pour les sections descriptives sans raisonnement déductif : format liste structurée.
 
## Règles absolues
 
- Aucun concept extérieur au texte source
- Toute variable ou acronyme défini à sa première apparition, sans exception
- Graphiques et tableaux : référencés directement (ex. "cf. Exhibit 5"), seuls les points remarquables sont notés
## Organisation des sessions
 
- 1 chat = 1 cours
- Début de module : LOS (Learning Outcome Statements) passés en contexte
- Pages passées une par une via JSON extrait par le script Python
- Pas de récap entre modules
## Stack technique
 
- Script Python : extraction HTML → JSON (cf. scripts/extract.py)
- Format d'échange : JSON structuré (sections, formules, encadrés, exemples, questions)
- Claude : claude-sonnet-4-6
## À compléter
 
<!-- Ajouter ici au fur et à mesure :
- Conventions de notation propres au cours
- Concepts déjà définis dans les sessions précédentes
- Décisions d'architecture prises
-->