# PRECOG
## Predictive Configuration & Trainability Engine
### Document de vision, spécification scientifique et feuille de route de recherche

---

## 0. Avertissement méthodologique

Toutes les valeurs numériques citées dans ce document (Recall@10 ≥ 90 %, Spearman ρ ≥ 0.90, réduction de compute ≥ 70 %, réduction de données, erreur de prédiction ≤ 5–10 %, etc.) sont des **objectifs expérimentaux à démontrer**, pas des résultats déjà obtenus. Les tableaux d'ablation présentés en exemple sont des **gabarits attendus**, pas des mesures réelles. Ce document est une spécification de recherche, pas un rapport de résultats.

---

## 1. Résumé exécutif

**PRECOG** est un système de recherche visant à transformer le problème classique d'optimisation d'hyperparamètres (HPO) en un problème de **prédiction de la trainability** : à partir d'un modèle vierge, des statistiques d'un dataset, et d'un environnement matériel, PRECOG cherche à prédire — **avant tout entraînement sur les données réelles** — une distribution de configurations d'apprentissage susceptibles de conduire à une convergence rapide, stable et efficace en données.

PRECOG ne se substitue pas à l'entraînement final. Il précède et guide la recherche de configuration, en réduisant drastiquement le nombre d'entraînements complets nécessaires pour trouver une bonne configuration.

L'énoncé central du projet est :

> **PRECOG ne cherche pas les meilleurs hyperparamètres après avoir entraîné de nombreuses configurations ; il cherche à apprendre la relation entre l'état initial d'un modèle, les propriétés du problème et les conditions d'apprentissage, afin de prédire — avant tout entraînement réel — quelles configurations ont la plus forte probabilité de conduire à une convergence rapide et efficace.**

PRECOG est conçu comme une architecture hybride combinant six familles de méthodes complémentaires (zero-cost proxies, analyse d'expressivité de type NEAR, théorie de l'initialisation, meta-learning, optimisation bayésienne, validation courte adaptative), organisées en boucle fermée d'amélioration continue à partir d'un meta-dataset d'expériences.

---

## 2. Motivation

L'optimisation d'hyperparamètres classique (grid search, random search, Bayesian Optimization, Hyperband, PBT, etc.) procède essentiellement par **essai-erreur coûteux** : chaque configuration candidate doit être partiellement ou totalement entraînée pour être évaluée. Ce coût devient prohibitif à mesure que les modèles grossissent.

Une partie de la littérature récente (zero-cost proxies, NAS training-free, NEAR) montre qu'il est possible d'extraire des signaux informatifs sur la qualité potentielle d'une architecture ou d'une configuration **sans entraînement complet**, parfois à partir d'un seul mini-batch. Ces résultats restent cependant fragmentaires : aucun proxy n'est universellement dominant, la généralisation inter-domaines (vision → NLP → LLM) reste incertaine, et ces travaux se concentrent presque toujours sur le classement d'architectures plutôt que sur la prédiction complète d'une configuration d'apprentissage (learning rate, batch size, initialisation, scheduler, etc.).

PRECOG part de l'hypothèse que ces signaux, combinés entre eux et enrichis par l'expérience accumulée sur de nombreux entraînements passés (meta-learning), peuvent être exploités pour construire un **prédicteur de configuration**, et non uniquement un classement d'architectures.

---

## 3. Problème scientifique

### 3.1 Formulation informelle

> Étant donné un modèle vierge M, un dataset D (caractérisé uniquement par ses statistiques, sans entraînement dessus) et un environnement matériel H, peut-on prédire une configuration d'apprentissage θ (architecture fine, initialisation, optimiseur, learning rate, batch size, régularisation, scheduler) qui maximise la probabilité d'atteindre une performance cible, tout en minimisant le compute, le temps et la quantité de données nécessaires ?

### 3.2 Formulation mathématique

$$
\theta^* = \arg\max_{\theta} \; P\big(\text{Convergence} \geq \text{Target} \mid M, D, H, \theta\big)
$$

PRECOG cherche à approximer :

$$
P(\theta^* \mid M, D, H)
$$

**sans mettre à jour les poids du modèle réel sur les données réelles** (voir §5 pour la définition stricte de « sans entraînement »).

### 3.3 Ce que PRECOG n'est pas

- Ce n'est **pas** un NAS (Neural Architecture Search) au sens strict : PRECOG peut proposer des ajustements d'architecture mais son cœur est la configuration d'apprentissage.
- Ce n'est **pas** un simple wrapper autour d'un optimiseur bayésien (type Google Vizier) : Vizier/BO est un composant interne (le moteur de recherche), pas le système entier.
- Ce n'est **pas** une garantie de performance : c'est un système probabiliste qui doit exprimer son incertitude.

---

## 4. Hypothèses de recherche

