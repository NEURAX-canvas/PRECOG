# PreTrainOpt
## Document fondateur — Recherche, Architecture Technique & Stratégie Produit

**Sous-titre :** *Prédire, avant l'entraînement, les conditions qui font converger un modèle plus vite, avec moins de données et moins de calcul.*

**Statut :** document de travail — hypothèses de recherche non validées, à tester expérimentalement.

---

## Table des matières

1. Executive Summary
2. Problem Statement
3. Scientific Motivation
4. Research Questions
5. Hypotheses
6. State of the Art
7. Existing Projects
8. Google Vizier — Analyse
9. Theoretical Foundations
10. Training Dynamics
11. Hyperparameter Taxonomy
12. Initialization
13. Synthetic Learning Laboratory
14. Meta-Learning
15. Causal Experimental Framework
16. Mathematical Formulation
17. Optimization Objectives
18. System Architecture
19. Software Architecture
20. Data Architecture
21. Experiment Database
22. Meta-Dataset
23. Algorithms
24. Experimental Protocol
25. Baselines
26. Ablation Studies
27. Evaluation Metrics
28. Statistical Analysis
29. Production Architecture
30. API Design
31. MLOps
32. Distributed Computing
33. Security / Reliability
34. Failure Modes
35. Research Risks
36. Open Research Questions
37. Roadmap
38. MVP
39. Future Extensions
40. Potential Scientific Contributions
41. Potential Industrial Applications
42. Open-source Strategy
43. Product Strategy
44. Final Research Thesis

Annexe A — Identité du projet (noms, tagline, mission)
Annexe B — Recommandation finale (prototype, expériences prioritaires, 3 hypothèses à tester en premier)

---

## 1. Executive Summary

L'entraînement d'un réseau de neurones est aujourd'hui piloté par un cycle **essai-erreur** : on choisit une configuration (learning rate, optimizer, batch size, initialisation…), on entraîne, on observe la loss, on ajuste. Des outils comme **Google Vizier**, **Optuna** ou **Hyperband** automatisent ce cycle, mais ne changent pas sa nature : ils restent des boucles *configuration → entraînement → métrique → nouvelle configuration*, où chaque itération coûte un entraînement (complet ou partiel).

**PreTrainOpt** part d'une question différente :

> Peut-on, à partir de propriétés observables **avant** ou avec un minimum d'entraînement réel (architecture du modèle, statistiques de la tâche, géométrie locale de la loss autour de l'initialisation), **prédire** une configuration d'entraînement qui converge plus vite, avec moins de données et moins de calcul — plutôt que de la *découvrir* par essais successifs ?

Ce document :

- pose la question de recherche et la décompose en sous-questions testables ;
- distingue explicitement ce qui est **établi**, ce qui est **plausible mais non démontré**, et ce qui constitue **notre hypothèse propre** ;
- propose une méthodologie expérimentale causale (pas seulement corrélationnelle) fondée sur un **laboratoire de tâches synthétiques** ;
- définit une architecture logicielle (Rust + Python) permettant de construire ce laboratoire, d'y faire tourner des milliers d'expériences contrôlées, et d'en extraire un **meta-modèle prédictif** ;
- propose une roadmap en 8 versions, du prototype MLP jusqu'à une API de production ;
- conclut par une recommandation concrète sur le premier prototype à construire.

Le projet est délibérément conçu pour **pouvoir échouer proprement** : si l'hypothèse centrale ne tient pas (les propriétés pré-entraînement ne suffisent pas à prédire la dynamique d'apprentissage), le laboratoire synthétique et l'*experiment database* construits en chemin restent des contributions utiles en elles-mêmes (étude empirique de la training dynamics, benchmark de baselines HPO, etc.).

---

## 2. Problem Statement

**Constat.** Le coût d'entraînement d'un modèle dépend fortement d'un ensemble de décisions prises *avant* le premier pas de gradient : initialisation, learning rate, optimizer, batch size, architecture, schedule. Ces décisions sont aujourd'hui choisies par :

- des heuristiques héritées de la littérature (ex. He init pour ReLU, LR ≈ 3e-4 pour Adam) ;
- des recherches automatiques coûteuses (grid/random search, Bayesian optimization, Vizier) qui nécessitent de nombreux entraînements complets ou partiels ;
- de l'intuition d'ingénieur, difficile à transférer et à reproduire.

**Problème.** Il n'existe pas aujourd'hui de système qui, à partir de la seule description d'un modèle et d'une tâche (avant tout entraînement significatif), **prédit** une configuration proche de l'optimum — au lieu de la *rechercher* par essais.

**Formulation.** On cherche à remplacer, ou au minimum à amorcer intelligemment, la boucle classique :

$$
H \rightarrow \mathrm{Train}(H) \rightarrow \mathrm{Performance}
$$

par une fonction de prédiction :

$$
X_{model}, X_{task}, X_{data} \;\longrightarrow\; \widehat{H^*}
$$

où \(\widehat{H^*}\) est une configuration d'entraînement (initialisation, LR, optimizer, batch, schedule, etc.) obtenue **sans** — ou avec un budget d'entraînement très inférieur à — une recherche d'hyperparamètres classique.

**Ce que ce projet n'est pas.** Ce n'est pas un *hyperparameter tuner* de plus. Un tuner cherche ; nous voulons **prédire**, quitte à corriger ensuite avec un budget d'entraînement minimal (« few-step probing », voir §15).

---

## 3. Scientific Motivation

Trois observations motivent le projet :

1. **Le transfer learning fonctionne.** Un modèle pré-entraîné apprend une nouvelle tâche avec infiniment moins de données qu'un modèle vierge, parce qu'il part d'une meilleure région de l'espace des paramètres. Cela prouve que *le point de départ* compte autant que l'algorithme d'optimisation.
2. **La géométrie locale de la loss est calculable sans entraînement complet.** Le gradient et des approximations de la courbure (Hessienne, NTK) sont observables dès l'initialisation, en un ou quelques *forward/backward pass*. Si ces quantités sont informatives sur la dynamique future, elles constituent un signal *bon marché*.
3. **Les outils de HPO actuels ignorent la structure du problème.** Vizier ou Optuna traitent l'entraînement comme une boîte noire \(f(x)\) ; ils ne réutilisent aucune connaissance d'une tâche à l'autre (sauf via des heuristiques de warm-start). Un système de meta-apprentissage entraîné sur des milliers de tâches pourrait, en théorie, généraliser cette connaissance.

Ces trois observations ne *prouvent* pas que notre approche fonctionnera — elles justifient seulement qu'elle **vaut la peine d'être testée rigoureusement**.

---

## 4. Research Questions

**Question principale (RQ0)**

> Dans quelle mesure peut-on prédire les conditions d'entraînement (initialisation, hyperparamètres) permettant une convergence rapide et une forte *sample efficiency*, à partir d'informations disponibles avant l'entraînement complet ?

**Sous-questions**

