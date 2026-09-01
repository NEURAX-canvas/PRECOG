## Stack recommandée pour PRECOG — avec preuves

Je structure la stack par couche architecturale (cf. §8-9 du document), en distinguant volontairement **environnement de recherche** (Python) et **portage production** (Rust), comme le prévoit déjà la spec (§2 : *"ton objectif initial n'est pas la performance du framework, mais la validation scientifique de l'hypothèse"*). Pour chaque brique, je donne la preuve qui justifie le choix plutôt qu'une alternative.

---

### 1. Socle de calcul — PyTorch (pas JAX, pas Rust natif au départ)

**Choix : PyTorch + écosystème `torch.func`**

Preuve : `torch.func` (ex-functorch) fournit `jacrev`/`jacfwd` composables avec `vmap` pour calculer des **Jacobiens batchés** sans boucle Python — exactement ce dont a besoin le Trainability Engine (§9.4, §11) pour les statistiques de gradient/Jacobien/conditionnement sur mini-batch :

jacrev() peut être composé avec vmap pour produire des Jacobiens batchés, et si vous rencontrez des problèmes de mémoire en calculant le Jacobien, vous pouvez spécifier un chunk_size non nul. La version vectorisée est significativement plus rapide qu'une boucle manuelle sur les lignes du Jacobien selon la documentation officielle des tutoriels PyTorch, la version avec vmap est bien plus rapide que la version sans, et devient encore plus rapide à mesure que le nombre de sorties augmente.

C'est directement le bon outil pour PRECOG-0 (mode PURE) : forward pass, Jacobien, conditionnement, sans jamais appeler `optimizer.step()`.

---

### 2. Meta-Predictor & incertitude — GPyTorch + ensembles

**Choix : GPyTorch pour les processus gaussiens (petits meta-datasets), + ensembles de réseaux/quantile regression pour les grands volumes**

GPyTorch est le moteur d'inférence gaussienne utilisé nativement par BoTorch, donc il n'y a pas de couture à faire entre "prédiction avec incertitude" et "moteur de recherche" — les deux partagent le même tenseur PyTorch de bout en bout (voir point 3).

---

### 3. Search Engine (Bayesian Optimization) — BoTorch + Ax comme cœur, Optuna comme couche légère optionnelle

**Choix : BoTorch (bas niveau) piloté par Ax (haut niveau)**

C'est exactement l'architecture "moteur / carrosserie" que la spec décrit en §9.8 (Vizier/BO comme bras d'exploration, pas cerveau) :

BoTorch implémente des briques modulaires pour l'optimisation bayésienne moderne. Il fait le pont entre recherche et production en étant à la fois un framework de recherche très flexible et une implémentation fiable de qualité production. Ax est une plateforme d'expérimentation séquentielle qui s'appuie sur BoTorch pour implémenter les algorithmes d'optimisation bayésienne, mais fournit des APIs de plus haut niveau pour spécifier les problèmes, visualiser les résultats et benchmarker de nouveaux algorithmes ; elle inclut aussi une gestion puissante des métadonnées et du stockage des résultats.

Le projet est activement maintenu — le changelog montre des versions publiées en juin 2026, avec le remplacement de Pyro par NumPyro pour l'inférence NUTS entièrement bayésienne, apportant une réduction importante du temps de fit, et l'exigence de PyTorch>=2.4. C'est un point important pour PRECOG : la partie "fully Bayesian" (SAASBO) sert précisément à gérer les espaces de recherche haute dimension du §10 (architecture + optimisation + régularisation combinées).

**Optuna** reste pertinent comme **moteur léger d'ablation rapide** (§19) quand on veut juste comparer des variantes de PRECOG sans monter toute l'infrastructure Ax — mais pas comme moteur principal, car Ax offre nativement la gestion du meta-data que PRECOG doit de toute façon construire.

---

### 4. Benchmarks scientifiques — **ne pas reprendre NAS-Bench-201/HPOBench tels quels**

C'est le point le plus important à corriger par rapport à la première version du document : les deux benchmarks de référence cités (§15.2) sont aujourd'hui **dépréciés ou quasi à l'arrêt**.

- NAS-Bench-201 : depuis que NAS-Bench-201 a été étendu vers NATS-Bench, ce dépôt est déprécié et non maintenu ; il est recommandé d'utiliser NATS-Bench, qui contient 5 fois plus d'informations sur les architectures et une API plus rapide.
- HPOBench : les dernières releases GitHub remontent à plusieurs années, la version 0.0.10 corrige la gestion d'un paramètre d'agent PPO et la clé de signature du commit a expiré — signe clair d'un projet peu actif.

**Recommandation corrigée :**
| Ancien choix | Remplacement recommandé | Preuve |
|---|---|---|
| NAS-Bench-201 | **NATS-Bench** | successeur officiel, maintenu, 5× plus de données |
| — | **NAS-Bench-Suite-Zero** (automl/NASLib) | les auteurs prévoient de maintenir activement le dépôt et accueillent les contributions de la communauté — c'est en plus le benchmark *conçu spécifiquement* pour évaluer des zero-cost proxies, donc directement aligné avec PRECOG-0 |
| HPOBench | **HPO-B** ou **JAHS-Bench** | JAHS-Bench est cité dans la littérature récente (2025) comme benchmark actif pour l'optimisation jointe architecture+hyperparamètres, ce qui correspond exactement à l'espace de recherche multi-niveaux du §10 |

Un raccourci pratique utile pour prototyper vite : `simple-hpo-bench`, qui fournit un ensemble de datasets de benchmark HPO mono-objectif incluant HPOBench, HPOLib et NAS-Bench-201 derrière une API unifiée — utile en V1/V2 (§25) avant d'investir dans NATS-Bench/JAHS en V4-V5.

---

### 5. Meta-dataset & tracking — réutiliser l'existant plutôt que réinventer

Vu ton architecture MLOps déjà en place (MLflow → ArgoCD, cluster GPU K8s), la question n'est pas "quel outil" mais "faut-il en ajouter un nouveau". Réponse : non.

MLflow est recommandé si vous devez self-hoster, garder chaque métrique et artefact dans votre propre réseau, ou éviter la facturation par siège — c'est exactement ton contexte (souveraineté des données d'expérience, déjà self-hosted). Comparé à W&B : MLflow est entièrement open-source et self-hosted sous licence Apache 2.0, donnant un contrôle complet sur l'infrastructure ML, alors que W&B propose une expérience managée.

