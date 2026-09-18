

Todo · MD
# TODO
 
## Court terme — Pipeline de base
 
- [x] Définir le format de sortie (structure Définition / Raisonnement / Proposition / Corollaires)
- [x] Rédiger le prompt de synthèse
- [ ] Définir le format JSON de sortie du script d'extraction
- [ ] Écrire le script Python d'extraction HTML → JSON
- [ ] Tester le pipeline complet en session réelle et collecter les retours
## Long terme — Système avancé
 
- [ ] **Cohérence inter-pages** : système de mémoire pour éviter les redéfinitions incohérentes et les variables posées sans contexte
  - Piste : base vectorisée ou BM25 des concepts déjà définis
  - Piste : MCP server local exposant cette base à Claude
  - Stack possible : Claude Code + agents locaux
- [ ] **Système de questions sans dilution du contexte**
  - Piste : agent séparé qui récupère le contexte de la session principale
  - L'utilisateur pose ses questions à cet agent, pas dans le fil du cours
- [ ] **Source de vérité**
  - Réfléchir à l'articulation PDF (vérité) / HTML (structure)
  - Éventuellement vectorialiser le PDF comme base de vérification des synthèses
 