| # | Question | Type de réponse attendue |
|---|---|---|
| Q1 | Peut-on prédire un learning rate efficace sans entraînement complet ? | Corrélation puis modèle prédictif |
| Q2 | Peut-on prédire l'optimizer approprié (SGD/Adam/AdamW/Lion…) ? | Classification |
| Q3 | Peut-on prédire le batch size ? | Régression / classification ordinale |
| Q4 | Peut-on prédire weight decay, warmup, LR schedule ? | Régression multi-sortie |
| Q5 | Peut-on trouver une meilleure stratégie d'initialisation que les heuristiques standards ? | Comparatif |
| Q6 | Peut-on prédire le nombre de samples nécessaires pour atteindre une performance cible ? | Régression (loi d'échelle locale) |
| Q7 | Peut-on prédire le nombre de steps nécessaires pour atteindre une loss cible ? | Régression |
| Q8 | Les propriétés du modèle vierge (spectre, normes, architecture) prédisent-elles sa dynamique future ? | Analyse de feature importance |
| Q9 | Des tâches synthétiques suffisent-elles à apprendre ces relations ? | Étude de transférabilité |
| Q10 | Ces connaissances se transfèrent-elles à des modèles et données réelles ? | Validation externe (out-of-distribution) |

Chaque sous-question est associée à une expérience dédiée dans le protocole (§24).

---

## 5. Hypotheses

Formulées explicitement pour être **falsifiables**.

- **H1 (signal pré-entraînement).** Les caractéristiques du modèle vierge et de la tâche (avant tout entraînement significatif) portent une information statistiquement exploitable sur la configuration d'entraînement optimale.
- **H2 (transférabilité synthétique → réel).** Une relation apprise sur des tâches synthétiques génère des prédictions meilleures que les heuristiques par défaut sur des tâches réelles comparables.
- **H3 (coût de prédiction ≪ coût d'entraînement).** Le coût de calcul de la prédiction (features + inférence du meta-modèle, éventuellement + un *probe* court) est très inférieur au coût d'une recherche d'hyperparamètres classique, pour un gain de performance comparable ou meilleur.
- **H4 (non-universalité).** Il n'existe **pas** une configuration universelle ; la configuration optimale dépend conjointement de l'architecture, de la tâche et des données — donc un prédicteur *conditionnel* est nécessaire, pas une simple règle empirique globale.
- **H5 (rendements décroissants du probing).** Au-delà d'un certain budget de *few-step probing* (~0.1–1 % du training), le gain marginal d'information sur la configuration optimale décroît fortement.

Chaque hypothèse est testée indépendamment (§24, §26) ; l'échec d'une hypothèse ne condamne pas les autres.

---

## 6. State of the Art

| Établi (littérature) | Utilisé industriellement | Plausible mais non démontré | Notre hypothèse propre |
|---|---|---|---|
| Xavier/He init réduisent l'explosion/disparition du gradient | AdamW + cosine schedule + warmup en standard LLM | Les statistiques spectrales à l'init prédisent le LR optimal | Un meta-modèle entraîné sur tâches synthétiques transfère à des tâches réelles |
| Le NTK décrit la dynamique de réseaux infiniment larges | Bayesian optimization (Vizier, Optuna) pour le HPO | Le NTK à l'initialisation est un proxy exploitable en pratique (largeur finie) | Un budget de probing de 0.1–1 % suffit à corriger une prédiction *zero-shot* |
| Les *scaling laws* relient taille de modèle/données/compute à la loss | Transfer learning / fine-tuning à partir de checkpoints pré-entraînés | Les scaling laws locales (petite échelle) prédisent le comportement à plus grande échelle | Une architecture-aware + data-aware initialization bat les heuristiques standards de façon généralisable |
| Le batch size interagit avec le LR optimal (règle linéaire empirique) | Gradient clipping, LR warmup pour stabiliser les Transformers | La cohérence directionnelle du gradient (cosine successif) est corrélée à la vitesse de convergence | Les features de tâche + modèle suffisent, sans accès aux vraies données de la tâche cible |

Ce tableau doit être maintenu à jour au fil du projet — chaque case droite qui se déplace vers la gauche est un résultat publiable.

---

## 7. Existing Projects

- **Google Vizier** — service de black-box optimization (Bayesian optimization + bandits), utilisé en interne chez Google. Analyse détaillée au §8.
- **Optuna** — framework open-source de HPO, TPE (Tree-structured Parzen Estimator), pruning intégré (early stopping des essais peu prometteurs).
- **Ray Tune / Hyperband / ASHA** — recherche à grande échelle avec arrêt précoce agressif des essais peu prometteurs (successive halving).
- **Population Based Training (PBT, DeepMind)** — hybride évolution + recherche, mute les hyperparamètres *pendant* l'entraînement plutôt qu'entre essais séparés.
- **AutoML-Zero, NAS (Neural Architecture Search)** — recherche automatique d'architectures, proche mais orthogonale (nous supposons l'architecture donnée).
- **µP (maximal update parametrization, Microsoft/Tensor Programs)** — reparamétrisation qui rend le LR optimal quasi-invariant à la largeur du réseau : exemple concret qu'une propriété *structurelle* du modèle peut réduire drastiquement le besoin de recherche d'hyperparamètres. **Référence directe et sérieuse pour PreTrainOpt.**
- **DeepMind "Scaling Laws" / Chinchilla** — lois empiriques reliant taille de modèle, taille de dataset et compute optimal ; proche en esprit (prédire *avant* d'avoir tout entraîné) mais à une échelle différente (across-run, pas within-run dynamics).

**Positionnement.** PreTrainOpt se situe entre µP (structurel, garanties théoriques mais scope étroit) et Vizier (empirique, scope large mais coûteux). Notre pari : combiner un signal structurel (comme µP) avec un meta-modèle appris (comme Vizier apprend d'un historique d'essais), mais en amont de l'entraînement plutôt que pendant.

---

## 8. Google Vizier — Analyse

**Principe.** Vizier traite l'entraînement comme une fonction boîte noire \(f(x)\) à optimiser :

```
Search Space → Vizier → Hyperparameters → Training → Metric → Vizier → ...
```

**Composants clés :**

- *Search space* : domaines (souvent log-scale pour LR, weight decay) et types (continu, discret, catégoriel) des hyperparamètres.
- *Objective* : une ou plusieurs métriques à optimiser (ex. validation loss, ou un objectif composite).
- *Trials* : chaque essai = une configuration testée + son résultat.
- *Bayesian optimization* : un modèle probabiliste (souvent processus gaussien ou modèle de type TPE) apprend la surface \(f(x)\) à partir des essais passés et propose le point suivant en arbitrant exploration/exploitation.
- *Early stopping* : arrêt des essais peu prometteurs avant la fin de l'entraînement (économie de compute).
- *Multi-objective* : recherche de front de Pareto quand plusieurs métriques s'opposent (ex. accuracy vs latence).

**Limite fondamentale pour notre objectif.** Vizier **entraîne toujours** pour évaluer une configuration — même partiellement. Il n'a aucune notion de « caractéristiques du modèle/de la tâche » réutilisables d'une recherche à l'autre : chaque nouvelle tâche redémarre (sauf warm-start manuel).

**Différence avec PreTrainOpt :**

```
Vizier :        Configuration → Training → Metric
PreTrainOpt :    Model/Task analysis → Prediction → Configuration → (Probe minimal) → Validation
```

**Rôle de Vizier dans notre projet.** Il n'est pas un concurrent à remplacer d'emblée mais un **outil pour construire le meta-dataset** : pendant la phase de recherche (laboratoire synthétique), Vizier (ou un équivalent Bayesian optimization) sert à trouver la configuration quasi-optimale *réelle* de chaque tâche synthétique — ce résultat devient un exemple d'entraînement pour notre meta-modèle. Vizier est donc utilisé **hors ligne**, comme génération de vérité terrain, pas comme composant du système final.

---

## 9. Theoretical Foundations

- **Descente de gradient et rôle du LR.** \(\theta_{t+1} = \theta_t - \eta \nabla_\theta L\) — le LR contrôle l'amplitude du pas ; trop petit → convergence lente ; trop grand → divergence/oscillation. La région stable dépend de la courbure locale (voir Hessienne).
- **Neural Tangent Kernel (NTK).** Dans la limite de largeur infinie, la dynamique d'un réseau entraîné par gradient descent est équivalente à un modèle linéaire dans un espace de features fixé par le noyau tangent à l'initialisation \(K(x,x') = \nabla_\theta f(x)^\top \nabla_\theta f(x')\). En largeur finie, le NTK évolue pendant l'entraînement, mais son spectre à l'initialisation reste un indicateur exploité dans la littérature pour analyser la « trainability ».
- **µP (maximal update parametrization).** Reparamétrisation des poids et du LR par couche telle que la dynamique d'apprentissage (au premier ordre) devienne invariante à la largeur du réseau — permettant de régler le LR sur un petit modèle et de le transférer directement à un grand modèle. C'est la preuve la plus concrète, à ce jour, qu'une propriété structurelle **connue avant training** peut remplacer une recherche d'hyperparamètres.
- **Scaling laws.** Relations empiriques \(L(N, D, C) \approx\) fonction puissance de la taille de modèle \(N\), de données \(D\), de compute \(C\). Utiles pour extrapoler, mais définies *entre* runs complets, pas *dans* la dynamique d'un run — pertinence indirecte pour PreTrainOpt (comme inspiration méthodologique).
- **Analyse de la Hessienne / sharpness.** La courbure locale \(\nabla^2 L(\theta_0)\) borne la taille de pas stable (analogue à la condition de stabilité \(\eta < 2/\lambda_{max}\) en optimisation convexe quadratique). Le calcul exact est coûteux (\(O(P^2)\)) ; des approximations (Hutchinson trace estimator, power iteration sur le produit Hessien-vecteur) sont utilisables à coût \(O(P)\) par évaluation.
- **Information de Fisher.** \(F = \mathbb{E}[\nabla \log p(y|x;\theta)\nabla \log p(y|x;\theta)^\top]\) — relie la géométrie de la loss à la courbure ; utilisée par les optimizers naturels (K-FAC) et comme proxy de « quantité d'information exploitable » par les données.

**Conclusion de section.** Il existe des fondations théoriques *partielles* qui rendent l'hypothèse H1 plausible (NTK, µP, Hessienne locale) — mais aucune ne fournit, en l'état, un prédicteur généraliste couvrant tous les hyperparamètres (optimizer, batch, schedule). C'est précisément l'espace que PreTrainOpt explore empiriquement.

---

## 10. Training Dynamics

Variables à instrumenter à chaque step (ou à intervalle régulier) pendant les entraînements du laboratoire :

$$
L_t,\quad \|\nabla L_t\|,\quad \|\theta_t\|,\quad \|\Delta\theta_t\|,\quad \frac{\|\nabla L_t\|}{\|\theta_t\|},\quad \cos(g_t, g_{t-1})
$$

| Signal | Utilité | Coût | Calculable avant training complet ? |
|---|---|---|---|
| Norme du gradient \(\|\nabla L\|\) | Détecte vanishing/exploding gradients | Faible (déjà calculé) | Oui — dès le 1er backward |
| Cosinus successif \(\cos(g_t,g_{t-1})\) | Cohérence directionnelle ≈ proxy de « qualité » du signal d'apprentissage | Faible | Nécessite ≥ 2 steps |
| Variance du gradient (entre échantillons d'un batch) | Bruit d'estimation, lié au batch size optimal | Moyen | Oui, sur quelques batches |
| Norme des mises à jour \(\|\Delta\theta\|\) | Vitesse effective de déplacement | Faible | Après 1 step |
| Statistiques d'activation (moyenne/variance par couche) | Détecte saturation, dead ReLU | Faible | Oui — 1 forward pass |
| Statistiques des poids (norme par couche, distribution) | Qualité de l'initialisation | Nul (poids connus) | Oui — avant tout training |
| Approximation de la courbure (Hutchinson trace, power iteration) | Stabilité, LR max théorique | Moyen à élevé | Oui — quelques backward supplémentaires |
| NTK (spectre, condition number approximés) | « Trainability » théorique | Élevé (approximations nécessaires en pratique) | Oui à l'init, coûteux à grande échelle |
| Sharpness (loss autour de \(\theta\) après perturbation) | Lien avec la généralisation | Élevé | Nécessite plusieurs forward |

**Classement pour un système « bon marché » (candidats prioritaires) :** statistiques de poids/activations à l'init, norme et variance du gradient sur quelques batches, cosinus successif sur une courte fenêtre. **Candidats coûteux à différer en V2+ :** NTK complet, Hessienne complète, sharpness par perturbation exhaustive.

---

## 11. Hyperparameter Taxonomy

### Optimisation
learning rate · optimizer (SGD/Adam/AdamW/Lion…) · momentum · β1 · β2 · ε · weight decay · gradient clipping

### Training
batch size · gradient accumulation · epochs · warmup (durée, forme) · scheduler (cosine/exponentiel/step/constant) · mixed precision

### Architecture
depth · width · activation · normalisation (BatchNorm/LayerNorm/RMSNorm) · connexions résiduelles · configuration d'attention · méthode d'initialisation

### Initialisation
Xavier/Glorot · He/Kaiming · orthogonale · normale/uniforme · scaled init · *architecture-aware* (ex. µP) · *data-aware* (calibrée sur un échantillon de données)

### Données
taille du dataset · bruit · diversité · redondance · distribution · entropie · complexité · déséquilibre de classes · curriculum · augmentation

Pour **chaque** hyperparamètre, la grille d'analyse standard à appliquer (documentée une fois, appliquée systématiquement dans le meta-dataset) :

1. rôle fonctionnel ;
2. influence sur le gradient (norme, variance, direction) ;
3. influence sur la convergence (vitesse, stabilité) ;
4. interactions connues avec d'autres hyperparamètres (ex. LR ↔ batch size, LR ↔ largeur via µP) ;
5. comment le mesurer empiriquement dans le laboratoire ;
6. quel(s) signal(aux) pré-training pourrai(en)t le prédire ;
7. quel algorithme de recherche l'optimise le mieux en *ground truth* (Bayesian opt, grid, etc.).

---

## 12. Initialization

Méthodes à comparer systématiquement (baselines obligatoires du benchmark d'initialisation) :

- **Xavier/Glorot** — variance calibrée pour activations linéaires/tanh.
- **He/Kaiming** — variance calibrée pour ReLU et variantes.
- **Orthogonale** — préserve la norme lors de la propagation, utile en RNN profonds.
- **Normale / uniforme simples** — baselines naïves.
- **Scaled init** (ex. GPT-2 style : échelle en \(1/\sqrt{2L}\) pour les couches résiduelles profondes).
- **Architecture-aware (µP)** — LR et variance d'initialisation par couche dépendant explicitement de la largeur, pour rendre la dynamique invariante à l'échelle.
- **Data-aware init** — calibrée à partir d'un échantillon (LSUV — *Layer-Sequential Unit-Variance*, ou normalisation des activations mesurée sur un mini-batch avant training).
- **Nouvelles méthodes candidates (à explorer, non validées)** — initialisation conditionnée par les features de tâche prédites par notre propre meta-modèle (Q5).

---

## 13. Synthetic Learning Laboratory

Composant central du projet : un générateur de **tâches contrôlées**, permettant de faire varier un facteur à la fois (nécessaire pour l'inférence causale, §15).

**Fonctions génératrices types :**

$$
y = x_1 + x_2 \qquad y = \sin(x_1) + 0.5x_2^2 - x_3x_4 + \epsilon \qquad y = \sin(x_1x_2) + e^{-x_3}
$$

**Paramètres contrôlables :**

- dimension d'entrée ;
- niveau de bruit \(\epsilon\) ;
- complexité (degré de non-linéarité, nombre de termes d'interaction) ;
- redondance (fraction de features corrélées/dupliquées) ;
- diversité / distribution (uniforme, gaussienne, mélange) ;
- taille du dataset ;
- déséquilibre de classes (pour les tâches de classification).

**Architectures couvertes en V0.1 :** MLP (regression/classification synthétique). Extension prévue : CNN sur images synthétiques procédurales (formes, textures paramétriques), Transformer miniature sur séquences synthétiques (tâches de copie, tri, parité — inspirées des benchmarks d'algorithmic reasoning).

**Pourquoi synthétique plutôt que réel dès le départ ?** Parce qu'on contrôle exactement la variable qu'on fait varier — condition nécessaire pour distinguer corrélation et causalité (§15). Un dataset réel confond systématiquement plusieurs facteurs (bruit, redondance, distribution) qu'on ne peut pas isoler.

---

## 14. Meta-Learning

**Formulation du problème :**

$$
(X_{model}, X_{task}, X_{data}) \;\longrightarrow\; \mathrm{OptimalTrainingConfiguration}
$$

**Approches candidates, comparées :**

| Approche | Précision attendue | Coût | Complexité d'implémentation | Scalabilité | Adapté au 1er prototype ? |
|---|---|---|---|---|---|
| Modèle supervisé simple (gradient boosting / random forest sur features tabulaires) | Moyenne | Faible | Faible | Bonne | **Oui — recommandé** |
| Gaussian Processes (surrogate) | Bonne en faible dimension | Moyen | Moyen | Faible (mise à l'échelle en \(O(n^3)\)) | Non (V2+) |
| Bayesian optimization (par tâche, pas meta) | Bonne mais coûteuse par tâche | Élevé (entraînements réels) | Faible (Optuna/Vizier existants) | Bonne | Utilisé en génération de vérité terrain, pas comme prédicteur final |
| Réseau de neurones (MLP sur features) | Bonne si assez de données meta | Moyen | Moyen | Bonne | V0.3+ une fois le meta-dataset assez grand |
| Graph Neural Network (représentation de l'architecture comme graphe) | Potentiellement la meilleure généralisation inter-architectures | Élevé | Élevé | Moyenne | V0.4+ (quand on couvre plusieurs familles d'architectures) |
| Transformers pour meta-learning (en confonction de séquences d'essais) | Prometteur mais data-hungry | Élevé | Élevé | Bonne à grande échelle | Recherche exploratoire, pas prioritaire |
| Learned optimizers (méta-apprentissage de la règle de mise à jour elle-même) | Ambitieux, hors scope initial | Très élevé | Très élevé | Faible en l'état de l'art | Non — piste séparée (§27) |

**Recommandation pour le prototype (V0.2) :** un modèle **gradient boosting** (type LightGBM/XGBoost) sur features tabulaires (statistiques du modèle + statistiques de la tâche). Justification : interprétable (feature importance directement exploitable pour Q8), peu de données nécessaires comparé à un réseau de neurones, rapide à itérer, standard robuste en tabulaire.

---

## 15. Causal Experimental Framework

**Principe.** Ne pas se contenter de corrélations observées sur le meta-dataset — vérifier, par expérimentation contrôlée, que changer un facteur *cause* effectivement un changement de dynamique.

```
Expérience contrôlée
        ↓
Changer UN SEUL facteur
        ↓
Mesurer l'effet (steps-to-threshold, etc.)
        ↓
Répéter (autres graines aléatoires)
        ↓
Analyse des interactions (2 facteurs à la fois)
        ↓
Hypothèse causale
```

**Méthodes à mobiliser :**

- **Plans d'expériences factoriels** (*factorial design*) — faire varier \(k\) facteurs à 2 ou 3 niveaux simultanément, avec réplication, pour estimer effets principaux et interactions à moindre coût qu'un balayage exhaustif.
- **Études d'ablation** — retirer un composant du système (feature, module) et mesurer la perte de performance (voir §26).
- **Analyse de sensibilité / indices de Sobol** — décomposer la variance de la métrique de sortie par facteur et par interaction, pour quantifier (pas seulement classer) l'importance de chaque facteur.
- **ANOVA** — test statistique de significativité des effets principaux/interactions dans un plan factoriel.
- **SHAP (SHapley Additive exPlanations)** — sur le meta-modèle final, pour expliquer *quelles features* motivent chaque prédiction (utile pour Q8, et pour la confiance produit).
- **Graphes causaux (DAG) + expériences d'intervention** — au-delà de la corrélation observationnelle, formaliser les hypothèses de causalité (ex. « largeur → LR optimal » plutôt que l'inverse) et les tester par intervention directe (fixer la largeur, faire varier le reste).

**Pertinence relative.** Les plans factoriels + ANOVA/Sobol sont **indispensables** dès la phase 1 (peu coûteux, rigoureux). SHAP est utile en continu sur le meta-modèle. Les graphes causaux formels sont une couche de rigueur supplémentaire à introduire une fois les relations empiriques principales stabilisées (phase 3+).

---

## 16. Mathematical Formulation

**Problème général.**

$$
H^* = \arg\min_H \; \mathbb{E}\big[\mathcal{C}(H, \mathrm{Model}, \mathrm{Task})\big]
$$

où \(\mathcal{C}\) est un coût combinant performance, vitesse de convergence et budget de calcul (voir §17).

**Cible de prédiction directe :**

$$
T_\epsilon = \min\{t : L_t < \epsilon\}
$$

le nombre de steps nécessaires pour atteindre une loss cible \(\epsilon\). On cherche un modèle \(g\) tel que :

$$
\widehat{T_\epsilon} = g\big(X_{model}, X_{task}, H\big) \approx T_\epsilon
$$

**Reformulation du problème d'optimisation classique en problème de prédiction :**

$$
\underbrace{H \rightarrow \mathrm{Train}(H) \rightarrow \mathrm{Performance}}_{\text{approche classique (Vizier)}}
\qquad\Longrightarrow\qquad
\underbrace{X_{model}, X_{task}, X_{data} \rightarrow \mathrm{Predict}(H^*)}_{\text{PreTrainOpt}}
$$

**Objectif multi-critère (voir §17) :**

$$
\min\big(T_\epsilon,\; N_\epsilon,\; \mathrm{FLOPs}_\epsilon\big) \quad \text{sous contrainte} \quad \mathrm{Accuracy} \geq \mathrm{seuil}
$$

---

## 17. Optimization Objectives

Ne pas se limiter à la validation loss finale. Métriques cibles :

- \(T_\epsilon\) — **steps** nécessaires pour atteindre une loss cible \(\epsilon\) ;
- \(N_\epsilon\) — **samples** nécessaires pour atteindre une performance cible (*sample efficiency*) ;
- \(C_\epsilon\) — **compute** (FLOPs) nécessaire ;
- \(E_\epsilon\) — **énergie** consommée (proxy : FLOPs × facteur matériel, ou mesure directe si l'infra le permet) ;
- \(\mathrm{AUC} = \int L(t)\,dt\) — aire sous la courbe d'apprentissage, résume toute la trajectoire en un scalaire.

**Objectif composite :**

$$
\mathrm{Efficiency} = f(\mathrm{Performance}, N_\epsilon, T_\epsilon, C_\epsilon, \mathrm{Memory}, E_\epsilon)
$$

En pratique, on formule un problème **multi-objectif** (front de Pareto entre vitesse de convergence, sample efficiency et performance finale) plutôt qu'un scalaire unique arbitraire — la pondération entre objectifs est un choix produit, pas un fait scientifique, et doit rester explicite et ajustable.

---

## 18. System Architecture

```
                    Model
                      │
                      ↓
              Model Analyzer
                      │
                      ↓
             Feature Extraction
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
     Model Features          Task Features
          │                       │
          └───────────┬───────────┘
                      ↓
                Meta Predictor
                      ↓
             Candidate Configs
                      ↓
               Rank / Optimize
                      ↓
             Recommended Config
                      ↓
             Optional Probe (few-step)
                      ↓
             Final Configuration
                      ↓
                  Training
                      ↓
              Feedback / Logs
                      ↓
             Meta-dataset update
```

**Composants :**

- **Model Analyzer** — inspecte l'architecture (nombre de paramètres, profondeur, largeur, types de couches, normalisation) sans exécuter de training.
- **Feature Extraction** — calcule les features modèle (statistiques de poids à l'init, spectre approximé) et tâche (statistiques du dataset échantillonné : dimension, bruit estimé, entropie, redondance).
- **Meta Predictor** — le meta-modèle (§14), produit une ou plusieurs configurations candidates avec un score de confiance.
- **Rank/Optimize** — si plusieurs candidates, arbitrage (éventuellement via une mini-recherche locale autour de la prédiction).
- **Optional Probe** — quelques steps réels d'entraînement pour corriger la prédiction *zero-shot* si le budget le permet (§15 du prompt original / régimes définis au §15 ci-dessous... voir aussi la section dédiée "Zero-training ou minimal-training").
- **Feedback loop** — le résultat réel de l'entraînement complet est renvoyé dans l'*experiment database*, pour ré-entraîner périodiquement le meta-modèle (continual meta-learning, §23 du prompt / repris ci-dessous dans le Roadmap).

---

## 19. Software Architecture

Langage principal : **Rust** (performance, sûreté mémoire, cohérent avec l'écosystème déjà utilisé par ailleurs) avec **intégration Python** pour l'écosystème ML (PyTorch/JAX, notebooks d'analyse, prototypage rapide du meta-modèle).

```
pretrainopt/
├── core/           # types partagés, config, erreurs, traits communs
├── model/          # définition et introspection de modèles (MLP, CNN, Transformer)
├── taskgen/        # générateur de tâches synthétiques paramétriques
├── analysis/       # extraction de features (spectral, jacobien, courbure, statistiques)
├── initialization/ # stratégies d'initialisation (standard + architecture/data-aware)
├── optimization/   # optimizers, schedulers, gradient clipping
├── meta/           # meta-modèle : features → prédiction de configuration
├── experiments/    # runner d'expériences, orchestration des trials
├── benchmark/      # baselines (random/grid/Bayesian/Vizier/Optuna), comparateurs
├── storage/        # persistance de l'experiment database / meta-dataset
├── api/            # service d'inférence (prédiction de configuration)
├── cli/            # interface en ligne de commande
└── dashboard/      # visualisation des expériences, courbes, feature importance
```

**Responsabilités précises :**

- `core` : types de configuration (`TrainingConfig`, `ModelFeatures`, `TaskFeatures`), traits `Trainable`, `Measurable`.
- `model` : construction de modèles paramétrables (nombre de couches, largeur, activation) + introspection (comptage de paramètres, parcours des couches).
- `taskgen` : fonctions génératrices, contrôle du bruit/complexité/redondance, échantillonnage reproductible (graines explicites).
- `analysis` : calcul des signaux du §10 (normes, variance de gradient, cosinus successif, approximations de courbure via Hutchinson/power-iteration).
- `initialization` : implémentations Xavier/He/orthogonale/scaled/µP + hook pour stratégies apprises.
- `optimization` : SGD/Adam/AdamW/Lion, schedulers (cosine/step/exponentiel), warmup, clipping.
- `meta` : entraînement et inférence du meta-modèle (features → configuration), interface avec un backend Python (gradient boosting) via FFI ou service séparé.
- `experiments` : orchestration des runs (séquentiels ou parallèles), gestion des seeds, écriture dans l'*experiment database*.
- `benchmark` : implémentations/wrappers des baselines (interfaçage Optuna en Python ; Vizier via API si accessible ; grid/random en Rust natif).
- `storage` : schéma de données (§20-22), backend (voir stack §18 du prompt / stack technologique ci-dessous).
- `api` : endpoint de prédiction (voir §30).
- `cli` : commandes pour lancer une génération de tâches, un entraînement du laboratoire, une inférence de configuration.
- `dashboard` : visualisation (courbes de loss, feature importance SHAP, comparaison de baselines).

---

## 20. Data Architecture

Trois familles de données à modéliser :

1. **Task Registry** — définition des tâches synthétiques générées (paramètres génératifs, seed, statistiques calculées).
2. **Experiment Database** — un enregistrement par essai d'entraînement (voir §21).
3. **Meta-Dataset** — vue agrégée de l'Experiment Database, structurée comme un jeu de données d'apprentissage supervisé pour le meta-modèle (voir §22).

Flux :

```
Task Registry ──┐
                 ├──► Experiment Runner ──► Experiment Database ──► Meta-Dataset ──► Meta-Model
Model Registry ──┘                                  ▲                                   │
                                                     └───────────── Feedback loop ◄──────┘
```

---

## 21. Experiment Database

Schéma (par expérience) :

```text
experiment_id
timestamp
seed

# Model features
model_type, depth, width, n_params, activation, normalization,
init_method, weight_norm_stats, spectral_stats

# Task features
task_id, input_dim, noise_level, complexity_score, redundancy,
n_samples, distribution_type, class_imbalance

# Hyperparameters (= H, l'entrée testée)
learning_rate, optimizer, batch_size, weight_decay,
warmup_steps, scheduler_type, gradient_clip

# Dynamics (séries temporelles ou statistiques résumées)
loss_curve[], grad_norm[], grad_cosine_similarity[],
param_update_norm[], activation_stats[]

# Compute
flops, wall_clock_time, peak_memory, device

# Outcome (= la vérité terrain à prédire)
steps_to_threshold, samples_to_threshold, final_loss,
final_accuracy, converged (bool), diverged (bool)
```

Ce schéma sert à la fois de journal d'expérimentation (reproductibilité) et de source pour construire le meta-dataset.

---

## 22. Meta-Dataset

Vue dérivée de l'Experiment Database, une ligne = un couple (features pré-training, configuration testée, résultat) :

$$
\big(X_{model},\, X_{task},\, H\big) \;\longrightarrow\; \big(T_\epsilon,\, N_\epsilon,\, \mathrm{Accuracy}\big)
$$

Pour l'entraînement du meta-modèle **prédictif de \(H^*\)** (et non simplement prédictif du résultat d'un \(H\) donné), on retient pour chaque tâche/modèle la **meilleure configuration trouvée** par la recherche Bayesienne de référence (§8) comme cible :

$$
\big(X_{model},\, X_{task}\big) \;\longrightarrow\; H^*_{trouvé\;par\;Vizier/Optuna}
$$

Deux formulations sont donc utiles et complémentaires : un modèle de **régression du résultat** (utile pour l'analyse causale, §15) et un modèle de **prédiction directe de la configuration optimale** (utile pour le produit final, §29-30).

---

## 23. Algorithms

Algorithmes à implémenter/intégrer, par catégorie :

- **Génération de tâches** : échantillonnage paramétrique reproductible (fonctions génératrices + bruit contrôlé).
- **Recherche de référence (génération de vérité terrain)** : Bayesian optimization (TPE via Optuna, ou GP-based), Successive Halving/Hyperband pour accélérer la génération du meta-dataset à moindre coût.
- **Extraction de features** : Hutchinson trace estimator (approx. de \(\mathrm{tr}(H)\)), power iteration (approx. de \(\lambda_{max}\) de la Hessienne ou du NTK), statistiques de poids/activations (moyenne, variance, norme, kurtosis).
- **Meta-modèle** : gradient boosting (baseline), puis MLP/GNN en évolution (§14).
- **Explication** : SHAP pour l'attribution de features.
- **Optimisation causale** : plans factoriels, ANOVA, indices de Sobol (§15).

---

## 24. Experimental Protocol

| Phase | Objet | Hypothèse testée | Variables | Baseline | Critère de succès |
|---|---|---|---|---|---|
| **1** | MLP + tâches synthétiques | H1, Q1-Q7 | LR, optimizer, batch, init, 5 hyperparamètres | Défauts standards (Adam LR=3e-4) | Meta-modèle bat la baseline sur ≥ 60 % des tâches de test synthétiques |
| **2** | CNN + tâches synthétiques (images procédurales) | H1, H2 (généralisation à une autre famille d'archi) | + architecture (depth/width/kernel) | Idem + heuristiques CNN standards | Le meta-modèle entraîné en Phase 1 (ou ré-entraîné) transfère avec dégradation modérée |
| **3** | Transformer miniature | H1, H2, µP comme référence | + attention config | µP + AdamW standard | Comparable ou meilleur que µP seul sur *steps-to-threshold* |
| **4** | Datasets réels (petite échelle : ex. classification tabulaire/image simple) | H2, H3 | Idem + vraies statistiques de données | Vizier/Optuna avec budget équivalent | \(N_{ours} \le N_{baseline}\) et \(T_{ours} \le T_{baseline}\) à performance égale |
| **5** | Modèles pré-entraînés (fine-tuning) | H2, H3 | LR/schedule de fine-tuning | Heuristiques de fine-tuning standards | Réduction mesurable du nombre de steps de fine-tuning à performance égale |
| **6** | Modèles plus grands | H4, H5 (limites de scaling) | Budget de probing (0 % / 0.1 % / 1 %) | Phase 4/5 extrapolée naïvement | Identifier le point de rupture où la prédiction *zero-shot* devient insuffisante |

Chaque phase produit un rapport : hypothèse, résultat, hypothèse confirmée/infirmée/partielle, risques mis à jour.

---

## 25. Baselines

Comparaisons obligatoires, à chaque phase :

- hyperparamètres par défaut (ex. Adam LR=3e-4, pas de warmup) ;
- réglage manuel par un ingénieur expérimenté (si possible, pour calibrer l'écart avec l'expertise humaine) ;
- random search ;
- grid search ;
- Bayesian optimization (Optuna) ;
- Google Vizier (si accès disponible) ;
- Hyperband/ASHA ;
- méthodes d'initialisation classiques seules (sans le reste du système), pour isoler la contribution de l'initialisation vs les autres hyperparamètres.

**Règle de décision.** PreTrainOpt n'est considéré « performant » sur une phase que s'il domine (ou égale à coût très inférieur) la meilleure baseline **à budget de calcul comparable ou inférieur**.

---

## 26. Ablation Studies

```
Système complet
  − sans initialization predictor
  − sans task features
  − sans model features
  − sans gradient/curvature features
  − sans meta-learning (retour à Bayesian opt pur)
  − sans tâches synthétiques (entraînement direct sur peu de données réelles)
  − sans probing court (zero-shot pur)
```

Pour chaque variante : mesurer la dégradation sur les métriques du §27. Objectif : identifier **quelle composante porte réellement la valeur** — condition nécessaire pour prioriser les efforts d'ingénierie (V0.3 vs V0.4, etc.) et pour toute publication scientifique crédible.

---

## 27. Evaluation Metrics

- **StepsToThreshold** \(T_\epsilon\) — sensible au choix de \(\epsilon\), à définir par tâche relativement à la loss d'un modèle bien entraîné.
- **SamplesToThreshold** \(N_\epsilon\) — capture la sample efficiency indépendamment de la vitesse de calcul.
- **ComputeToThreshold** \(C_\epsilon\) — FLOPs, comparable indépendamment du matériel.
- **AreaUnderLearningCurve** — résume toute la trajectoire, robuste aux seuils arbitraires mais moins interprétable directement.
- **Prediction accuracy du meta-modèle** — écart entre \(H^*\) prédit et \(H^*\) réel (trouvé par recherche exhaustive), et écart de performance entre les deux configurations.
- **Confidence calibration** — le score de confiance retourné par le système correspond-il à la fréquence réelle de succès (fiabilité de l'incertitude, essentielle en production, §29) ?

**Avantages/limites.** \(T_\epsilon\) et \(N_\epsilon\) sont intuitifs mais dépendent du seuil choisi ; l'AUC est plus robuste mais agrège des phases d'entraînement de nature différente (transitoire rapide vs affinage lent) — les deux familles de métriques doivent être rapportées conjointement.

---

## 28. Statistical Analysis

- **Réplication obligatoire** — chaque expérience (surtout en Phase 1-3, peu coûteuses) répétée sur ≥ 5 graines aléatoires ; rapporter moyenne **et** dispersion (écart-type, intervalles de confiance).
- **Tests de significativité** — comparaison de baselines via tests appropriés (ex. test de Wilcoxon apparié plutôt qu'un simple delta de moyenne, pour tenir compte de la variance inter-graines).
- **ANOVA / Sobol** — décomposition de variance pour les plans factoriels (§15).
- **Correction pour comparaisons multiples** — dès lors que de nombreux hyperparamètres/tâches sont comparés simultanément (ex. correction de Bonferroni ou False Discovery Rate) pour éviter les faux positifs.
- **Rapport de feature importance (SHAP)** — systématique sur chaque version du meta-modèle, versionné avec le modèle correspondant.

---

## 29. Production Architecture

Le service reçoit :

```json
{
  "model": "...",
  "task_metadata": "...",
  "dataset_statistics": "...",
  "compute_budget": "...",
  "target_metric": "..."
}
```

et retourne :

```json
{
  "recommended_initialization": "...",
  "recommended_optimizer": "...",
  "recommended_lr": 0.0007,
  "recommended_batch_size": 64,
  "recommended_scheduler": "cosine",
  "expected_convergence": { "steps": 3800, "loss_threshold": 0.1 },
  "confidence_score": 0.78
}
```

Le **score de confiance** est une exigence de premier ordre : un système qui ne sait pas dire *quand il ne sait pas* est dangereux à intégrer dans un pipeline de production. Approche recommandée : quantile regression ou ensembles de meta-modèles (variance inter-modèles comme proxy d'incertitude).

---

## 30. API Design

- `POST /v1/analyze-model` — introspection d'un modèle fourni (checkpoint vierge ou définition d'architecture), retourne \(X_{model}\).
- `POST /v1/analyze-task` — statistiques calculées sur un échantillon de données/tâche, retourne \(X_{task}\).
- `POST /v1/predict-config` — entrée \(X_{model}, X_{task}\) (+ budget, métrique cible) → configuration recommandée + confiance.
- `POST /v1/probe` — lance un *few-step probing* optionnel et retourne une configuration affinée.
- `POST /v1/feedback` — soumission du résultat réel d'un entraînement complet, alimente le meta-dataset (§23 boucle de feedback).
- `GET /v1/experiments/{id}` — consultation d'une expérience journalisée.

Design REST simple en V1 ; gRPC envisageable en V2 si l'intégration dans des pipelines d'entraînement à faible latence le justifie.

---

## 31. MLOps

- **Versionnement** : du meta-modèle (avec ses métriques de validation), du meta-dataset (snapshot daté), du code (SemVer).
- **CI/CD** : tests de non-régression sur un sous-ensemble fixe de tâches synthétiques (« benchmark de fumée ») avant chaque déploiement du meta-modèle.
- **Monitoring** : suivi en production de l'écart prédiction/réalité (dérive du modèle), alerte si la calibration de confiance se dégrade.
- **Ré-entraînement périodique** : pipeline automatisé déclenché quand le volume de nouveaux feedbacks dépasse un seuil (continual meta-learning, §23).
- **Reproductibilité** : graines aléatoires explicites, capture de l'environnement (versions de libs, matériel) pour chaque expérience.

---

## 32. Distributed Computing

Le laboratoire synthétique doit pouvoir exécuter **des milliers d'entraînements courts en parallèle** — un problème d'*embarrassingly parallel batch scheduling* plutôt que de distributed training classique (un seul entraînement sur plusieurs GPU).

- **Orchestration** : Kubernetes (ou Ray pour une option plus légère et native ML) pour distribuer les runs du laboratoire sur un pool de workers CPU/GPU.
- **Stockage partagé** : object storage (S3-compatible) pour les checkpoints et logs bruts ; base de données structurée pour l'Experiment Database.
- **Scheduling adaptatif** : privilégier ASHA/Hyperband pour arrêter tôt les tâches synthétiques peu informatives et réallouer le budget de calcul.

Ce composant n'est nécessaire qu'à partir du moment où le volume d'expériences dépasse la capacité d'une seule machine (typiquement V0.3-V0.4, pas pour le MVP).

---

## 33. Security / Reliability

- **Isolation des runs** — chaque entraînement du laboratoire dans un environnement isolé (conteneur), pour éviter qu'une divergence numérique (NaN, explosion mémoire) n'affecte les autres runs.
- **Détection de divergence** — arrêt automatique des runs qui produisent des NaN/Inf ou dépassent un budget mémoire/temps, avec journalisation de l'échec comme donnée utile (un échec est une information, pas un simple rejet).
- **Validation des entrées API** — bornage des budgets de calcul demandés côté production, pour éviter qu'une requête ne déclenche un probing disproportionné.
- **Traçabilité** — chaque prédiction en production doit être reliée à la version exacte du meta-modèle et du meta-dataset qui l'ont produite (auditabilité).

---

## 34. Failure Modes

| Mode d'échec | Symptôme | Détection | Mitigation |
|---|---|---|---|
| Divergence numérique pendant un run du laboratoire | Loss = NaN | Monitoring automatique | Arrêt + log comme échec informatif |
| Meta-modèle en sur-apprentissage sur les tâches synthétiques | Bonnes perfs en test synthétique, mauvaises sur données réelles | Split train/val/test strict + validation externe (Phase 4+) | Régularisation, augmentation de la diversité des tâches synthétiques |
| Dérive de distribution en production | Confiance élevée mais résultats réels dégradés | Boucle de feedback (§23) + monitoring de calibration | Ré-entraînement périodique, alerte automatique |
| Coût de calcul du laboratoire sous-estimé | Budget explosé avant d'atteindre un meta-dataset exploitable | Suivi budgétaire par phase | Prioriser Hyperband/ASHA, réduire le nombre de graines en phase exploratoire |
| Features chères (NTK, Hessienne complète) trop coûteuses pour être utiles en production | Latence API inacceptable | Benchmark de latence par feature | Ne garder en production que les features validées comme *rentables* (§26 ablation) |

---

## 35. Research Risks

| Risque | Description | Expérience pour le tester |
|---|---|---|
| Optimalité fortement dépendante du dataset | \(H^*\) varie trop d'une tâche à l'autre pour être généralisable | Mesurer la variance de \(H^*\) à travers des tâches synthétiques *proches* (même famille, paramètres voisins) |
| Mauvaise transférabilité synthétique → réel | Le meta-modèle entraîné sur synthétique ne généralise pas | Phase 4 : validation externe stricte, hold-out de tâches réelles jamais vues |
| Espace d'architectures trop vaste | Impossible de couvrir suffisamment de diversité architecturale | Limiter le scope initial (MLP → CNN → Transformer miniature), mesurer la dégradation par famille |
| Impossibilité de prédire précisément la convergence | Le signal pré-training est trop faible | Étude de feature importance (Q8) tôt, avec seuil d'abandon défini à l'avance |
| Coût des features (NTK, Hessienne) prohibitif | Le système coûte presque autant que ce qu'il économise | Benchmark de coût vs valeur ajoutée par feature (ablation §26) |
| Distribution shift entre phase de recherche et production | Les tâches réelles diffèrent trop du laboratoire synthétique | Élargir progressivement la diversité du générateur de tâches |
| Meta-overfitting | Le meta-modèle mémorise les tâches du meta-dataset plutôt que d'apprendre une relation généralisable | Validation croisée stricte à l'échelle des *tâches* (pas des essais), tâches de test totalement disjointes |
| Hyperparamètres non stationnaires | La configuration optimale change au cours de l'entraînement lui-même (justifie schedules) | Comparer prédiction statique vs schedule prédit dynamiquement |
| Absence de relation universelle architecture ↔ configuration optimale | H1 est simplement fausse | C'est le risque central du projet — testé dès la Phase 1 avec un seuil d'abandon/pivot explicite |

**Principe directeur.** Chaque risque a une expérience assignée dans le protocole (§24) — aucun risque ne reste « à explorer plus tard » sans un test concret prévu.

---

## 36. Open Research Questions

Au-delà du scope initial, pistes à garder en réserve, chacune évaluée pour sa pertinence :

| Concept | Explication courte | Lien avec le projet | À intégrer ? | Expérience proposée |
|---|---|---|---|---|
| **Learned initialization** | Apprendre directement une fonction qui génère les poids initiaux | Extension directe de §12 | Oui, V0.3+ | Comparer init apprise vs µP vs He sur Phase 2-3 |
| **Learned optimizers** | Remplacer la règle de mise à jour elle-même par un modèle appris | Orthogonal, plus ambitieux | Non prioritaire | Piste séparée, à isoler du cœur du projet |
| **Neural scaling laws** | Lois puissance liant taille/données/compute à la loss | Inspiration méthodologique | Oui, en arrière-plan (Phase 6) | Vérifier si nos prédictions restent valables à travers les échelles |
| **Neural Tangent Kernel** | Cf. §9 | Feature candidate directe | Oui | Comparer spectre NTK approximé comme feature vs sans |
| **Loss landscape geometry / dynamical isometry** | Propriétés globales/locales de la surface de loss | Lié à §9 (Hessienne) | Oui, comme feature | Tester corrélation sharpness ↔ généralisation dans le laboratoire |
| **Spectral initialization** | Initialisation calibrée sur le spectre attendu des activations/gradients | Extension de §12 | Oui | Comparer à Xavier/He |
| **Gradient flow** | Analyse continue (EDO) de la dynamique de descente de gradient | Fondation théorique | En arrière-plan seulement | — |
| **Fisher information** | Cf. §9 | Feature candidate (lien avec K-FAC) | Oui, V0.4+ | Comparer coût/valeur vs Hessienne approximée |
| **Grokking** | Généralisation tardive et soudaine après une longue phase de mémorisation apparente | Cas limite intéressant pour tester la robustesse des prédictions de \(T_\epsilon\) | Oui, comme étude de cas | Tâches synthétiques connues pour produire du grokking (arithmétique modulaire) |
| **Lottery ticket hypothesis** | Sous-réseaux entraînables isolables dès l'initialisation | Lien indirect avec « qualité d'initialisation » | Exploratoire | Tester si les features d'un « bon » sous-réseau prédisent aussi un bon \(H^*\) |
| **Pruning / distillation** | Réduction de modèle post ou pendant training | Périphérique | Non prioritaire | — |
| **Curriculum learning** | Cf. doc. source #1 | Déjà dans la taxonomie données (§11) | Oui | Comparer ordre naïf vs curriculum sur tâches synthétiques à difficulté paramétrable |
| **Active learning / data selection / dataset valuation** | Sélectionner quelles données entraîner en premier/en priorité | Lien avec sample efficiency (§17) | Oui, V0.5+ (données réelles) | Comparer sélection aléatoire vs sélection guidée par le meta-modèle |
| **Synthetic data generation (au-delà du laboratoire)** | Générer des données d'entraînement synthétiques pour la tâche cible elle-même (pas seulement pour la recherche méta) | Distinct du Synthetic Learning Laboratory | Piste séparée | — |
| **Neural Architecture Search** | Recherche automatique d'architecture | Orthogonal (on suppose l'architecture donnée) | Non — hors scope explicite | — |
| **Learned HPO (meta-apprentissage de l'algorithme de recherche lui-même)** | Aller un cran plus loin que notre meta-prédicteur | Vision long terme | Recherche exploratoire V2.0 | — |

---

## 37. Positionnement Scientifique

Domaines de recherche concernés :

- **AutoML** (Automated Machine Learning) — cadre général.
- **Hyperparameter Optimization** — le champ le plus proche historiquement, mais notre approche diffère par la prédiction *a priori* plutôt que la recherche.
- **Meta-Learning** — cœur méthodologique (apprendre à travers les tâches).
- **Optimization Theory** — fondations (NTK, Hessienne, µP).
- **Training Dynamics** — objet d'étude empirique central.
- **Neural Architecture Search** — voisin, explicitement hors scope initial.
- **Efficient Deep Learning** — motivation (réduire coût/données/énergie).
- **Sample-Efficient Learning** — un des deux axes de métrique principaux (avec la vitesse).
- **AI Systems** — dimension ingénierie/infrastructure du projet.

**Contribution potentielle.** À l'intersection de la Training Dynamics (habituellement étudiée de façon descriptive/post-hoc) et du Meta-Learning appliqué au HPO (habituellement traité comme boîte noire) : un système qui relie explicitement des **propriétés structurelles pré-entraînement** à des **prédictions de dynamique**, validé par une méthodologie **causale** plutôt que purement corrélationnelle.

---

## 38. Roadmap

| Version | Contenu | Expériences | Critères de réussite | Difficulté | Risques principaux |
|---|---|---|---|---|---|
| **MVP** | Laboratoire MLP + 5 hyperparamètres + recherche Bayesienne de référence | Phase 1 partielle | Meta-dataset de ≥ 1000 essais cohérent et exploitable | Faible-Moyenne | Sous-estimation du coût de calcul |
| **V0.1** | Synthetic Learning Laboratory complet (fonctions génératrices paramétriques, contrôle bruit/complexité/redondance) | Génération de ≥ 100 tâches | Diversité de tâches suffisante (vérifiée par clustering des features de tâche) | Moyenne | Générateur trop peu diversifié |
| **V0.2** | Hyperparameter predictor (gradient boosting) | Phase 1 complète | Bat la baseline par défaut sur ≥ 60 % des tâches test | Moyenne | H1 insuffisamment vérifiée |
| **V0.3** | Initialization predictor + features de courbure (Hutchinson, power iteration) | Ablation §26 partielle | Gain mesurable attribuable spécifiquement à l'initialisation prédite | Moyenne-Élevée | Coût de calcul des features de courbure |
| **V0.4** | Extension CNN/Transformer miniature | Phase 2-3 | Transfert du meta-modèle avec dégradation « acceptable » (seuil à définir a priori) | Élevée | Espace d'architecture trop large |
| **V0.5** | Datasets réels | Phase 4 | \(N_{ours} \le N_{baseline}\), \(T_{ours} \le T_{baseline}\) à performance égale | Élevée | Mauvaise transférabilité synthétique→réel (risque central) |
| **V1.0** | API de production (§29-30) + score de confiance calibré | Validation de calibration | Confiance corrélée à la fréquence réelle de succès | Élevée | Latence, fiabilité en conditions réelles |
| **V2.0** | Meta-learning à grande échelle (GNN sur architectures, boucle de feedback continue) | Phase 5-6 | Amélioration continue mesurable au fil des feedbacks de production | Très élevée | Meta-overfitting, dérive |

---

## 39. MVP — Détail

Le MVP doit rester **volontairement petit** :

```
MLP
  ↓
Tâches synthétiques de régression (3-5 fonctions génératrices)
  ↓
5 hyperparamètres (learning_rate, batch_size, optimizer, weight_decay, initialization)
  ↓
~1000 configurations testées (recherche Bayesienne de référence, via Optuna)
  ↓
Mesure de convergence (steps_to_threshold)
  ↓
Constitution du meta-dataset
  ↓
Premier modèle prédictif (gradient boosting)
```

**Sortie attendue du MVP :** une réponse chiffrée, même négative, à la première hypothèse (H1) sur un scope restreint — pas un produit utilisable.

---

## 40. Future Extensions

- Extension à des familles d'architecture supplémentaires (RNN/SSM, GNN, modèles multimodaux).
- Prédiction de configurations de *fine-tuning* pour LLM (LoRA/PEFT — rang, learning rate d'adaptateur) comme cas d'usage à forte valeur pratique.
- Intégration d'un budget de probing adaptatif (le système décide lui-même s'il a besoin de plus de signal avant de répondre, plutôt qu'un budget fixe).
- Marketplace de « profils de convergence » — bibliothèque de configurations validées par famille de tâches, alimentée par la communauté (piste open-source, §42).

---

## 41. Potential Scientific Contributions

- Un **Synthetic Learning Laboratory** open-source, réutilisable indépendamment du succès de l'hypothèse centrale (contribution méthodologique en soi).
- Une **Experiment/Meta-Database** publique de dynamiques d'entraînement contrôlées, utile à la communauté training-dynamics au-delà de PreTrainOpt.
- Une évaluation empirique rigoureuse (causale, pas seulement corrélationnelle) de l'importance relative des facteurs pré-training sur la convergence — publiable indépendamment du succès du produit final.
- Si H1-H3 sont validées : un article démontrant qu'un meta-prédicteur bat les baselines HPO standards à budget de calcul très inférieur.

---

## 42. Potential Industrial Applications

- Réduction du coût de *tuning* pour les équipes ML sans expertise HPO poussée (démocratisation).
- Accélération du fine-tuning de LLM en production (cas d'usage à forte valeur, coût d'expérimentation élevé chez les praticiens).
- Intégration en amont des plateformes MLOps existantes (Kubeflow, SageMaker, Vertex AI) comme étape de recommandation avant lancement d'un job d'entraînement.
- Réduction de l'empreinte énergétique de l'entraînement de modèles (argument ESG concret si \(E_\epsilon\) est effectivement réduit).

---

## 43. Open-source Strategy

- Le **Synthetic Learning Laboratory** (générateur de tâches) et l'**Experiment Database** publiés en open-source dès la V0.1 — construisent la crédibilité scientifique et attirent des contributions externes (nouvelles familles de tâches, nouvelles architectures).
- Le **meta-modèle entraîné** et l'**API de prédiction** peuvent rester propriétaires (différenciation produit) même si le code du laboratoire est ouvert — modèle « open-core » classique.
- Publication d'un article (workshop puis conférence) dès que Phase 1-2 produisent un résultat solide, pour asseoir la légitimité scientifique avant la phase produit.

---

## 44. Product Strategy

- **Phase recherche (V0.x)** : pas de produit, publication et crédibilité scientifique comme objectif.
- **Phase early access (V1.0)** : API restreinte à quelques utilisateurs pilotes (équipes ML internes ou partenaires), pour valider H3 (le rapport coût/bénéfice) en conditions réelles.
- **Phase produit (V1.0+)** : SaaS d'API de recommandation de configuration, intégrable dans les pipelines d'entraînement existants ; tarification indexée sur le compute économisé (modèle « value-based pricing » cohérent avec la proposition de valeur).
- **Phase infrastructure enterprise (V2.0)** : déploiement on-premise pour les organisations dont les contraintes de confidentialité empêchent l'usage d'une API externe (pertinent notamment pour les grands modèles propriétaires).

---

## 45. Final Research Thesis

> **Une part significative de la dynamique d'apprentissage future d'un modèle est déterminée par des propriétés observables avant l'entraînement complet — architecture, statistiques de la tâche, statistiques d'initialisation — et cette relation, apprise sur un laboratoire de tâches synthétiques contrôlées, se transfère à des modèles et données réels avec un gain net (mesuré en steps, samples et compute) par rapport aux méthodes de recherche d'hyperparamètres classiques.**

Cette thèse n'est **pas** présentée comme acquise. Elle est la conclusion que le protocole expérimental (§24) est construit pour confirmer, nuancer ou réfuter — avec, dans les trois cas, une contribution scientifique et une base technique (laboratoire, experiment database) qui restent utiles.

---

## Annexe A — Identité du projet

**Noms proposés** (fonctionnant comme projet open-source, framework de recherche, produit SaaS et infrastructure enterprise) :

1. **PreTrainOpt** — descriptif, direct, facile à indexer techniquement.
2. **Vantage** — évoque le point de vue pris *avant* de s'engager dans l'entraînement.
3. **Primer** — au sens « amorcer » un entraînement avec une bonne configuration de départ.
4. **Convergo** — évoque directement la convergence, sonorité internationale.
5. **Nascent** — l'état du modèle avant training, connotation scientifique.
6. **Priora** — de « a priori », connotation prédictive/bayésienne.

**Recommandation :** **PreTrainOpt** pour le nom technique/dépôt (clarté immédiate pour un public ML), avec **Vantage** ou **Priora** en réserve pour un futur nom de produit commercial plus mémorable.

**Tagline :** *« Know your training before you run it. »*

**Mission :** Réduire le coût en données, en calcul et en temps de l'entraînement des réseaux de neurones en remplaçant la recherche d'hyperparamètres par une prédiction fondée sur les propriétés du modèle et de la tâche.

**Vision :** Un futur où lancer un entraînement commence par une recommandation fiable et expliquée, pas par un essai à l'aveugle.

**Problème :** Le tuning d'hyperparamètres consomme une part significative — et largement évitable — du budget de calcul et du temps d'ingénierie en machine learning.

**Solution :** Un système de meta-apprentissage, entraîné sur un laboratoire de tâches synthétiques contrôlées, qui prédit une configuration d'entraînement quasi-optimale avant, ou avec un minimum de, calcul réel.

**Proposition de valeur :** Moins de données, moins de compute, moins de temps d'ingénieur — pour une performance égale ou meilleure, avec un score de confiance explicite plutôt qu'une promesse aveugle.

---

## Annexe B — Recommandation finale

### Architecture recommandée pour le premier prototype

- **Scope** : MLP uniquement, tâches de régression synthétique (3-5 fonctions génératrices de complexité croissante).
- **Hyperparamètres couverts** : learning rate, batch size, optimizer (Adam/AdamW/SGD), weight decay, méthode d'initialisation (Xavier/He/orthogonale) — volontairement limité à 5 pour rester interprétable.
- **Génération de vérité terrain** : Optuna (TPE) comme recherche Bayesienne de référence, pas Vizier directement (plus simple à intégrer en Rust/Python pour un prototype).
- **Meta-modèle** : gradient boosting (LightGBM), features tabulaires uniquement en V1 (pas de NTK/Hessienne au MVP — trop coûteux pour la première itération, à introduire en V0.3 une fois H1 partiellement validée).
- **Infrastructure** : exécution locale/mono-machine au MVP, pas de Kubernetes avant que le volume d'expériences ne le justifie réellement.

### Expériences prioritaires (dans l'ordre)

1. **Expérience de calibration** — pour une tâche synthétique fixée, balayer le learning rate seul (toutes choses égales par ailleurs, 5 graines) et vérifier qu'on retrouve une courbe en U conforme à la théorie (§9). *Objectif : valider l'instrumentation avant toute chose.*
2. **Expérience factorielle LR × Batch size** — sur 3-4 tâches synthétiques de complexité croissante, pour tester l'interaction connue LR↔batch (règle linéaire empirique) et calibrer la méthodologie factorielle (§15) sur un cas où la réponse attendue est déjà connue.
3. **Premier test de H1** — entraîner le meta-modèle sur 80 % des tâches synthétiques générées, évaluer sur les 20 % restantes (tâches jamais vues) : le meta-modèle bat-il la configuration par défaut ? C'est l'expérience qui décide si le projet continue tel quel ou pivote.

### Trois premières hypothèses à tester

1. **H1** — les features pré-training (modèle + tâche) portent un signal exploitable sur \(H^*\) — testée par l'expérience #3 ci-dessus.
2. **H4** — il n'existe pas de configuration universelle — testée en mesurant la variance de \(H^*\) trouvé par Optuna à travers les tâches synthétiques (si la variance est faible, H4 est infirmée et le problème est plus simple que prévu ; si elle est forte, cela confirme le besoin d'un prédicteur conditionnel).
3. **H5** — les rendements décroissants du probing — testée en comparant, sur le meilleur modèle issu du MVP, la précision de prédiction à 0 %, 0.1 % et 1 % de budget de probing.

**Ne pas commencer à coder l'API de production, le dashboard ou l'architecture distribuée avant que H1 (expérience #3) ne soit tranchée.** Tout le reste du document (§18 à §44) est la trajectoire *si* le signal existe — pas une liste de tâches à exécuter en parallèle dès le premier jour.