**Recommandation :** garder MLflow comme registre d'expériences (compatible avec ton toolchain ArgoCD existant), et l'adosser à **Postgres** pour les métadonnées structurées du meta-dataset (§12) + **DuckDB/Parquet** pour l'analyse embarquée offline (ablations, corrélations, requêtes ad hoc sur des millions de lignes d'expériences sans monter un cluster analytique).

---

### 6. Orchestration & infra — réutiliser `ai-helm`, ne pas en créer une nouvelle

Le pipeline PRECOG (§14) est fondamentalement un DAG d'expériences avec budgets adaptatifs (FULL TRAINING, PROBE) : c'est exactement ce que ton architecture existante (StatefulSet serving, Kubernetes GPU orchestration avec MIG/KEDA/Volcano/Kueue) sait déjà faire pour la partie allocation dynamique de ressources GPU. Le Short-Probe adaptatif (§9.10) mappe naturellement sur Kueue/Volcano pour la priorisation de jobs courts vs longs.

---

### 7. Portage production — Rust, cohérent avec UMC, mais **pas dès la V1**

C'est là où ton profil change la réponse par rapport à une réponse "générique". Le choix n'est pas Candle *ou* Burn *ou* tch-rs — c'est une question de phase :

| Phase | Besoin | Choix | Preuve |
|---|---|---|---|
| Recherche (V1-V4) | Autodiff complet, Jacobien, GP, BO | **PyTorch** | aucun concurrent Rust n'a l'équivalent de `torch.func`/GPyTorch/BoTorch aujourd'hui |
| Inférence PURE en production (V5-V6, une fois le meta-predictor figé) | Charger un modèle entraîné, calculer les zero-cost proxies et scorer, sans entraînement | **tch-rs** si tu dois réutiliser des poids PyTorch entraînés tel quel, **Candle** si tu veux du HuggingFace-natif | pour la performance, en particulier dans les environnements accélérés GPU, tch-rs est le choix le plus clair car il s'appuie sur le backend hautement optimisé de PyTorch, alors que Candle bénéficie d'un fort support de l'écosystème HuggingFace |
| Composant natif Rust long terme (aligné UMC) | Zero dépendance Python en prod, cohérence avec ta philosophie "native Rust only" | **Burn** | en 2026, Burn atteint la v0.15.0 avec un support CPU/GPU/WebAssembly via CubeCL et une "production readiness" jugée haute, contre Candle jugé "modérée" en production readiness — mais Burn reste, par sa propre littérature, encore en retrait sur l'entraînement de gros modèles, actuellement en manque de maturité et d'optimisation pour des projets GPU-intensifs à grande échelle |

**Recommandation concrète :** ne pas chercher à faire du Rust pur dès la V1 — la valeur scientifique de PRECOG (§14-19) doit être démontrée en PyTorch, où l'écosystème d'incertitude/BO est incomparablement plus mûr. Le portage Rust (probablement Burn, par cohérence avec UMC et parce que sa feuille de route production est la plus favorable des trois selon le comparatif 2026) n'a de sens qu'en V5-V6, pour la partie **inférence PURE** uniquement (scoring zero-cost + prédiction, pas l'entraînement du meta-predictor lui-même).

---

### 8. Récapitulatif

| Couche | Choix | Alternative rejetée | Raison |
|---|---|---|---|
| Calcul/autodiff | PyTorch + `torch.func` | JAX | écosystème BO/GP (BoTorch/GPyTorch) plus mûr et interopérable |
| Incertitude | GPyTorch (+ ensembles) | — | natif BoTorch |
| Search engine | BoTorch + Ax | Vizier open-source, Optuna seul | Ax gère nativement le meta-data management dont PRECOG a besoin |
| Benchmarks | NATS-Bench, NAS-Bench-Suite-Zero, JAHS-Bench/HPO-B | NAS-Bench-201, HPOBench | dépréciés / peu maintenus |
| Tracking/meta-dataset | MLflow + Postgres + DuckDB | W&B | cohérent avec ton infra existante, self-hosted, pas de per-seat |
| Orchestration | K8s existant (ai-helm) | nouveau système dédié | réutilisation directe des mécanismes MIG/Kueue déjà en place |
| Production/inférence | Burn (cible), tch-rs (transition) | Candle seul | meilleure trajectoire "production readiness" 2026, cohérent avec la philosophie native-Rust d'UMC |

Le point le plus actionnable immédiatement : corriger le choix de benchmarks (§15.2 et §18 du document) — NATS-Bench + NAS-Bench-Suite-Zero au lieu de NAS-Bench-201/HPOBench, car ces derniers ne recevront plus de mises à jour ni de support communautaire actif.