- **H1 (Signal pré-entraînement) :** l'état d'un réseau vierge (statistiques de gradient, Jacobien, activations, spectre, initialisation) contient de l'information exploitable sur sa future trainability.
- **H2 (Non-universalité des proxies) :** aucun signal pris isolément n'est suffisant ; la combinaison de plusieurs familles de signaux est plus robuste que chacune séparément.
- **H3 (Transférabilité par meta-learning) :** l'expérience accumulée sur des couples (modèle, dataset, configuration, résultat) passés améliore la prédiction sur des couples nouveaux, via une représentation de tâche partagée.
- **H4 (Utilité du entraînement court) :** une validation très courte (quelques dizaines à quelques centaines de steps) réduit fortement l'incertitude sur les meilleures prédictions, à un coût marginal.
- **H5 (Existence de régimes)** : les relations optimales entre hyperparamètres (ex. LR* = f(BatchSize)) dépendent du régime d'apprentissage (taille du modèle, bruit des données, architecture), et non d'une constante universelle.
- **H6 (Corrélation ≠ causalité)** : certaines relations observées entre signaux pré-entraînement et performance finale sont confondues par des variables tierces (l'architecture, notamment) ; une partie doit être testée expérimentalement pour être exploitée avec confiance.

Chacune de ces hypothèses doit être testée et potentiellement réfutée par les protocoles décrits en §14.

---

## 5. Définition opérationnelle de « sans entraînement » — les trois modes

C'est la contrainte méthodologique la plus importante du projet : elle doit être non ambiguë.

| Mode | Description | Mise à jour des poids du modèle réel | Usage |
|---|---|---:|---|
| **PURE-PRECOG** | Analyse du modèle vierge et du dataset (statistiques, forward passes sans apprentissage, calculs zero-cost, Jacobien, etc.) | **ΔW = 0** | Mode de référence pour la promesse centrale du projet |
| **PROBE** | Entraînement très court et contrôlé (ex. 50–1000 steps, 0.1–1 % du budget total) | ΔW ≠ 0, mais borné et journalisé | Validation/raffinement d'une prédiction PURE |
| **FULL TRAINING** | Entraînement complet | ΔW ≠ 0, sans restriction | Génération de la vérité terrain (ground truth), jamais utilisé pour « tricher » sur la prédiction |

**Règle de contrat (Zero-Training Contract) :** tout benchmark revendiquant la promesse centrale de PRECOG (« prédire sans entraîner ») doit être réalisé exclusivement en mode **PURE**. Le mode **PROBE** est une extension explicitement mesurée séparément : on doit toujours pouvoir répondre à la question « combien PROBE apporte-t-il par rapport à PURE seul, pour quel coût additionnel ? ».

En mode PURE, les opérations autorisées sur le dataset sont limitées à des **statistiques descriptives** (taille, dimensionnalité, entropie approximée, déséquilibre de classes, redondance, bruit estimé) et, si nécessaire, à des **forward passes sans rétropropagation ni mise à jour des poids** (pour mesurer activations/Jacobien). Aucune boucle `optimizer.step()` n'est permise.

---

## 6. Positionnement par rapport à l'état de l'art

| Courant | Apport pour PRECOG | Limite reconnue |
|---|---|---|
| Zero-Cost Proxies (NAS training-free) | Signaux rapides (SynFlow, SNIP, GraSP, Jacob-Cov…) à partir d'un mini-batch | Aucun proxy n'est dominant partout ; corrélations très variables selon domaine |
| NEAR (effective rank des activations) | Signal d'expressivité training-free, utile pour choisir activation/initialisation | Signal seul, insuffisant pour prédire une configuration complète |
| Théorie de l'initialisation / dynamical isometry | Cadre pour comprendre la propagation du signal et du gradient | Résultats surtout établis sur des cas simplifiés (réseaux linéaires profonds) |
| Meta-learning pour HPO | Réutilisation d'expériences passées comme prior | Dépend fortement de la qualité et de la diversité du meta-dataset |
| Bayesian Optimization, Hyperband, BOHB, PBT, ASHA, Vizier, Optuna | Moteurs de recherche efficaces sous budget | Partent en général d'un prior faible ou nul ; coût d'évaluation encore élevé sans signal pré-entraînement |
| Freeze-thaw BO / prédiction de learning curves | Allocation progressive de ressources, arrêt anticipé | Nécessite déjà des observations partielles d'entraînement |

PRECOG se positionne comme une **couche de prédiction en amont** de ces moteurs de recherche : ceux-ci restent utilisés comme **bras d'exploration**, alimentés par un prior beaucoup plus informé.

---

## 7. Principes fondamentaux

1. **Observer avant de tester.** Toute information exploitable sans entraînement doit être exploitée avant de dépenser du compute.
2. **Ne jamais dépendre d'un signal unique.** Chaque famille de signaux compense les faiblesses d'une autre (voir §9).
3. **Prédire des distributions, pas des valeurs.** PRECOG retourne une région probable avec un niveau de confiance, jamais une valeur ponctuelle présentée comme certaine.
4. **Apprendre des fonctions conditionnelles, pas des constantes.** Ex. LR* = f(Model, Dataset, Initialization, BatchSize, Optimizer), et non « LR = 0.001 ».
5. **Économie mesurable.** PRECOG n'a de valeur que si son coût total (analyse + probes éventuels) reste largement inférieur au coût d'un HPO classique.
6. **Apprendre de ses erreurs.** Chaque écart entre prédiction et vérité terrain est une donnée précieuse, conservée et exploitée, pas un résultat à ignorer.
7. **Corrélation ≠ causalité.** Les relations exploitées en production doivent, autant que possible, être validées par des tests contrôlés.
8. **Généralisation avant tout.** Un score élevé sur un benchmark déjà vu n'a pas de valeur scientifique tant qu'il n'est pas reproduit sur des tâches, architectures et datasets jamais rencontrés.

---

## 8. Architecture complète

```text
                         PRECOG
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
       MODEL ENCODER   DATA ENCODER    HARDWARE ENCODER
            │               │                │
            └───────────────┼────────────────┘
                            ▼
                     TASK REPRESENTATION
                            │
                            ▼
                    TRAINABILITY ENGINE
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
       Zero-Cost          NEAR          Initialization /
       Proxies                          Gradient / Jacobian
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                      REGIME DETECTOR
                            │
                            ▼
                    META-KNOWLEDGE BASE
                     (meta-dataset + task
                        embeddings)
                            │
                            ▼
                       META-PREDICTOR
                     (ensemble multi-tête)
                      /              \
              Prediction         Uncertainty
                (distribution)    (calibrée)
                      \              /
                            ▼
                  HYPERPARAMETER DISTRIBUTION
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        Pareto Search                Search Engine
       (multi-objectif)          (BO / Active Learning /
                                    Diversity)
              └─────────────┬─────────────┘
                            ▼
                    ADAPTIVE SHORT-PROBE
                     (mode PROBE, optionnel)
                            │
                    ┌───────┴────────┐
                    ▼                ▼
                REJETER          CONFIRMER
                    │                │
                    ▼                ▼
              (retour boucle)   FULL TRAINING
                                     │
                                     ▼
                               GROUND TRUTH
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                                ▼
              META-DATASET UPDATE               FAILURE ANALYSIS
                     │                                │
                     └───────────────┬────────────────┘
                                     ▼
                       SCIENTIFIC DISCOVERY ENGINE
                                     │
                                     ▼
                              PRECOG v(n+1)
```

---

## 9. Composants détaillés

### 9.1 Model Encoder

Extrait un vecteur de descripteurs $X_{model}$ à partir de la seule architecture (sans données) : profondeur, largeur, nombre de paramètres, FLOPs, type d'activation, normalisation, ratio de connexions résiduelles, structure d'attention, mémoire requise.

### 9.2 Data Encoder

Extrait $X_{data}$ à partir de statistiques descriptives autorisées en mode PURE : taille, dimensionnalité, entropie, bruit estimé, déséquilibre de classes, corrélation de features, redondance, distribution. Objectif à terme : un embedding $Z_D = \text{Encoder}_{data}(D)$ permettant de comparer des datasets par similarité.

### 9.3 Hardware Encoder

Capture GPU/CPU, mémoire, bande passante, précision numérique, capacité de batch, interconnexion — car la configuration optimale dépend aussi de l'environnement d'exécution : $\theta^* = f(M, D, H)$.

### 9.4 Trainability Engine

Cœur analytique du système. Calcule, sans mise à jour des poids :

- **Zero-Cost Proxies** : SynFlow, SNIP, GraSP, Jacob-Cov, statistiques de gradient et d'activation sur un ou quelques mini-batchs.
- **NEAR** : rang effectif des activations avant/après non-linéarité, comme indicateur d'expressivité.
- **Analyse d'initialisation** : variance des activations et des gradients, valeurs singulières du Jacobien $J = \partial f(x)/\partial x$, conditionnement $\kappa(J) = \sigma_{max}/\sigma_{min}$, lien avec la dynamical isometry.
- **Courbure** (lorsque mesurable à faible coût) : approximations de la Hessienne locale.

Règle de combinaison : $Score_{ZC} = f(S_1, S_2, ..., S_n)$, jamais un score isolé.

### 9.5 Regime Detector

Classifie le couple (modèle, dataset, hardware) dans un régime d'apprentissage (ex. petit modèle/données propres, grand modèle/données bruitées, faible quantité de données, séquences longues). Produit un **prior de régime** utilisé pour contraindre la distribution d'hyperparamètres prédite.

```text
(Model, Dataset, Hardware) → Regime → Hyperparameter Prior
```

### 9.6 Meta-Knowledge Base

Base structurée de toutes les expériences passées (voir §12), avec un mécanisme de **task embedding** permettant de retrouver les expériences historiques les plus proches d'une nouvelle tâche, et d'utiliser ce voisinage comme prior de recherche (transfert d'expérience).

### 9.7 Meta-Predictor

Modèle (ou ensemble de modèles) prenant en entrée :

$$
X = [X_{model}, X_{data}, X_{ZC}, X_{NEAR}, X_{init}, X_{regime}]
$$

et produisant, pour chaque configuration candidate, une prédiction multi-tête :

- $\hat{A}$ : performance attendue
- $\hat{T}$ : steps/temps de convergence
- $\hat{C}$ : compute attendu
- $\hat{N}$ : données nécessaires
- une **incertitude** associée à chaque tête (ex. par ensembles, quantile regression, ou approches bayésiennes)

Le résultat n'est jamais une valeur unique mais une distribution, par exemple :

```text
Learning rate
  recommended = 3.5e-4
  range       = [2e-4, 6e-4]
  confidence  = 91 %
```

### 9.8 Search Engine (BO + Active Learning + Diversity)

Le meta-predictor fournit un **prior informé** ; le moteur de recherche explore ensuite l'espace restant. Fonction d'acquisition hybride :

$$
Acquisition = \alpha \cdot \text{Expected Improvement} + \beta \cdot \text{Uncertainty} + \gamma \cdot \text{Diversity}
$$

Google Vizier / Optuna / BOHB jouent ici le rôle de **bras d'exploration**, pas de cerveau du système.

### 9.9 Pareto Search (optimisation multi-objectifs)

Plutôt que de chercher un optimum unique, PRECOG recherche un **front de Pareto** sur (performance, compute, données, temps, mémoire, énergie) :

```text
                  Performance
                       ▲
                  A ●
                    \
                 B ● \
                       ● C
                          \
                           ● D
                       └──────────────► Coût
```

PRECOG peut alors retourner plusieurs configurations Pareto-optimales, à charge pour l'utilisateur (humain ou système) de choisir selon ses contraintes.

### 9.10 Adaptive Short-Probe (mode PROBE)

Budget d'entraînement court alloué **dynamiquement** selon l'incertitude et la performance intermédiaire :

```text
Candidate A → 50 steps → très mauvais → STOP
Candidate B → 50 steps → prometteur   → 200 steps
Candidate C → 50 steps → excellent    → 1000 steps
```

Formalisation : $Budget_i = f(Uncertainty_i, Performance_i)$. Ce mécanisme s'appuie sur la prédiction de learning curves (freeze-thaw) pour estimer une *time-to-target* et décider CONTINUER/ARRÊTER.

### 9.11 Decision Policy

Politique explicite transformant PRECOG d'un simple prédicteur en agent d'optimisation expérimentale :

$$
Policy(s_t) \rightarrow \{\text{TRAIN}, \text{STOP}, \text{EXPLORE}, \text{EXPLOIT}, \text{REQUEST MORE DATA}\}
$$

### 9.12 Causal Discovery Module

Sépare corrélation et causalité par des expériences contrôlées : à architecture, dataset et optimiseur fixés, on fait varier une seule variable candidate (ex. la variance du gradient induite par l'initialisation) pour observer son effet isolé sur la convergence, plutôt que de conclure à partir d'une simple corrélation observationnelle.

### 9.13 OOD / Distribution-Shift Detector

Estime $P(\text{tâche connue})$. Si une nouvelle tâche est jugée éloignée du meta-dataset, PRECOG doit automatiquement augmenter le budget de validation (mode PROBE) plutôt que de faire une prédiction PURE surconfiante.

### 9.14 Failure Analysis Engine

Catégorise chaque erreur de prédiction significative :

```text
DATA_SHIFT
ARCHITECTURE_SHIFT
INITIALIZATION_FAILURE
OPTIMIZER_FAILURE
PROXY_FAILURE
PREDICTOR_FAILURE
```

et alimente le cycle d'amélioration (meta-dataset → ré-entraînement du meta-predictor).

### 9.15 Scientific Discovery Engine

Objectif à plus long terme : transformer des corrélations observées en hypothèses, tester ces hypothèses par des expériences contrôlées (voir 9.12), et en déduire des principes généraux de trainability (ex. une relation candidate $LR^* \approx f(\text{BatchSize}, \text{GradientNoise}, \text{ModelScale})$ à vérifier expérimentalement).

```text
Experiments → Patterns → Correlations → Hypotheses
   → Controlled experiments → Causal evidence → New principle
```

---

## 10. Variables et hyperparamètres

### 10.1 Hiérarchie des hyperparamètres cibles (du modèle entraîné)

| Niveau | Famille | Variables |
|---|---|---|
| 1 | Architecture | depth, width, hidden dimension, number of heads, activation, normalization, residual connections |
| 2 | Initialisation | Xavier, He, Orthogonal, variance/scale, bias init, LSUV |
| 3 | Optimisation | optimizer (SGD, Momentum, Adam, AdamW, RMSProp, Lion), learning rate, batch size, gradient accumulation, momentum |
| 4 | Scheduling | warmup, scheduler (cosine, linear, exponentiel, OneCycle), decay, LR minimum |
| 5 | Régularisation | weight decay, dropout, label smoothing |
| 6 | Données | sampling ratio, augmentation, curriculum, quantité de données |

### 10.2 Hyperparamètres internes de PRECOG (à distinguer strictement des précédents)

| Composant | Hyperparamètres internes |
|---|---|
| Bayesian Optimization | fonction d'acquisition, coefficient exploration/exploitation, choix de noyau, observations initiales |
| Short-Probe | nombre de steps initial, budget de probe, seuil d'arrêt anticipé, seuil de confiance |
| Active Learning | coefficients d'exploration/incertitude/diversité |
| Meta-learning | dimension des embeddings, taille de l'historique, taux d'apprentissage du meta-predictor |

### 10.3 Principe des fonctions conditionnelles

PRECOG n'apprend jamais une constante universelle mais des relations conditionnelles :

$$
LR^* = f(\text{Model}, \text{Dataset}, \text{Initialization}, \text{BatchSize}, \text{Optimizer})
$$
$$
\text{Initialization}^* = f(\text{Architecture}, \text{Dataset})
$$
$$
\text{BatchSize}^* = f(\text{ModelSize}, \text{DatasetSize}, \text{LR}, \text{Hardware})
$$
$$
\text{Optimizer}^* = f(\text{Model}, \text{Dataset}, \text{LR}, \text{BatchSize})
$$

et plus généralement une distribution jointe $P(\theta^* \mid M, D, H)$, avec un **graphe d'interactions** explicite entre variables (ex. LR ↔ BatchSize ↔ bruit du gradient ; Architecture ↔ Initialisation ↔ propagation du signal).

---

## 11. Le concept central : la trainability

### 11.1 Définition opérationnelle

$$
\text{Trainability} = f(\text{Gradient}, \text{Jacobian}, \text{Activation}, \text{Curvature}, \text{Conditioning}, \text{Initialization}, \text{Architecture}, \text{Data})
$$

### 11.2 Signaux exploitables

- Norme et distribution du gradient $\|\nabla_\theta L\|$
- Variance du gradient $Var(\nabla_\theta L)$
- Jacobien $J$, ses valeurs singulières $\sigma_1, ..., \sigma_n$
- Conditionnement $\kappa(J) = \sigma_{max}/\sigma_{min}$
- Statistiques d'activation $E[a], Var(a)$
- Courbure locale $H = \nabla^2_\theta L$ (approximée, quand le coût le permet)
- Propriétés d'initialisation et lien avec la dynamical isometry

### 11.3 Question de recherche centrale

> Quels signaux, observables sur un modèle vierge, prédisent réellement la vitesse et la qualité future de l'apprentissage — et lesquels ne sont que des artefacts corrélés à l'architecture ?

Cette question doit être traitée à la fois de façon **prédictive** (le meta-predictor) et **causale** (le module de découverte causale, §9.12).

---

## 12. Le meta-dataset : mémoire scientifique de PRECOG

Chaque expérience — y compris chaque échec — doit être enregistrée avec, au minimum :

```text
Experiment
├── Model        (architecture, depth, width, params, FLOPs, activation, norm.)
├── Dataset      (taille, dimension, entropie, bruit, déséquilibre, diversité)
├── Hardware     (GPU/CPU, mémoire, précision, bande passante)
├── Initialization
├── Optimizer, LR, batch size, weight decay, scheduler, warmup
├── Zero-cost descriptors (SynFlow, SNIP, GraSP, Jacobian, NEAR…)
├── Training dynamics (normes de gradient, pente de la loss, statistiques d'activation)
├── Learning curve complète
├── Steps, compute (GPU-hours), mémoire, temps, quantité de données, seed
└── Ground truth (performance finale, convergence, coût réel)
```

Les échecs de prédiction sont **conservés et étiquetés** (voir Failure Analysis, §9.14) : ils constituent un signal d'apprentissage au moins aussi précieux que les succès.

**Séparation stricte :** le meta-dataset est partitionné en TRAIN / VALIDATION / TEST, avec verrouillage explicite du TEST (jamais utilisé pour améliorer PRECOG), afin d'éviter le *benchmark overfitting*.

---

## 13. Transfert d'expérience et task embedding

```text
                 New Task
                    │
                    ▼
              Task Encoder
                    │
                    ▼
              Task Embedding
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Similar Tasks       Meta-Dataset
          │                   │
          └─────────┬─────────┘
                    ▼
              Prior Knowledge
                    │
                    ▼
              Optimization
```

PRECOG doit pouvoir reconnaître qu'un nouveau problème « ressemble » à un problème déjà rencontré et exploiter cette similarité comme prior, plutôt que de repartir d'une recherche non informée — c'est l'un des principaux leviers attendus pour passer d'un système simplement analytique à un système réellement intelligent.

---

## 14. Pipeline expérimental de bout en bout

```text
                    ┌──────────────────┐
                    │  BENCHMARK TASKS │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │  PRECOG ANALYSIS │  (mode PURE)
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ META-PREDICTOR   │
                    │ prediction +     │
                    │ uncertainty      │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ SEARCH ENGINE    │  (BO / Active Learning / Pareto)
                    └────────┬─────────┘
                             ▼
                      TOP CANDIDATES
                             ▼
                    ┌──────────────────┐
                    │ SHORT PROBES     │  (mode PROBE, optionnel)
                    └────────┬─────────┘
                     ┌───────┴────────┐
                     ▼                ▼
                  PROMETTEUR        MAUVAIS
                     │                │
                     ▼                ▼
               FULL TRAINING     STOP / APPRENDRE
                     ▼
                 GROUND TRUTH
                     ▼
              META-DATASET UPDATE
                     ▼
              FAILURE ANALYSIS + RETRAIN
                     ▼
               PRECOG v(n+1)
```

Cette boucle ne s'arrête jamais après une seule itération : chaque génération de PRECOG doit être comparée à la précédente sur un protocole strictement identique.

---

## 15. Protocoles de test

| Protocole | Question | Métrique principale |
|---|---|---|
| **P1 — Ranking** | PRECOG classe-t-il correctement les configurations ? | Spearman ρ, Kendall τ |
| **P2 — Top-K** | Retrouve-t-il les meilleures configurations ? | Recall@K |
| **P3 — Convergence** | La configuration retenue converge-t-elle plus vite ? | Steps/Time-to-Target |
| **P4 — Compute** | Combien de calcul est économisé ? | GPU-hours / FLOPs |
| **P5 — Data efficiency** | Même qualité avec moins de données ? | Samples-to-Target |
| **P6 — Generalization** | Fonctionne-t-il sur un modèle/dataset jamais vu ? | Performance out-of-distribution |

### 15.1 Séparation TRAIN/VALIDATION/TEST

```text
PRECOG TRAIN        → datasets et architectures connus, historique d'expériences
PRECOG VALIDATION   → datasets différents, architectures partiellement nouvelles
PRECOG TEST (verrouillé) → jamais vus, jamais utilisés pour améliorer PRECOG
```

### 15.2 Benchmarks de référence pour la phase initiale

- **NAS-Bench-201** : espace de référence d'architectures avec performances pré-calculées (CIFAR-10, CIFAR-100, ImageNet16-120) — utile pour tester le ranking sans avoir à entraîner chaque architecture soi-même.
- **HPOBench** : collection de problèmes de benchmark HPO, notamment multi-fidelity, pensée pour la reproductibilité.
- **Laboratoire synthétique** (généré en interne) : datasets et modèles entièrement contrôlés (bruit, entropie, dimensionnalité, profondeur, largeur), permettant d'isoler des variables causales candidates avant de passer aux benchmarks réels.

### 15.3 Multi-seed et tests statistiques

Chaque expérience importante est répétée sur plusieurs seeds, avec calcul de moyenne, écart-type et intervalle de confiance (95 % CI). Les comparaisons entre méthodes (PRECOG vs Random, vs BO, vs Hyperband, vs Vizier) utilisent des tests statistiques adaptés (ex. Wilcoxon signed-rank plutôt qu'un t-test lorsque les hypothèses paramétriques ne sont pas garanties), afin d'éviter de déclarer une supériorité sur la base d'un seed favorable.

---

## 16. Métriques et objectifs (à démontrer, non garantis)

| Métrique | Définition | Cible expérimentale visée |
|---|---|---|
| Ranking correlation | Spearman ρ / Kendall τ entre classement PRECOG et classement réel | ρ ≥ 0.80 puis ≥ 0.90 |
| Top-K recall | $Recall@K = \|\text{PredictedTopK} \cap \text{TrueTopK}\| / K$ | Recall@10 ≥ 80 % puis ≥ 90 % |
| Compute reduction | $1 - C_{PRECOG}/C_{baseline}$ | ≥ 50 % puis ≥ 70 % |
| Performance retention | $Performance_{PRECOG}/Performance_{oracle}$ | ≥ 99 % (ou tolérance définie a priori) |
| Data efficiency | $Samples_{baseline}/Samples_{PRECOG}$ pour performance cible égale | ≥ 30–50 % de réduction, à affiner |
| Time/Steps-to-Target | Réduction du temps/nombre de steps pour atteindre une cible | ≥ 50 % de réduction |
| Prediction error (learning curve) | $\lvert \text{Prediction} - \text{Actual} \rvert$ | ≈ 5–10 % selon la métrique |
| Generalization | Recall@K sur tâches/architectures/datasets jamais vus | même ordre de grandeur que sur données connues |

Ces cibles sont **des hypothèses de progression**, formalisées en portes successives (§17), jamais présentées comme acquises avant démonstration.

---

## 17. Portes de progression (Gates)

```text
                PRECOG
                   │
             GATE 1 : ρ ≥ 0.70 ?
                   │
             GATE 2 : Recall@10 ≥ 80 % ?
                   │
             GATE 3 : Compute reduction ≥ 50 % ?
                   │
             GATE 4 : Generalization maintenue (données jamais vues) ?
                   │
             GATE 5 : Recall@10 ≥ 90 % ?
                   │
             GATE 6 : Compute reduction ≥ 70 % ?
                   │
             PRECOG « niveau avancé »
```

Chaque porte est validée par des métriques indépendantes, sur des jeux verrouillés, avant de considérer la génération suivante.

---

## 18. Baselines de comparaison

PRECOG doit être systématiquement comparé, à budget égal, à :

```text
Random Search       Grid Search
Bayesian Optimization   Hyperband
ASHA                 BOHB
Population Based Training
Google Vizier         Optuna
Zero-Cost NAS (proxy seul)
Meta-learning HPO (sans les couches additionnelles de PRECOG)
```

sur les axes : performance finale, compute, vitesse de convergence, données nécessaires, généralisation.

---

## 19. Stratégie d'ablation

### 19.1 Ablation des composants du pipeline

```text
PRECOG-A = Zero-Cost uniquement
PRECOG-B = + NEAR
PRECOG-C = + Initialization analysis
PRECOG-D = + Meta-Learning
PRECOG-E = + Bayesian Optimization
PRECOG-F = + Short Probe adaptatif
PRECOG-G = + Active Learning / Uncertainty
PRECOG-H = + Causal Discovery / OOD detection
```

Exemple de tableau attendu (gabarit, non des résultats) :

| Système | Spearman | Recall@10 | Compute utilisé |
|---|---:|---:|---:|
| Random | 0.10 | 10 % | 100 % |
| ZC | 0.60 | 55 % | 10 % |
| ZC+NEAR | 0.68 | 64 % | 12 % |
| +Init | 0.73 | 70 % | 14 % |
| +Meta | 0.79 | 77 % | 16 % |
| +BO | 0.82 | 82 % | 20 % |
| +Probe adaptatif | 0.88 | 90 % | 30 % |

### 19.2 Ablation des proxies individuels

SynFlow, SNIP, GraSP, Jacobian, NASWOT, Jacob-Cov, Gradient Norm, NEAR — testés individuellement puis en combinaison, car la littérature montre qu'aucun proxy n'est universellement dominant.

### 19.3 Test de robustesse

Perturbations volontaires : bruit et déséquilibre du dataset, distribution shift, profondeur/largeur du modèle, activation, seed, batch size, matériel — pour vérifier que les performances de PRECOG ne s'effondrent pas hors des conditions d'entraînement du meta-predictor.

---

## 20. Gestion de l'incertitude

PRECOG doit systématiquement produire, en plus d'une prédiction :

- une **incertitude calibrée** (par ensembles de prédicteurs, quantile regression, ou méthode bayésienne),
- une distinction entre **incertitude du modèle** (manque de connaissance), **incertitude des données** (ambiguïté intrinsèque du problème) et **stochasticité de l'entraînement** (variance entre seeds).

Exemple de sortie :

```text
Configuration A : prédiction = 95 %, confiance = 91 %
Configuration B : prédiction = 94 %, confiance = 52 %
```

L'incertitude alimente directement la fonction d'acquisition (§9.8) et la politique de décision (§9.11) : une configuration incertaine mais potentiellement informative peut être testée en priorité pour réduire l'incertitude globale du système (active learning).

---

## 21. Causalité vs corrélation

Une corrélation observée entre un signal pré-entraînement (ex. variance du gradient) et la performance finale peut être confondue par une variable tierce (l'architecture, typiquement). PRECOG doit donc :

1. Identifier les relations candidates à partir des corrélations du meta-dataset.
2. Formuler des hypothèses explicites.
3. Concevoir des expériences contrôlées où seule la variable candidate change (architecture, dataset et optimiseur fixés).
4. Ne promouvoir une relation au rang de « connaissance exploitable en production » qu'après validation causale, ou à défaut la marquer explicitement comme « corrélation non validée causalement ».

---

## 22. Généralisation et détection de distribution-shift

Le test de généralisation (P6, §15) est considéré comme **le plus important scientifiquement**. Il exige de :

- entraîner/valider le meta-predictor sur un sous-ensemble d'architectures et de datasets, puis
- tester sur des architectures et datasets **structurellement absents** de l'ensemble d'entraînement (ex. entraîner sur CNN/MLP/ResNet, tester sur Transformer).

Le module OOD (§9.13) doit estimer $P(\text{tâche connue})$ et déclencher automatiquement une augmentation du budget de validation (mode PROBE) lorsque la tâche est jugée éloignée du meta-dataset, plutôt que de produire une prédiction PURE trop confiante hors distribution.

---

## 23. Risques méthodologiques et mitigations

| Risque | Description | Mitigation |
|---|---|---|
| Data leakage | Information du dataset réel s'infiltrant dans l'analyse PURE | Contrat Zero-Training strict (§5), audit des features autorisées |
| Benchmark overfitting | PRECOG optimisé en boucle sur les mêmes benchmarks (NAS-Bench-201, HPOBench…) | Jeu de TEST verrouillé, non révélé avant évaluation finale |
| Biais du meta-dataset | Sur-représentation de certaines architectures/domaines | Curriculum de diversification, suivi explicite de la couverture du meta-dataset |
| Distribution shift non détecté | Application de PRECOG hors de son domaine de validité sans avertissement | Module OOD (§9.13) + budget de validation adaptatif |
| Stochasticité des entraînements | Confondre variance de seed et effet réel d'une configuration | Multi-seed obligatoire, intervalles de confiance (§15.3) |
| Incertitude mal calibrée | Confiance affichée ne reflétant pas l'erreur réelle | Calibration régulière, tests de calibration (ex. reliability diagrams) |
| Coût excessif de PRECOG lui-même | Le coût d'analyse dépasse l'économie réalisée | Mesure systématique de $Cost_{PRECOG} + Cost_{PROBE}$ vs $Cost_{HPO\ classique}$ (§24) |
| Corrélation trompeuse | Relation exploitée en production non causale | Module de découverte causale (§21) |
| Dépendance à une famille d'architectures | Bonne performance uniquement sur les architectures du meta-dataset | Curriculum progressif (MLP → CNN → Transformer → inconnu), tests de généralisation stricts |

---

## 24. Économie du système

PRECOG n'a de valeur pratique que si :

$$
Cost_{PRECOG} + Cost_{PROBE\ éventuel} \; \ll \; Cost_{HPO\ classique\ ou\ multiples\ FULL\ TRAINING}
$$

Cette contrainte doit être mesurée à chaque évaluation, pas seulement supposée. Un système théoriquement précis mais dont l'inférence est trop coûteuse (par exemple un meta-predictor nécessitant lui-même énormément de calcul) doit être considéré comme un échec économique, même en cas de bon score de ranking.

---

## 25. Roadmap de développement

```text
V1 — Fondations
  Learning Rate, Batch Size, Optimizer, Initialization
  (analyse zero-cost de base, sans meta-learning)

V2 — Configuration complète
  Weight Decay, Warmup, Scheduler, Gradient Accumulation

V3 — Architecture
  Dropout, Architecture (depth/width/activation/normalization)

V4 — Intelligence
  Meta-learning, Task Embeddings, NEAR, Zero-Cost combinés

V5 — Recherche adaptative
  Active Learning, Bayesian Optimization, Adaptive Short-Probe

V6 — Science
  Causal Discovery, OOD Detection, Failure Analysis,
  Scientific Discovery Engine
```

### Progression scientifique par phase (indicative)

```text
Phase A : fondations analytiques (Zero-Cost, NEAR, Initialization)
Phase B : meta-learning + Bayesian Optimization
Phase C : incertitude + active learning + acquisition adaptative
Phase D : prédiction de learning curves + probe adaptatif + failure analysis
Phase E : validation — tâches jamais vues, multi-seed, tests statistiques, reproductibilité
```

### Curriculum expérimental

```text
Niveau 1 : MLP sur datasets synthétiques
Niveau 2 : CNN sur vision
Niveau 3 : ResNet / architectures modernes
Niveau 4 : Transformers
Niveau 5 : fine-tuning de LLM
Niveau 6 : modèles et datasets jamais vus (test de généralisation ultime)
```

---

## 26. Critères de réussite

Un jalon de PRECOG n'est considéré atteint que si **simultanément**, sur un jeu de test verrouillé et jamais utilisé pour l'entraînement :

1. le ranking (Spearman ρ) atteint le seuil visé pour le niveau considéré,
2. le Recall@K atteint le seuil visé,
3. la réduction de compute mesurée atteint le seuil visé,
4. la performance finale retenue reste dans la tolérance de perte définie a priori,
5. les résultats se maintiennent sur des tâches/architectures/datasets jamais vus (généralisation),
6. les résultats sont reproductibles (multi-seed, intervalles de confiance, environnement documenté).

Un système qui n'atteint qu'une partie de ces critères (ex. bon ranking mais mauvaise généralisation) n'est **pas** considéré comme ayant atteint le jalon.

---

## 27. Limites connues

- La généralisation à des familles d'architectures radicalement nouvelles (au-delà de celles représentées dans le meta-dataset) n'est pas garantie et doit être traitée comme une hypothèse à tester, pas comme acquise.
- Les signaux zero-cost actuels de la littérature ne sont pas universellement fiables ; leur combinaison réduit le risque mais ne l'élimine pas.
- La qualité du meta-dataset borne intrinsèquement la qualité du meta-predictor : un meta-dataset peu diversifié produira des prédictions optimistes hors de sa couverture réelle.
- Le mode PROBE introduit un coût réel, même minime ; toute revendication de gain doit être nette de ce coût.
- La distinction causalité/corrélation reste partielle : certaines relations exploitées resteront, en pratique, des corrélations robustes plutôt que des causes démontrées, et doivent être présentées comme telles.

---

## 28. Perspectives

À plus long terme, l'ambition scientifique de PRECOG dépasse l'HPO : il s'agit de construire une théorie opérationnelle de la **dynamique d'apprentissage prédictible**, c'est-à-dire une fonction

$$
F : (\text{Model}, \text{Data}, \text{Initialization}, \text{Hyperparameters}) \rightarrow \text{Training trajectory}
$$

capable d'anticiper la trajectoire de la loss $L(t)$ avant l'entraînement complet. Si cette direction aboutit, PRECOG cesserait d'être uniquement un optimiseur d'hyperparamètres pour devenir un **modèle prédictif de la dynamique d'apprentissage**, avec un potentiel de contribution scientifique propre (au-delà de l'intégration d'outils existants).

---

## 29. Architecture de production (cible à terme)

PRECOG, en tant que plateforme, doit pouvoir :

1. Recevoir un modèle vierge, les métadonnées/statistiques autorisées du dataset, et une description de l'environnement matériel.
2. Exécuter une analyse en mode **PURE** (aucune mise à jour de poids sur données réelles).
3. Produire une **distribution d'hyperparamètres** avec justification et niveau de confiance, ainsi qu'un **ensemble Pareto-optimal** de configurations selon les contraintes (performance/compute/données/temps).
4. Sur demande, valider les meilleures hypothèses via un budget minimal en mode **PROBE**.
5. Journaliser systématiquement l'expérience (y compris en cas d'usage en production) dans le meta-dataset, pour amélioration continue.

```text
Modèle vierge + Dataset (stats) + Hardware
                    │
                    ▼
              PRECOG (mode PURE)
                    │
                    ▼
     Distribution d'hyperparamètres + confiance
                    │
                    ▼
        Ensemble Pareto-optimal de configurations
                    │
             (optionnel) PROBE
                    │
                    ▼
        Configuration recommandée + justification
```

---

## 30. Synthèse — l'idée qui distingue PRECOG d'un HPO classique

> **PRECOG ne cherche pas simplement les meilleurs hyperparamètres après avoir entraîné de nombreuses configurations ; il cherche à apprendre la relation entre l'état initial d'un modèle, les propriétés du problème et les conditions d'apprentissage, afin de prédire — avant tout entraînement sur les données réelles — quelles configurations ont la plus forte probabilité de conduire à une convergence rapide et efficace.**

Toute évaluation, tout benchmark et toute communication scientifique autour de PRECOG doivent revenir à ce test : le système apporte-t-il une information exploitable **avant** l'entraînement, mesurable, généralisable, et économiquement justifiée — ou se contente-t-il de reproduire un HPO classique habillé différemment ?
