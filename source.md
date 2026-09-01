Oui. Après recherche, il existe une famille entière de travaux scientifiques qui partagent la philosophie de PRECOG : réduire le coût de l'entraînement, prédire les performances avant ou avec très peu d'entraînement, optimiser automatiquement les hyperparamètres, améliorer l'initialisation et comprendre la dynamique de convergence.

Il est important de préciser qu'aucun document ne décrit exactement PRECOG. PRECOG se situe à l'intersection de plusieurs domaines de recherche. Les documents ci-dessous constituent donc le corpus scientifique de référence à étudier.

# Les 8 piliers scientifiques de PRECOG

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(255%2C%20255%2C%20255\)%22%20viewBox%3D%220%200%20320%20420%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20width%3D%22320%22%20height%3D%22420%22%20rx%3D%2218%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.15%22%20stroke-width%3D%221.5%22%2F%3E%3Crect%20x%3D%2278%22%20y%3D%2218%22%20width%3D%22164%22%20height%3D%2236%22%20rx%3D%2210%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.08%22%20stroke%3D%22currentColor%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2231%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPRECOG%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2243%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EPredictive%20Training%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2251%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EOptimization%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%2254%22%20x2%3D%22160%22%20y2%3D%2268%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2218%22%20y%3D%2268%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%2284%22%20y%3D%2282%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EHyperparameter%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%2293%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EOptimization%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22106%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EVizier%20%E2%80%A2%20BOHB%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%2268%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22236%22%20y%3D%2282%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EMeta-Learning%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%2293%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ELearned%20Optimizers%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22106%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EPrior%20knowledge%3C%2Ftext%3E%3Cline%20x1%3D%2284%22%20y1%3D%22120%22%20x2%3D%22160%22%20y2%3D%22145%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Cline%20x1%3D%22236%22%20y1%3D%22120%22%20x2%3D%22160%22%20y2%3D%22145%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2294%22%20y%3D%22145%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22159%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ETraining-Free%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22170%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPrediction%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22183%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EZero-cost%20proxies%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22197%22%20x2%3D%22160%22%20y2%3D%22212%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2218%22%20y%3D%22212%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%2284%22%20y%3D%22226%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EInitialization%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22237%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EDynamical%20Isometry%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22250%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EGradient%20flow%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%22212%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22236%22%20y%3D%22226%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ETraining%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22237%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EDynamics%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22250%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3ELoss%20%E2%80%A2%20Hessian%3C%2Ftext%3E%3Cline%20x1%3D%2284%22%20y1%3D%22264%22%20x2%3D%22160%22%20y2%3D%22289%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Cline%20x1%3D%22236%22%20y1%3D%22264%22%20x2%3D%22160%22%20y2%3D%22289%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2294%22%20y%3D%22289%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22303%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ESample%20Efficiency%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22314%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EActive%20Learning%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22325%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EData%20Selection%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22341%22%20x2%3D%22160%22%20y2%3D%22356%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2254%22%20y%3D%22356%22%20width%3D%22212%22%20height%3D%2246%22%20rx%3D%2212%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.06%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22371%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EObjectif%20final%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22384%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Epr%C3%A9dire%20la%20meilleure%20configuration%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22394%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eavant%20le%20training%20complet%3C%2Ftext%3E%3C%2Fsvg%3E)

# 1. Hyperparameter Optimization

C'est le domaine le plus proche de Google Vizier.

![Google Vizier — Taylor Vennel | Senior Creative + Brand Designer](https://images.openai.com/static-rsc-4/UUHJvD6x5yDZEPiOPHXaviA6PhBIFEXYZI1e2c5FV4LlN3aq5Y_2D26d4Tum46_9cxccRCdzDpwKV9woPEZTgRc1-hZ7oa2Bk9IXhYrY8_DsmjfpsO3lJsz_PXyxaY-8enZ7yuuAqLRBd-W8k--Btwh3fo5w_zmyXFjTATrsdRU?purpose=inline)

### Google Vizier

Fondamental

Document : Google Vizier: A Service for Black-Box Optimization

Ce papier décrit le moteur de Google pour optimiser automatiquement des hyperparamètres et des fonctions objectives complexes par black-box optimization. C'est la baseline industrielle la plus importante pour PRECOG.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

Google Research

Google Vizier: A Service for Black-Box Optimization

![recent advances in bayesian optimization .pdf](https://images.openai.com/static-rsc-4/v9_ZK_Tmz0Eeww07AHu4DEYvFoyr2K_OQHbfBVdYpEEPldTBVRd6OEzTnzDH4lmzFI08bCZkgo2Qx1JKLN1dmijDW3WD_D56AdYUUb_jWiR6EUAcmoDnc7YHVTjnjZG9qqEOCdDjTSHU4sEdYD5fdWYqAvJqxFhdSaABgIB0rLc?purpose=inline)

### Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

Document de référence : grande revue scientifique sur Grid Search, Random Search, Bayesian Optimization, Hyperband et les défis ouverts.

Ce document doit servir de base théorique pour construire le module `optimization/` de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv survey

Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

![AutoML | BOHB: Robust and Efficient Hyperparameter Optimization at Scale](https://images.openai.com/static-rsc-4/Yi6zfM3BSjKJTx6Ni-lprD23_Z29HCRyVl0cMG36pqpX5HkwxerbkglNW8JbzZ-kT5sQ-3plCl8dgMrPkoGqigIUxZImCqcsbiWK8fujst1AeKVcvON7wtpev6an7k-QyMzw4AHBMioQla8Y1QnVl5rNz1zjhbbLdMeLVStLAn8?purpose=inline)

### Hyperparameter Optimization in Machine Learning

Revue récente expliquant les méthodes modernes de recherche d'hyperparamètres, y compris BOHB qui combine Bayesian Optimization et Hyperband pour améliorer l'efficacité des essais.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arxiv.org

Hyperparameter Optimization in Machine Learning

# 2. Meta-Learning : apprendre des expériences précédentes

La philosophie de PRECOG repose fortement sur cette idée :

> Les expériences passées doivent devenir une connaissance réutilisable.

![Bo Zhao (@BoZhao\_\_) on X](https://images.openai.com/static-rsc-4/zX-qzqtX3ibRUxuIVrdIVlwufzVuzLP1XBfvKlvJ-lxvu9FtmwoGeK_4dsCx9As9zFwKI8JVKi2WAODk7qPf0VvwK_-egMdENq8j8HaPgoLMeCSYL31WdwZMLI5Y06KQ09qmX3Z0epg--aqHziGW8intNAROHxiMDrKev6G3xeU?purpose=inline)

### Initializing Bayesian Hyperparameter Optimization via Meta-Learning

Ce papier montre qu'on peut utiliser des tâches précédentes pour démarrer l'optimisation dans des régions prometteuses plutôt que repartir de zéro.

C'est exactement la logique du futur Meta-Dataset de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

ojs.aaai.org+1

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

AAAI

Initializing Bayesian Hyperparameter Optimization via Meta-Learning

![Gradient-Based Optimizers in Deep Learning - Analytics Vidhya](https://images.openai.com/static-rsc-4/byb7HwBacdWxO4eBx6fgFsKfgcejpNhqFnUdwErZewNonI_GZz1YaH9PlgCW3ODvvLdamo65LJKvYOZEQPzzRnSXWKj3IZsHLKb6VX1am39DWoR4h9akf2dywqJhRJF2LSmi1WLT6RWsa_V3BtCqJwfwp-rPT77E_2gCBqtuHK8?purpose=inline)

### Learned Optimizers that Scale and Generalize

Les auteurs proposent un optimiseur lui-même appris par un réseau de neurones afin de généraliser sur de nouvelles tâches.

Cette branche est essentielle si PRECOG évolue vers un optimiseur appris plutôt qu'un simple prédicteur d'hyperparamètres.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

PMLR ICML

Learned Optimizers that Scale and Generalize

![Axon and Myelin Sheath Segmentation in Electron Microscopy Images using Meta Learning - PMC](https://images.openai.com/static-rsc-4/I_R2m9RZhkGUwfMCPebKMJGNnn9PuQ6dJL-3V8oxYFGuEFFGjH40O6R5Ebp6X1ohV8cS4K9JH0vKJvnJegeOEBoHMTothaJ9iSug5WU7h6_mkFM13_22qVI-w8taJubkUd1oGlYUXVhyyPuVt0lSHerf04ImWRJZ7j9LmQUI8GY?purpose=inline)

### Meta-Learning Bidirectional Update Rules

Étudie des règles de mise à jour apprises au lieu des règles classiques de descente de gradient.

Très pertinent pour imaginer une future version de PRECOG où les updates elles-mêmes deviennent prédictives.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

PMLR

Meta-Learning Bidirectional Update Rules

# 3. Training-Free Prediction

C'est probablement la branche la plus proche de ton idée originale.

L'objectif est de prédire les performances d'un réseau sans effectuer son entraînement complet.

![Abacus.AI at NeurIPS 2022 - The Abacus.AI Blog](https://images.openai.com/static-rsc-4/wumTrDmx04iDV7QBgfPiHRYQVEH8nYZTTrtpTH2ER9CHMFOYjXg5ZlcAreaBFw3qezleOP1s1AZpvYwik6dQrbJMrQf6_LQqW4UAttripNOcf_wXK1fR9_1dSnzaonCMeD1a4N2fN8SVpQDEY68mguE4zW3IVhX-gqa20fu3PTY?purpose=inline)

### Zero-Cost Proxies for Lightweight NAS

Très important

Ce papier introduit les zero-cost proxies, capables d'évaluer des architectures avec seulement une initialisation et un mini-batch, sans entraînement complet.

C'est une inspiration directe pour PRECOG-0.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Zero-Cost Proxies for Lightweight NAS

![Publications | Abdelfattah Research Group at Cornell University](https://images.openai.com/static-rsc-4/nwmHfGB3lV2nu7d4PrZVORFIfhPfeujoGqq8rDO-ImAkzlfhhrQq1rQ7kRApNUtkoxEIfj-jE9xngux9heOkyLQx8lLGcmME1gzhX3hd4Iy0qcmtsPJBqf8kCUuLp82Licv8dlUs2mADaCEs8weFA1bf7SYUC51mnd1TzyitSoU?purpose=inline)

### Zero-Shot Neural Architecture Search

Revue complète des méthodes permettant de prédire la qualité d'une architecture sans entraîner ses paramètres.

Elle donne une cartographie scientifique des proxies zéro entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Zero-Shot Neural Architecture Search

![ICLR Poster NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance](https://images.openai.com/static-rsc-4/p_9YQf0h71LyXsBFjum4detP2QGEeNRhUVW8D5AvO7i6mjFHrtaLUApXDMs6ZYY5qdrer7XxaYeey3FlB2QmbN7ViS6vk6F4se0yTKu_zpgFNMkatuUVCqZvkq72JlCOKWBKVyHDXo14S11kZexqGbPJBbK0sGmyWmmQRbnIqYw?purpose=inline)

### NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

L'un des papiers les plus intéressants pour PRECOG.

Il propose un score basé sur le rang effectif des activations afin d'estimer la performance future d'un réseau et montre également une utilisation pour sélectionner certaines initialisations et fonctions d'activation.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

![Iclr 2024 openreview](https://images.openai.com/static-rsc-4/QsVJC_RfmdR3spk-oksHDpYySZs8IZUhni3W4IBg3x7EgCFNEzs187C2ql1GlXka-V6toQVVnwCogSKxuMvScw0vXZyW7a9iTQKS4zUqlYW48xVYRAfELM9VSL4Rz4vBMEwVKriZXjuZXJNxmGeCCtjzmTPLjpXuhl0iLypuUwQ?purpose=inline)

### ProxyBO

Combine les zero-cost proxies avec Bayesian Optimization afin d'accélérer la recherche de bonnes architectures.

Très proche de l'idée d'utiliser des signaux analytiques avant d'investir dans un entraînement coûteux.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

ProxyBO

![NeurIPS Poster Per-Architecture Training-Free Metric Optimization for Neural Architecture Search](https://images.openai.com/static-rsc-4/55P3YmqsRsYyn0xPSAJt121PhdZgNBoJ1__IMpqVh_p68j2T5PBF9JPCQ9iPUfBduBflxk6UBe-kh210uPGWHjJNz7XsJMSh6G3ZH98XdFiVW4KE5kioMJNpWfk6LaWIg9inFSm5UCodCAI8iV-HFCRNclggHX4N32namyX1xW4?purpose=inline)

### TG-NAS

Utilise un Transformer et un GCN comme proxy universel pour prédire les performances d'architectures sans réentraîner le prédicteur sur chaque espace de recherche.

Très intéressant pour la partie Model Analyzer de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

TG-NAS

# 4. Initialisation et Dynamical Isometry

Cette branche cherche à répondre à une autre question fondamentale :

> Pourquoi certaines initialisations permettent-elles une convergence beaucoup plus rapide ?

![7 Ways to Initialize Deep Learning Models | by Maryum Arif | Medium](https://images.openai.com/static-rsc-4/Iu46Imjq_1PpXzXpQ-qxatYH_QkTVTecoHuq9tjqGevVy4nnAO82IfcfrA_CR_OVtjaSWZTFLQC3DzHI-7GulU_3L3_1g8X6bLDaG89XAaxViIG2veaa6WLmjtyDT2t3g56YTGQCkuXbAhqKs90MLmCFDGtSPe1QYmjIrIkMykM?purpose=inline)

### Provable Benefit of Orthogonal Initialization in Optimizing Deep Linear Networks

Fondamental

Ce papier démontre mathématiquement que l'initialisation orthogonale peut accélérer la convergence dans les réseaux linéaires profonds par rapport à certaines initialisations gaussiennes.

C'est une référence incontournable pour le module `initialization/`.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Provable Benefit of Orthogonal Initialization in Optimizing Deep Linear Networks

![Understanding implicit regularization in deep learning by analyzing trajectories of gradient descent – Off the convex path](https://images.openai.com/static-rsc-4/8CYLgkNDu3WlUgqqvKiJLGYMc7g-SG9h_cSjwnMfrm7_Jqehpgqu-yCXJ1nW-V1_7j5lsDh4eVewMdD2aSsgz_2lJ5RMjq8W3PDoi2tWa7JFDSFILAqQ3bzZYYCE6Uggqx5YRZgkj47Shm_IefcxOnJIeKzoC-8eGgvW_L-66L4?purpose=inline)

### Resurrecting the Sigmoid in Deep Learning Through Dynamical Isometry

Étudie la propagation du signal et montre que certaines conditions d'initialisation permettent une meilleure circulation des gradients et un apprentissage beaucoup plus rapide dans certains régimes.

C'est la base théorique du concept de dynamical isometry.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Resurrecting the Sigmoid in Deep Learning Through Dynamical Isometry

![Weight Initialization: Xavier, He & Variance Preservation - Interactive | Michael Brenndoerfer | Michael Brenndoerfer](https://images.openai.com/static-rsc-4/2rhl-ygGtMNCkBwbK_YToj8pGOeGnARObFC5i-KAKD3tfi_kS4K78KSvBn3XqT4mJiXU_Q3xsEshks3d1q039vb8oWlc_UMOGnfyG-Rrf595vzFKXl2ij1Uy86Hn4XXpA3ZFi779ZUtjIJekL-YMeKi6IraeGUp3JIgFi5fbW9s?purpose=inline)

### On the Neural Tangent Kernel of Deep Networks with Orthogonal Initialization

Analyse le lien entre orthogonalité, NTK et vitesse d'apprentissage.

Très utile si PRECOG veut exploiter des propriétés géométriques avant entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

On the Neural Tangent Kernel of Deep Networks with Orthogonal Initialization

![Structure, Disorder, and Dynamics in Task-Trained Recurrent Neural Circuits - Kempner Institute](https://images.openai.com/static-rsc-4/eetZqQ2zfNRTFdttH4jx8ZVFqhI6dPq5HHjK0IRwG3gEVg2ruY0oTwORwPJ28q9nzeFiTjtT1QjyuuOHv6yQhnVTWqoLBYUK_9NdtSxiB0agbVoDoJ2UX3NiNjrGTwc7fEPUinnxAuuk4gd7RPizYq9I0lla5Jaef-2t7nVlXJo?purpose=inline)

### Dynamical Isometry and a Mean Field Theory of RNNs

Développe une théorie de la propagation du signal à l'initialisation à l'aide de la théorie des matrices aléatoires et du mean-field.

Important pour comprendre comment analyser un réseau vierge.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Dynamical Isometry and a Mean Field Theory of RNNs

# 5. Training Dynamics et géométrie de l'apprentissage

PRECOG veut mesurer ce qui se passe pendant les premières étapes de l'apprentissage afin de prédire la suite.

Les domaines associés sont :

* Gradient Flow

* Loss Landscape

* Hessian Spectrum

* Jacobian Analysis

* Sharpness

* Curvature

* Gradient Noise

* Gradient Alignment

![Cross Entropy Loss: Intro, Applications, Code](https://images.openai.com/static-rsc-4/1VvWQpI0BTA1xF49WaPzmlL5cK53zTegmiVl5Cw4DNlq_43zQvwzop7JZnnf7ACtSxj6lhPiVI6MaMMIxPyBQWRB7CqrQ7xmaOTuby47zrdtlHqdpVesGHc-za83_9uejDh5zOIh5_zADCOwLuNskYJWWL-WgzVnduitlbfG5qY?purpose=inline)

### Deep Network Trainability via Persistent Subspace Orthogonality

Travail récent approfondissant la notion de dynamical isometry et la relation entre orthogonalité persistante et facilité d'entraînement.

Il montre que la géométrie interne du réseau reste un sujet actif de recherche.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arxiv.org

Deep Network Trainability via Persistent Subspace Orthogonality

# 6. Sample Efficiency et moins de données

Ton objectif n'est pas seulement de réduire les epochs.

Tu veux aussi réduire :

NϵN_{\epsilon}Nϵ

c'est-à-dire le nombre de données nécessaires pour atteindre une performance cible.

![Jidong ZHAO | Professor | Ph.D. | Hong Kong University of Science and Technology, Hong Kong | UST | Department of Civil and Environmental Engineering | Research profile](https://images.openai.com/static-rsc-4/BcDQCf-KRh3AVxtPi3bz87l71OY7M961zuDMOXGVu8kKjoLSqobdYtLaIb5ABZuOuwp49z0S8NxDw1POkqNcGMZNNVrFZUqM-kwPWQ9O710hMbdteuO_yP0OBSUVDcyussnHRlS6ITdK9ngat1fWbPw-M0FDmjEEuaatZJ3EodA?purpose=inline)

### A Survey of Deep Active Learning

Référence

L'active learning cherche explicitement à maximiser le gain de performance en annotant le moins d'exemples possible.

C'est une littérature essentielle pour la partie sample efficiency de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

A Survey of Deep Active Learning

![When deep learning meets active learning in the era of foundation models | EurekAlert!](https://images.openai.com/static-rsc-4/WxXAzSwL9L9qhTcvUA94_DPJ5PQHayxC8DsYvhERk4FIVL1658DUw4vdzhG_-pBYBskMfPoTEmO8mL5zu0qoUyDPsK67cdGl4G2iEVIIj5_pMLYsnb_rGcKI2ub397Ee8-wBCcRwqtNg2EMWZy9YPQNIkEj29iSjCSd3NIlSW3I?purpose=inline)

### A Comparative Survey of Deep Active Learning

Compare de nombreuses méthodes d'active learning dans un cadre expérimental homogène.

Très utile pour construire les futurs benchmarks de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

A Comparative Survey of Deep Active Learning

# 7. Neural Architecture Search sans entraînement

Même si PRECOG ne cherche pas d'abord la meilleure architecture, cette littérature apporte les méthodes permettant de prédire la qualité d'un réseau vierge.

Documents importants :

![An Efficient Evolutionary Neural Architecture Search Algorithm Without Training](https://images.openai.com/static-rsc-4/a6TOVzWn1LC0RXjlxYPztmNlRC3DHgatBG1s2X37I-ABz5lv3ONin3eFtJCDATLASbsVYJGCeetXS_eco3uOGVOeOKx6GS5r7X_1QZZPEW5ypIfGoEfrD1SkCnVpVivP66ZtnaHOXlKOZxCNqY6p2b1vd_8_SV_K1jC3a9ijqlY?purpose=inline)

### NASWOT et les Zero-Cost Proxies

Cette famille de travaux introduit des scores calculés à l'initialisation permettant de classer des architectures sans les entraîner complètement. Elle constitue une inspiration méthodologique directe pour PRECOG.

![](https://www.google.com/s2/favicons?domain=https://iclr-blog-track.github.io\&sz=32)

iclr-blog-track.github.io+1

![](https://www.google.com/s2/favicons?domain=https://iclr-blog-track.github.io\&sz=32)

ICLR Blog Track

A Deeper Look at Zero-Cost Proxies

![A Generic Graph-based Neural Architecture Encoding Scheme for Predictor-based NAS | Hyunju Kim](https://images.openai.com/static-rsc-4/49X_Hr8TfAlh98NTZXbWt1Xqto_bdD0RTKSdT3AidRSyIIZzpfdy_1FUoRDN73ejfwD8Tm8f51BsLlsvSjHmvHqSVhOr6mvARtfDvJwGMk2gcaY5sfzoqH9uEhQbI6emvYp79Q1xjXEFT0CRPj_u_HM3rFlnh0xXFw4ZojJsXQg?purpose=inline)

### Generic Neural Architecture Search via Regression

Explore la prédiction de performances d'architectures par régression et l'utilisation de représentations des réseaux plutôt que des entraînements complets.

![](https://www.google.com/s2/favicons?domain=https://openreview.net\&sz=32)

openreview.net

![](https://www.google.com/s2/favicons?domain=https://openreview.net\&sz=32)

OpenReview

Generic Neural Architecture Search via Regression

![2023年 18篇神经架构搜索(Neural Architecture Search) ICCV ICML NIPS IJCAI 阅读笔记\_prenas: preferred one-shot learning towards effici-CSDN博客](https://images.openai.com/static-rsc-4/_SlqvfyDfQNFBU-KzjqdtjTH60brrapixodI8uvjZqnyZNwq8xH-FbY2Utwq9-wR51m4P5pb0r0tvXJqAR2QMuacqvu-_nw7R6ig9uRyO4EJGekZueVJMYurMVJI7CTwLmWthT7zXkLhjr1H22lCPLr4mRANpyaKHztuCTq8VOs?purpose=inline)

### RBFleX-NAS

Recherche récente sur les approches training-free pour sélectionner des architectures avec un coût minimal. Intéressant pour suivre l'évolution du domaine.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

RBFleX-NAS

# 8. Outils open-source à étudier

Ces projets ne partagent pas toute la philosophie de PRECOG, mais ils constituent l'infrastructure de référence.

![Google Vizier — Taylor Vennel | Senior Creative + Brand Designer](https://images.openai.com/static-rsc-4/UUHJvD6x5yDZEPiOPHXaviA6PhBIFEXYZI1e2c5FV4LlN3aq5Y_2D26d4Tum46_9cxccRCdzDpwKV9woPEZTgRc1-hZ7oa2Bk9IXhYrY8_DsmjfpsO3lJsz_PXyxaY-8enZ7yuuAqLRBd-W8k--Btwh3fo5w_zmyXFjTATrsdRU?purpose=inline)

### Google Vizier

Framework open-source de black-box optimization inspiré du système utilisé chez Google.

À étudier pour : moteur de recherche d'hyperparamètres et API d'expérimentation.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

Google Vizier

![Optuna: A Practical Guide to Hyperparameter Optimization](https://images.openai.com/static-rsc-4/eNbSmAa6A05hq_wfqkcHigMl_nEUjzvo4zXY2-x5SUrUZLTQKumXy-tLixK7Zx47WOJJFcA589YeG2zxsu7vl2mUNkGAlprc42q3YhjIo5g53rvAie3n9bOzs3tbyls8bFnw4otNesI697DveQRrTf_C3jd3sW2a2cNM6srFxMw?purpose=inline)

### Optuna

Framework très utilisé pour les études expérimentales reproductibles et les algorithmes modernes de tuning.

À utiliser comme baseline expérimentale.

![](https://www.google.com/s2/favicons?domain=https://optuna.org\&sz=32)

Official website

Optuna

![Ray Tune: a Python library for fast hyperparameter tuning at any scale | by Richard Liaw | TDS Archive | Medium](https://images.openai.com/static-rsc-4/DF5Uo7DnpiayYJbvDNZawe3_NDYseDQW5jK56Culr6nhk7_FgWnYYXeAsO123NomOaP6xR0zxGleEYa914BvnWUj5apMKmgAohShONZWinAl1YHNYgK0WrrZxtU-dEdcFWi6ldTIKJnie5EEUzHsLI8a5Ou2wZmfiZ7DLG8M5s8?purpose=inline)

### Ray Tune

Bibliothèque distribuée pour exécuter des milliers d'expériences parallèles sur plusieurs GPU ou clusters.

Très pertinent pour PRECOG Cloud.

![](https://www.google.com/s2/favicons?domain=https://docs.ray.io\&sz=32)

Official documentation

Ray Tune Documentation

![Kubernetes & AI - Beauty and the Beast !?! @KCD Istanbul 2024 | PDF](https://images.openai.com/static-rsc-4/MVLEXCgb9Kc5BexE1_aeXej7DEQhb9zGyE7_0T0IjdVuDQZJiYqVA5bg_xlw-DFtlFE6GhccGKNBpt7LNh6pafxWP77fkK1ZDalYjxqu6fbc-kxgpYCXOyErBpdy_yL3Ya8DwoF1y2EOIyXO2tPg5B7bV-6ygj9G5gIwUtiQowY?purpose=inline)

### Katib

Système de tuning intégré à Kubernetes pour les pipelines MLOps.

À étudier pour l'industrialisation enterprise.

![](https://www.google.com/s2/favicons?domain=https://www.kubeflow.org\&sz=32)

Official documentation

Kubeflow Katib

### Awesome AutoML

Une collection open-source regroupant les principaux frameworks AutoML, HPO, NAS et outils de benchmark.

Très utile comme index de recherche bibliographique.

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

Awesome AutoML

# Les documents les plus proches de PRECOG

Si ton objectif est de construire PRECOG, voici les 10 lectures prioritaires dans l'ordre.

1. Google Vizier: A Service for Black-Box Optimization

Base industrielle de l'optimisation des hyperparamètres.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![CVPR Poster Efficient Hyperparameter Optimization with Adaptive Fidelity Identification](https://images.openai.com/static-rsc-4/xMiPkqep8BGuyGpPQTFVcAWypIQMG6_XXPe5lImGfZLvGKQnr5DbBViUWanJym0vHdUDQZh8qQWSNCPKKwrppQV6ex0AkHSrmxjdWllYvA2F9zrMZpn8iFXWDm8ug4xalvVk5LOM_cKtKMZ4OyM3MH4XhTqx3WsfFcvk-GBcXsk?purpose=inline)

2. Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

Référence théorique complète sur le HPO.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS Poster NAS-Bench-Suite-Zero: Accelerating Research on Zero Cost Proxies](https://images.openai.com/static-rsc-4/pDUDX4-l9Iqw7RTnP6GphfwBataSqHaIHpFOPjoOoEQlQdJsNvwMuP1oWSsQUMiNuAu93JBAXh7s5PRT4wOjnsGZvRmosUMwYJQn6fVz1EqNOYi21vE9GDIcXIOluDJQ1GaPrWif2mo5OQ0htguIcF8q0UpjChSutFNPzPUXO_4?purpose=inline)

3. Zero-Cost Proxies for Lightweight NAS

Première grande démonstration qu'un réseau peut être évalué sans entraînement complet.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![ICLR Poster NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance](https://images.openai.com/static-rsc-4/p_9YQf0h71LyXsBFjum4detP2QGEeNRhUVW8D5AvO7i6mjFHrtaLUApXDMs6ZYY5qdrer7XxaYeey3FlB2QmbN7ViS6vk6F4se0yTKu_zpgFNMkatuUVCqZvkq72JlCOKWBKVyHDXo14S11kZexqGbPJBbK0sGmyWmmQRbnIqYw?purpose=inline)

4. NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

Le papier le plus proche de l'idée de prédiction avant entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS 2022 Towards Learning Universal Hyperparameter Optimizers With Transformers Paper Conference | PDF](https://images.openai.com/static-rsc-4/vXk6d4jWGqX6iTHN39VPjf_WKIcdh6qQGY9XC0r3k1ptcCVWB6KAzg9hP-PM5j0sNRxJZKxWfZfX1wa7OAbo-jeRNAUlD1Lyaisf9l2RPp0sqOmE8ACnlIzPELJS7HiTwbP4mPggPazRJMVCtvYgShii3jQRedSZj-j8tcTem_Y?purpose=inline)

5. Initializing Bayesian Hyperparameter Optimization via Meta-Learning

Fondation du meta-dataset et du transfert d'expérience.

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

ojs.aaai.org

6. Learned Optimizers that Scale and Generalize

Vers des optimiseurs appris plutôt que manuellement conçus.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![(PDF) Dynamical Isometry and a Mean Field Theory of CNNs: How to Train 10,000-Layer Vanilla Convolutional Neural Networks](https://images.openai.com/static-rsc-4/HsbMPZKPq19Rnl9yt6u2s9eeMeA8T0Bd54MqRYTgiIIqiGVr3hCEVZtwnbN4L_Ym6ezr6BBxDdbES_K-kVSWR-jaEjzzfyhzTW07wieHxDTaZNXoVxAs5Gv4Lf2bVTI6sJcAc3yfb04UcE4Wl4LJmeLQc6rGggJItWjmfAO0h0w?purpose=inline)

7. Provable Benefit of Orthogonal Initialization

Justification mathématique de l'importance de l'initialisation.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

8. Resurrecting the Sigmoid Through Dynamical Isometry

Comprendre pourquoi certains réseaux propagent mieux les gradients.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![(PDF) A Survey on Deep Active Learning: Recent Advances and New Frontiers](https://images.openai.com/static-rsc-4/7z7eD-I8KhLQvEjp-bmibfpnNj8rfJjdidU94dRuTPte_lVvdp-XesvZV_boCFwhh4hsBCrMZ6X7Mfyei6XXcLBJVEfGJzCXsJ7VVHUEnMjcdu8BgAj-nPHftvBKMX51DfpjruE9WLuhu5lWOPP8Wv0ahvS3SAemxwkVQ6IKSAA?purpose=inline)

9. A Survey of Deep Active Learning

Référence sur l'apprentissage avec moins de données.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS Poster Per-Architecture Training-Free Metric Optimization for Neural Architecture Search](https://images.openai.com/static-rsc-4/VQFHmlESyOkC9tLLMbhJx18DRA1HOkHhePRex-BPvrKoDsFk05xwlEps7c8DNYsLBTyjjlavNFBvfqOLsEhJ9Dvn2gzVft15AXZa_2GYkVQLPpzpnT24u8Xpo-hOwGyfApgxUAfQT67mvC8SB-l_a0FTUHk5FRZa6jEJ4Xi5DE4?purpose=inline)

10. Zero-Shot Neural Architecture Search

Cartographie complète des méthodes training-free.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

# La philosophie commune

Tous ces travaux peuvent être résumés par une même idée :

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(255%2C%20255%2C%20255\)%22%20viewBox%3D%220%200%20320%20360%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20width%3D%22320%22%20height%3D%22360%22%20rx%3D%2218%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.15%22%20stroke-width%3D%221.5%22%2F%3E%3Crect%20x%3D%2234%22%20y%3D%2218%22%20width%3D%22252%22%20height%3D%2234%22%20rx%3D%229%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.08%22%20stroke%3D%22currentColor%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2231%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPhilosophie%20PRECOG%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2243%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eanalyser%20avant%20de%20d%C3%A9penser%20le%20compute%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%2252%22%20x2%3D%22160%22%20y2%3D%2266%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%2266%22%20width%3D%22248%22%20height%3D%2238%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2280%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EMod%C3%A8le%20vierge%20%2B%20t%C3%A2che%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2292%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Earchitecture%20%E2%80%A2%20donn%C3%A9es%20%E2%80%A2%20statistiques%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22104%22%20x2%3D%22160%22%20y2%3D%22118%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22118%22%20width%3D%22248%22%20height%3D%2246%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22132%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EAnalyse%20pr%C3%A9dictive%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22144%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Egradients%20initiaux%20%E2%80%A2%20spectre%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22154%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eproxy%20%E2%80%A2%20m%C3%A9ta-connaissance%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22164%22%20x2%3D%22160%22%20y2%3D%22178%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22178%22%20width%3D%22248%22%20height%3D%2246%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22192%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EConfiguration%20recommand%C3%A9e%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22204%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3ELR%20%E2%80%A2%20optimizer%20%E2%80%A2%20batch%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22214%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Einitialization%20%E2%80%A2%20scheduler%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22224%22%20x2%3D%22160%22%20y2%3D%22238%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22238%22%20width%3D%22248%22%20height%3D%2240%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22252%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EEntra%C3%AEnement%20minimal%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22264%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Evalidation%20rapide%20de%20l'hypoth%C3%A8se%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22278%22%20x2%3D%22160%22%20y2%3D%22292%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22292%22%20width%3D%22248%22%20height%3D%2244%22%20rx%3D%228%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.06%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22306%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EObjectif%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22318%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Emoins%20de%20donn%C3%A9es%20%E2%80%A2%20moins%20de%20steps%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22328%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Emoins%20de%20compute%20%E2%80%A2%20m%C3%AAme%20performance%3C%2Ftext%3E%3C%2Fsvg%3E)

La différence essentielle est la suivante :

|
Domaine

|

Question posée

|
| --- | --- |
|

Google Vizier

|

Quels hyperparamètres donnent le meilleur résultat après des essais ?

|
|

Optuna / Ray Tune

|

Comment rechercher efficacement les meilleures configurations ?

|
|

Zero-Cost NAS

|

Peut-on évaluer un réseau sans l'entraîner ?

|
|

Dynamical Isometry

|

Quelle initialisation favorise la propagation des gradients ?

|
|

Learned Optimizers

|

Peut-on apprendre une meilleure règle d'optimisation ?

|
|

Active Learning

|

Comment atteindre une performance avec moins de données ?

|
|

PRECOG

|

Peut-on prédire avant le training les meilleures conditions de convergence en combinant toutes ces connaissances ?

|

C'est précisément là que se situe l'originalité potentielle de ton projet : PRECOG n'invente pas un nouveau domaine, il cherche à unifier plusieurs branches de recherche aujourd'hui séparées dans un même système de prédiction de la dynamique d'entraînement.

## Les 6 domaines de recherche que tu dois maîtriser

![Automatic Hyperparameter Optimization - RL Tutorial ICRA 2022](https://images.openai.com/static-rsc-4/uHucCXbBcTqLviwG1efqR-0lFz6DBKjOHiewtHnkaMkXRpN16XKiWfCbQ85QKtgEdVUSa3b16i_WPxgv0rQM_P80ScuBVZV6qO5eDeTUFpa6JPVXEWJiyLi9dGt4y7XhTBLTpx7m4fD_4leiyJT4O0GoVSsR4e342tQ4YBCAiS4?purpose=inline)

Hyperparameter Optimization

Vizier, BOHB, Hyperband, Random Search.

![Information, Inference and Machine Learning Group at University College London](https://images.openai.com/static-rsc-4/W0Y6dIDu1ACySqnN25hzrw8DglOi-_BiCkZ0okn5xaONyhPKIPmtHm48RN1FqtkEWORd_9KaXk8GKowbqhg_xze7JkrnEh78wzg8PITAUDywCpSrlyttOR-6OELXdWa41h4iPItQEQUkwE-cuoMBPxR2ywGbbLoUqT1EO0ZiOS0?purpose=inline)

Meta-Learning

Apprendre des expériences passées pour prédire les futures.

![Mathematics Visualizations for Machine Learning | Apatero](https://images.openai.com/static-rsc-4/0AWPuqYscnQA0DMmm25yrU7eIvcUin8o0hlj73pRLfz9itUNUnd73JGsp5u5FzROjKfRSvAWu0wF13sSCOD6c_4jbZLYUBZZ4hpPX5WsaJpqlB7oCwEmdw8YA_Ibftq3DK3SHSFrH9loudZYcpETG6zPjtMlSjDhsMny391s1XU?purpose=inline)

Training Dynamics

Gradients, Hessian, Jacobian, courbure et stabilité.

![7 Ways to Initialize Deep Learning Models | by Maryum Arif | Medium](https://images.openai.com/static-rsc-4/Iu46Imjq_1PpXzXpQ-qxatYH_QkTVTecoHuq9tjqGevVy4nnAO82IfcfrA_CR_OVtjaSWZTFLQC3DzHI-7GulU_3L3_1g8X6bLDaG89XAaxViIG2veaa6WLmjtyDT2t3g56YTGQCkuXbAhqKs90MLmCFDGtSPe1QYmjIrIkMykM?purpose=inline)

Initialization Theory

Xavier, He, orthogonal, dynamical isometry.

![Iclr 2024 openreview](https://images.openai.com/static-rsc-4/QsVJC_RfmdR3spk-oksHDpYySZs8IZUhni3W4IBg3x7EgCFNEzs187C2ql1GlXka-V6toQVVnwCogSKxuMvScw0vXZyW7a9iTQKS4zUqlYW48xVYRAfELM9VSL4Rz4vBMEwVKriZXjuZXJNxmGeCCtjzmTPLjpXuhl0iLypuUwQ?purpose=inline)

Training-Free Prediction

Zero-cost proxies, NEAR, NASWOT, SynFlow.

![Optimizing the Labeling Process](https://images.openai.com/static-rsc-4/iA_uJ-UNZo9D6D9Gcy08Nk0-K8DktUd7MOY1RwrJV_CrkW-VsC2ZuKgKTPzfPbnr-X6EO1HdsDcXGLd4bI6T6nEnajLwi0o7LCuns4iz3fh7RvWbyML2QO4nB0y9q2H7AwCFqC8MwqdO3mi58iCM0HhNHiV7G8H4E9HNVA0pYSY?purpose=inline)

Sample Efficiency

Active learning, data selection, curriculum et dataset valuation.

## Bibliothèque officielle de départ

Je te conseille de créer un dossier `papers/` contenant exactement ces références :

papers/ │ ├── 01_hyperparameter_optimization/ │ ├── Google_Vizier.pdf │ ├── HPO_Foundations.pdf │ └── BOHB.pdf │ ├── 02_meta_learning/ │ ├── Meta_BO.pdf │ └── Learned_Optimizers.pdf │ ├── 03_training_free/ │ ├── Zero_Cost_Proxies.pdf │ ├── Zero_Shot_NAS.pdf │ ├── NEAR.pdf │ └── ProxyBO.pdf │ ├── 04_initialization/ │ ├── Orthogonal_Initialization.pdf │ ├── Dynamical_Isometry.pdf │ └── NTK_Orthogonal.pdf │ ├── 05_sample_efficiency/ │ ├── Deep_Active_Learning.pdf │ └── Comparative_Active_Learning.pdf │ └── 06_benchmarks/ ├── NAS_Bench.pdf ├── OpenML.pdf └── AutoML_Frameworks.pdf

Ce corpus constitue une excellente base scientifique pour écrire le State of the Art de PRECOG, construire les hypothèses de recherche et identifier précisément ce qui existe déjà avant de proposer une contribution originale.
Oui. Après recherche, il existe une famille entière de travaux scientifiques qui partagent la philosophie de PRECOG : réduire le coût de l'entraînement, prédire les performances avant ou avec très peu d'entraînement, optimiser automatiquement les hyperparamètres, améliorer l'initialisation et comprendre la dynamique de convergence.

Il est important de préciser qu'aucun document ne décrit exactement PRECOG. PRECOG se situe à l'intersection de plusieurs domaines de recherche. Les documents ci-dessous constituent donc le corpus scientifique de référence à étudier.

# Les 8 piliers scientifiques de PRECOG

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(255%2C%20255%2C%20255\)%22%20viewBox%3D%220%200%20320%20420%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20width%3D%22320%22%20height%3D%22420%22%20rx%3D%2218%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.15%22%20stroke-width%3D%221.5%22%2F%3E%3Crect%20x%3D%2278%22%20y%3D%2218%22%20width%3D%22164%22%20height%3D%2236%22%20rx%3D%2210%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.08%22%20stroke%3D%22currentColor%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2231%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPRECOG%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2243%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EPredictive%20Training%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2251%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EOptimization%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%2254%22%20x2%3D%22160%22%20y2%3D%2268%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2218%22%20y%3D%2268%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%2284%22%20y%3D%2282%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EHyperparameter%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%2293%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EOptimization%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22106%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EVizier%20%E2%80%A2%20BOHB%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%2268%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22236%22%20y%3D%2282%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EMeta-Learning%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%2293%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ELearned%20Optimizers%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22106%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EPrior%20knowledge%3C%2Ftext%3E%3Cline%20x1%3D%2284%22%20y1%3D%22120%22%20x2%3D%22160%22%20y2%3D%22145%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Cline%20x1%3D%22236%22%20y1%3D%22120%22%20x2%3D%22160%22%20y2%3D%22145%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2294%22%20y%3D%22145%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22159%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ETraining-Free%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22170%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPrediction%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22183%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EZero-cost%20proxies%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22197%22%20x2%3D%22160%22%20y2%3D%22212%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2218%22%20y%3D%22212%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%2284%22%20y%3D%22226%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EInitialization%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22237%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EDynamical%20Isometry%3C%2Ftext%3E%3Ctext%20x%3D%2284%22%20y%3D%22250%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EGradient%20flow%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%22212%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22236%22%20y%3D%22226%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ETraining%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22237%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EDynamics%3C%2Ftext%3E%3Ctext%20x%3D%22236%22%20y%3D%22250%22%20font-size%3D%227%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3ELoss%20%E2%80%A2%20Hessian%3C%2Ftext%3E%3Cline%20x1%3D%2284%22%20y1%3D%22264%22%20x2%3D%22160%22%20y2%3D%22289%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Cline%20x1%3D%22236%22%20y1%3D%22264%22%20x2%3D%22160%22%20y2%3D%22289%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2294%22%20y%3D%22289%22%20width%3D%22132%22%20height%3D%2252%22%20rx%3D%2210%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22303%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3ESample%20Efficiency%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22314%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EActive%20Learning%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22325%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3EData%20Selection%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22341%22%20x2%3D%22160%22%20y2%3D%22356%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.4%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2254%22%20y%3D%22356%22%20width%3D%22212%22%20height%3D%2246%22%20rx%3D%2212%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.06%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22371%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EObjectif%20final%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22384%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Epr%C3%A9dire%20la%20meilleure%20configuration%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22394%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eavant%20le%20training%20complet%3C%2Ftext%3E%3C%2Fsvg%3E)

# 1. Hyperparameter Optimization

C'est le domaine le plus proche de Google Vizier.

![Google Vizier — Taylor Vennel | Senior Creative + Brand Designer](https://images.openai.com/static-rsc-4/UUHJvD6x5yDZEPiOPHXaviA6PhBIFEXYZI1e2c5FV4LlN3aq5Y_2D26d4Tum46_9cxccRCdzDpwKV9woPEZTgRc1-hZ7oa2Bk9IXhYrY8_DsmjfpsO3lJsz_PXyxaY-8enZ7yuuAqLRBd-W8k--Btwh3fo5w_zmyXFjTATrsdRU?purpose=inline)

### Google Vizier

Fondamental

Document : Google Vizier: A Service for Black-Box Optimization

Ce papier décrit le moteur de Google pour optimiser automatiquement des hyperparamètres et des fonctions objectives complexes par black-box optimization. C'est la baseline industrielle la plus importante pour PRECOG.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

Google Research

Google Vizier: A Service for Black-Box Optimization

![recent advances in bayesian optimization .pdf](https://images.openai.com/static-rsc-4/v9_ZK_Tmz0Eeww07AHu4DEYvFoyr2K_OQHbfBVdYpEEPldTBVRd6OEzTnzDH4lmzFI08bCZkgo2Qx1JKLN1dmijDW3WD_D56AdYUUb_jWiR6EUAcmoDnc7YHVTjnjZG9qqEOCdDjTSHU4sEdYD5fdWYqAvJqxFhdSaABgIB0rLc?purpose=inline)

### Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

Document de référence : grande revue scientifique sur Grid Search, Random Search, Bayesian Optimization, Hyperband et les défis ouverts.

Ce document doit servir de base théorique pour construire le module `optimization/` de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv survey

Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

![AutoML | BOHB: Robust and Efficient Hyperparameter Optimization at Scale](https://images.openai.com/static-rsc-4/Yi6zfM3BSjKJTx6Ni-lprD23_Z29HCRyVl0cMG36pqpX5HkwxerbkglNW8JbzZ-kT5sQ-3plCl8dgMrPkoGqigIUxZImCqcsbiWK8fujst1AeKVcvON7wtpev6an7k-QyMzw4AHBMioQla8Y1QnVl5rNz1zjhbbLdMeLVStLAn8?purpose=inline)

### Hyperparameter Optimization in Machine Learning

Revue récente expliquant les méthodes modernes de recherche d'hyperparamètres, y compris BOHB qui combine Bayesian Optimization et Hyperband pour améliorer l'efficacité des essais.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arxiv.org

Hyperparameter Optimization in Machine Learning

# 2. Meta-Learning : apprendre des expériences précédentes

La philosophie de PRECOG repose fortement sur cette idée :

> Les expériences passées doivent devenir une connaissance réutilisable.

![Bo Zhao (@BoZhao\_\_) on X](https://images.openai.com/static-rsc-4/zX-qzqtX3ibRUxuIVrdIVlwufzVuzLP1XBfvKlvJ-lxvu9FtmwoGeK_4dsCx9As9zFwKI8JVKi2WAODk7qPf0VvwK_-egMdENq8j8HaPgoLMeCSYL31WdwZMLI5Y06KQ09qmX3Z0epg--aqHziGW8intNAROHxiMDrKev6G3xeU?purpose=inline)

### Initializing Bayesian Hyperparameter Optimization via Meta-Learning

Ce papier montre qu'on peut utiliser des tâches précédentes pour démarrer l'optimisation dans des régions prometteuses plutôt que repartir de zéro.

C'est exactement la logique du futur Meta-Dataset de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

ojs.aaai.org+1

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

AAAI

Initializing Bayesian Hyperparameter Optimization via Meta-Learning

![Gradient-Based Optimizers in Deep Learning - Analytics Vidhya](https://images.openai.com/static-rsc-4/byb7HwBacdWxO4eBx6fgFsKfgcejpNhqFnUdwErZewNonI_GZz1YaH9PlgCW3ODvvLdamo65LJKvYOZEQPzzRnSXWKj3IZsHLKb6VX1am39DWoR4h9akf2dywqJhRJF2LSmi1WLT6RWsa_V3BtCqJwfwp-rPT77E_2gCBqtuHK8?purpose=inline)

### Learned Optimizers that Scale and Generalize

Les auteurs proposent un optimiseur lui-même appris par un réseau de neurones afin de généraliser sur de nouvelles tâches.

Cette branche est essentielle si PRECOG évolue vers un optimiseur appris plutôt qu'un simple prédicteur d'hyperparamètres.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

PMLR ICML

Learned Optimizers that Scale and Generalize

![Axon and Myelin Sheath Segmentation in Electron Microscopy Images using Meta Learning - PMC](https://images.openai.com/static-rsc-4/I_R2m9RZhkGUwfMCPebKMJGNnn9PuQ6dJL-3V8oxYFGuEFFGjH40O6R5Ebp6X1ohV8cS4K9JH0vKJvnJegeOEBoHMTothaJ9iSug5WU7h6_mkFM13_22qVI-w8taJubkUd1oGlYUXVhyyPuVt0lSHerf04ImWRJZ7j9LmQUI8GY?purpose=inline)

### Meta-Learning Bidirectional Update Rules

Étudie des règles de mise à jour apprises au lieu des règles classiques de descente de gradient.

Très pertinent pour imaginer une future version de PRECOG où les updates elles-mêmes deviennent prédictives.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

PMLR

Meta-Learning Bidirectional Update Rules

# 3. Training-Free Prediction

C'est probablement la branche la plus proche de ton idée originale.

L'objectif est de prédire les performances d'un réseau sans effectuer son entraînement complet.

![Abacus.AI at NeurIPS 2022 - The Abacus.AI Blog](https://images.openai.com/static-rsc-4/wumTrDmx04iDV7QBgfPiHRYQVEH8nYZTTrtpTH2ER9CHMFOYjXg5ZlcAreaBFw3qezleOP1s1AZpvYwik6dQrbJMrQf6_LQqW4UAttripNOcf_wXK1fR9_1dSnzaonCMeD1a4N2fN8SVpQDEY68mguE4zW3IVhX-gqa20fu3PTY?purpose=inline)

### Zero-Cost Proxies for Lightweight NAS

Très important

Ce papier introduit les zero-cost proxies, capables d'évaluer des architectures avec seulement une initialisation et un mini-batch, sans entraînement complet.

C'est une inspiration directe pour PRECOG-0.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Zero-Cost Proxies for Lightweight NAS

![Publications | Abdelfattah Research Group at Cornell University](https://images.openai.com/static-rsc-4/nwmHfGB3lV2nu7d4PrZVORFIfhPfeujoGqq8rDO-ImAkzlfhhrQq1rQ7kRApNUtkoxEIfj-jE9xngux9heOkyLQx8lLGcmME1gzhX3hd4Iy0qcmtsPJBqf8kCUuLp82Licv8dlUs2mADaCEs8weFA1bf7SYUC51mnd1TzyitSoU?purpose=inline)

### Zero-Shot Neural Architecture Search

Revue complète des méthodes permettant de prédire la qualité d'une architecture sans entraîner ses paramètres.

Elle donne une cartographie scientifique des proxies zéro entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Zero-Shot Neural Architecture Search

![ICLR Poster NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance](https://images.openai.com/static-rsc-4/p_9YQf0h71LyXsBFjum4detP2QGEeNRhUVW8D5AvO7i6mjFHrtaLUApXDMs6ZYY5qdrer7XxaYeey3FlB2QmbN7ViS6vk6F4se0yTKu_zpgFNMkatuUVCqZvkq72JlCOKWBKVyHDXo14S11kZexqGbPJBbK0sGmyWmmQRbnIqYw?purpose=inline)

### NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

L'un des papiers les plus intéressants pour PRECOG.

Il propose un score basé sur le rang effectif des activations afin d'estimer la performance future d'un réseau et montre également une utilisation pour sélectionner certaines initialisations et fonctions d'activation.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

![Iclr 2024 openreview](https://images.openai.com/static-rsc-4/QsVJC_RfmdR3spk-oksHDpYySZs8IZUhni3W4IBg3x7EgCFNEzs187C2ql1GlXka-V6toQVVnwCogSKxuMvScw0vXZyW7a9iTQKS4zUqlYW48xVYRAfELM9VSL4Rz4vBMEwVKriZXjuZXJNxmGeCCtjzmTPLjpXuhl0iLypuUwQ?purpose=inline)

### ProxyBO

Combine les zero-cost proxies avec Bayesian Optimization afin d'accélérer la recherche de bonnes architectures.

Très proche de l'idée d'utiliser des signaux analytiques avant d'investir dans un entraînement coûteux.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

ProxyBO

![NeurIPS Poster Per-Architecture Training-Free Metric Optimization for Neural Architecture Search](https://images.openai.com/static-rsc-4/55P3YmqsRsYyn0xPSAJt121PhdZgNBoJ1__IMpqVh_p68j2T5PBF9JPCQ9iPUfBduBflxk6UBe-kh210uPGWHjJNz7XsJMSh6G3ZH98XdFiVW4KE5kioMJNpWfk6LaWIg9inFSm5UCodCAI8iV-HFCRNclggHX4N32namyX1xW4?purpose=inline)

### TG-NAS

Utilise un Transformer et un GCN comme proxy universel pour prédire les performances d'architectures sans réentraîner le prédicteur sur chaque espace de recherche.

Très intéressant pour la partie Model Analyzer de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

TG-NAS

# 4. Initialisation et Dynamical Isometry

Cette branche cherche à répondre à une autre question fondamentale :

> Pourquoi certaines initialisations permettent-elles une convergence beaucoup plus rapide ?

![7 Ways to Initialize Deep Learning Models | by Maryum Arif | Medium](https://images.openai.com/static-rsc-4/Iu46Imjq_1PpXzXpQ-qxatYH_QkTVTecoHuq9tjqGevVy4nnAO82IfcfrA_CR_OVtjaSWZTFLQC3DzHI-7GulU_3L3_1g8X6bLDaG89XAaxViIG2veaa6WLmjtyDT2t3g56YTGQCkuXbAhqKs90MLmCFDGtSPe1QYmjIrIkMykM?purpose=inline)

### Provable Benefit of Orthogonal Initialization in Optimizing Deep Linear Networks

Fondamental

Ce papier démontre mathématiquement que l'initialisation orthogonale peut accélérer la convergence dans les réseaux linéaires profonds par rapport à certaines initialisations gaussiennes.

C'est une référence incontournable pour le module `initialization/`.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Provable Benefit of Orthogonal Initialization in Optimizing Deep Linear Networks

![Understanding implicit regularization in deep learning by analyzing trajectories of gradient descent – Off the convex path](https://images.openai.com/static-rsc-4/8CYLgkNDu3WlUgqqvKiJLGYMc7g-SG9h_cSjwnMfrm7_Jqehpgqu-yCXJ1nW-V1_7j5lsDh4eVewMdD2aSsgz_2lJ5RMjq8W3PDoi2tWa7JFDSFILAqQ3bzZYYCE6Uggqx5YRZgkj47Shm_IefcxOnJIeKzoC-8eGgvW_L-66L4?purpose=inline)

### Resurrecting the Sigmoid in Deep Learning Through Dynamical Isometry

Étudie la propagation du signal et montre que certaines conditions d'initialisation permettent une meilleure circulation des gradients et un apprentissage beaucoup plus rapide dans certains régimes.

C'est la base théorique du concept de dynamical isometry.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Resurrecting the Sigmoid in Deep Learning Through Dynamical Isometry

![Weight Initialization: Xavier, He & Variance Preservation - Interactive | Michael Brenndoerfer | Michael Brenndoerfer](https://images.openai.com/static-rsc-4/2rhl-ygGtMNCkBwbK_YToj8pGOeGnARObFC5i-KAKD3tfi_kS4K78KSvBn3XqT4mJiXU_Q3xsEshks3d1q039vb8oWlc_UMOGnfyG-Rrf595vzFKXl2ij1Uy86Hn4XXpA3ZFi779ZUtjIJekL-YMeKi6IraeGUp3JIgFi5fbW9s?purpose=inline)

### On the Neural Tangent Kernel of Deep Networks with Orthogonal Initialization

Analyse le lien entre orthogonalité, NTK et vitesse d'apprentissage.

Très utile si PRECOG veut exploiter des propriétés géométriques avant entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

On the Neural Tangent Kernel of Deep Networks with Orthogonal Initialization

![Structure, Disorder, and Dynamics in Task-Trained Recurrent Neural Circuits - Kempner Institute](https://images.openai.com/static-rsc-4/eetZqQ2zfNRTFdttH4jx8ZVFqhI6dPq5HHjK0IRwG3gEVg2ruY0oTwORwPJ28q9nzeFiTjtT1QjyuuOHv6yQhnVTWqoLBYUK_9NdtSxiB0agbVoDoJ2UX3NiNjrGTwc7fEPUinnxAuuk4gd7RPizYq9I0lla5Jaef-2t7nVlXJo?purpose=inline)

### Dynamical Isometry and a Mean Field Theory of RNNs

Développe une théorie de la propagation du signal à l'initialisation à l'aide de la théorie des matrices aléatoires et du mean-field.

Important pour comprendre comment analyser un réseau vierge.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

Dynamical Isometry and a Mean Field Theory of RNNs

# 5. Training Dynamics et géométrie de l'apprentissage

PRECOG veut mesurer ce qui se passe pendant les premières étapes de l'apprentissage afin de prédire la suite.

Les domaines associés sont :

* Gradient Flow

* Loss Landscape

* Hessian Spectrum

* Jacobian Analysis

* Sharpness

* Curvature

* Gradient Noise

* Gradient Alignment

![Cross Entropy Loss: Intro, Applications, Code](https://images.openai.com/static-rsc-4/1VvWQpI0BTA1xF49WaPzmlL5cK53zTegmiVl5Cw4DNlq_43zQvwzop7JZnnf7ACtSxj6lhPiVI6MaMMIxPyBQWRB7CqrQ7xmaOTuby47zrdtlHqdpVesGHc-za83_9uejDh5zOIh5_zADCOwLuNskYJWWL-WgzVnduitlbfG5qY?purpose=inline)

### Deep Network Trainability via Persistent Subspace Orthogonality

Travail récent approfondissant la notion de dynamical isometry et la relation entre orthogonalité persistante et facilité d'entraînement.

Il montre que la géométrie interne du réseau reste un sujet actif de recherche.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arxiv.org

Deep Network Trainability via Persistent Subspace Orthogonality

# 6. Sample Efficiency et moins de données

Ton objectif n'est pas seulement de réduire les epochs.

Tu veux aussi réduire :

NϵN_{\epsilon}Nϵ

c'est-à-dire le nombre de données nécessaires pour atteindre une performance cible.

![Jidong ZHAO | Professor | Ph.D. | Hong Kong University of Science and Technology, Hong Kong | UST | Department of Civil and Environmental Engineering | Research profile](https://images.openai.com/static-rsc-4/BcDQCf-KRh3AVxtPi3bz87l71OY7M961zuDMOXGVu8kKjoLSqobdYtLaIb5ABZuOuwp49z0S8NxDw1POkqNcGMZNNVrFZUqM-kwPWQ9O710hMbdteuO_yP0OBSUVDcyussnHRlS6ITdK9ngat1fWbPw-M0FDmjEEuaatZJ3EodA?purpose=inline)

### A Survey of Deep Active Learning

Référence

L'active learning cherche explicitement à maximiser le gain de performance en annotant le moins d'exemples possible.

C'est une littérature essentielle pour la partie sample efficiency de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

A Survey of Deep Active Learning

![When deep learning meets active learning in the era of foundation models | EurekAlert!](https://images.openai.com/static-rsc-4/WxXAzSwL9L9qhTcvUA94_DPJ5PQHayxC8DsYvhERk4FIVL1658DUw4vdzhG_-pBYBskMfPoTEmO8mL5zu0qoUyDPsK67cdGl4G2iEVIIj5_pMLYsnb_rGcKI2ub397Ee8-wBCcRwqtNg2EMWZy9YPQNIkEj29iSjCSd3NIlSW3I?purpose=inline)

### A Comparative Survey of Deep Active Learning

Compare de nombreuses méthodes d'active learning dans un cadre expérimental homogène.

Très utile pour construire les futurs benchmarks de PRECOG.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

A Comparative Survey of Deep Active Learning

# 7. Neural Architecture Search sans entraînement

Même si PRECOG ne cherche pas d'abord la meilleure architecture, cette littérature apporte les méthodes permettant de prédire la qualité d'un réseau vierge.

Documents importants :

![An Efficient Evolutionary Neural Architecture Search Algorithm Without Training](https://images.openai.com/static-rsc-4/a6TOVzWn1LC0RXjlxYPztmNlRC3DHgatBG1s2X37I-ABz5lv3ONin3eFtJCDATLASbsVYJGCeetXS_eco3uOGVOeOKx6GS5r7X_1QZZPEW5ypIfGoEfrD1SkCnVpVivP66ZtnaHOXlKOZxCNqY6p2b1vd_8_SV_K1jC3a9ijqlY?purpose=inline)

### NASWOT et les Zero-Cost Proxies

Cette famille de travaux introduit des scores calculés à l'initialisation permettant de classer des architectures sans les entraîner complètement. Elle constitue une inspiration méthodologique directe pour PRECOG.

![](https://www.google.com/s2/favicons?domain=https://iclr-blog-track.github.io\&sz=32)

iclr-blog-track.github.io+1

![](https://www.google.com/s2/favicons?domain=https://iclr-blog-track.github.io\&sz=32)

ICLR Blog Track

A Deeper Look at Zero-Cost Proxies

![A Generic Graph-based Neural Architecture Encoding Scheme for Predictor-based NAS | Hyunju Kim](https://images.openai.com/static-rsc-4/49X_Hr8TfAlh98NTZXbWt1Xqto_bdD0RTKSdT3AidRSyIIZzpfdy_1FUoRDN73ejfwD8Tm8f51BsLlsvSjHmvHqSVhOr6mvARtfDvJwGMk2gcaY5sfzoqH9uEhQbI6emvYp79Q1xjXEFT0CRPj_u_HM3rFlnh0xXFw4ZojJsXQg?purpose=inline)

### Generic Neural Architecture Search via Regression

Explore la prédiction de performances d'architectures par régression et l'utilisation de représentations des réseaux plutôt que des entraînements complets.

![](https://www.google.com/s2/favicons?domain=https://openreview.net\&sz=32)

openreview.net

![](https://www.google.com/s2/favicons?domain=https://openreview.net\&sz=32)

OpenReview

Generic Neural Architecture Search via Regression

![2023年 18篇神经架构搜索(Neural Architecture Search) ICCV ICML NIPS IJCAI 阅读笔记\_prenas: preferred one-shot learning towards effici-CSDN博客](https://images.openai.com/static-rsc-4/_SlqvfyDfQNFBU-KzjqdtjTH60brrapixodI8uvjZqnyZNwq8xH-FbY2Utwq9-wR51m4P5pb0r0tvXJqAR2QMuacqvu-_nw7R6ig9uRyO4EJGekZueVJMYurMVJI7CTwLmWthT7zXkLhjr1H22lCPLr4mRANpyaKHztuCTq8VOs?purpose=inline)

### RBFleX-NAS

Recherche récente sur les approches training-free pour sélectionner des architectures avec un coût minimal. Intéressant pour suivre l'évolution du domaine.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

RBFleX-NAS

# 8. Outils open-source à étudier

Ces projets ne partagent pas toute la philosophie de PRECOG, mais ils constituent l'infrastructure de référence.

![Google Vizier — Taylor Vennel | Senior Creative + Brand Designer](https://images.openai.com/static-rsc-4/UUHJvD6x5yDZEPiOPHXaviA6PhBIFEXYZI1e2c5FV4LlN3aq5Y_2D26d4Tum46_9cxccRCdzDpwKV9woPEZTgRc1-hZ7oa2Bk9IXhYrY8_DsmjfpsO3lJsz_PXyxaY-8enZ7yuuAqLRBd-W8k--Btwh3fo5w_zmyXFjTATrsdRU?purpose=inline)

### Google Vizier

Framework open-source de black-box optimization inspiré du système utilisé chez Google.

À étudier pour : moteur de recherche d'hyperparamètres et API d'expérimentation.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

Google Vizier

![Optuna: A Practical Guide to Hyperparameter Optimization](https://images.openai.com/static-rsc-4/eNbSmAa6A05hq_wfqkcHigMl_nEUjzvo4zXY2-x5SUrUZLTQKumXy-tLixK7Zx47WOJJFcA589YeG2zxsu7vl2mUNkGAlprc42q3YhjIo5g53rvAie3n9bOzs3tbyls8bFnw4otNesI697DveQRrTf_C3jd3sW2a2cNM6srFxMw?purpose=inline)

### Optuna

Framework très utilisé pour les études expérimentales reproductibles et les algorithmes modernes de tuning.

À utiliser comme baseline expérimentale.

![](https://www.google.com/s2/favicons?domain=https://optuna.org\&sz=32)

Official website

Optuna

![Ray Tune: a Python library for fast hyperparameter tuning at any scale | by Richard Liaw | TDS Archive | Medium](https://images.openai.com/static-rsc-4/DF5Uo7DnpiayYJbvDNZawe3_NDYseDQW5jK56Culr6nhk7_FgWnYYXeAsO123NomOaP6xR0zxGleEYa914BvnWUj5apMKmgAohShONZWinAl1YHNYgK0WrrZxtU-dEdcFWi6ldTIKJnie5EEUzHsLI8a5Ou2wZmfiZ7DLG8M5s8?purpose=inline)

### Ray Tune

Bibliothèque distribuée pour exécuter des milliers d'expériences parallèles sur plusieurs GPU ou clusters.

Très pertinent pour PRECOG Cloud.

![](https://www.google.com/s2/favicons?domain=https://docs.ray.io\&sz=32)

Official documentation

Ray Tune Documentation

![Kubernetes & AI - Beauty and the Beast !?! @KCD Istanbul 2024 | PDF](https://images.openai.com/static-rsc-4/MVLEXCgb9Kc5BexE1_aeXej7DEQhb9zGyE7_0T0IjdVuDQZJiYqVA5bg_xlw-DFtlFE6GhccGKNBpt7LNh6pafxWP77fkK1ZDalYjxqu6fbc-kxgpYCXOyErBpdy_yL3Ya8DwoF1y2EOIyXO2tPg5B7bV-6ygj9G5gIwUtiQowY?purpose=inline)

### Katib

Système de tuning intégré à Kubernetes pour les pipelines MLOps.

À étudier pour l'industrialisation enterprise.

![](https://www.google.com/s2/favicons?domain=https://www.kubeflow.org\&sz=32)

Official documentation

Kubeflow Katib

### Awesome AutoML

Une collection open-source regroupant les principaux frameworks AutoML, HPO, NAS et outils de benchmark.

Très utile comme index de recherche bibliographique.

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

![](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

Awesome AutoML

# Les documents les plus proches de PRECOG

Si ton objectif est de construire PRECOG, voici les 10 lectures prioritaires dans l'ordre.

1. Google Vizier: A Service for Black-Box Optimization

Base industrielle de l'optimisation des hyperparamètres.

![](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google

![CVPR Poster Efficient Hyperparameter Optimization with Adaptive Fidelity Identification](https://images.openai.com/static-rsc-4/xMiPkqep8BGuyGpPQTFVcAWypIQMG6_XXPe5lImGfZLvGKQnr5DbBViUWanJym0vHdUDQZh8qQWSNCPKKwrppQV6ex0AkHSrmxjdWllYvA2F9zrMZpn8iFXWDm8ug4xalvVk5LOM_cKtKMZ4OyM3MH4XhTqx3WsfFcvk-GBcXsk?purpose=inline)

2. Hyperparameter Optimization: Foundations, Algorithms, Best Practices and Open Challenges

Référence théorique complète sur le HPO.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS Poster NAS-Bench-Suite-Zero: Accelerating Research on Zero Cost Proxies](https://images.openai.com/static-rsc-4/pDUDX4-l9Iqw7RTnP6GphfwBataSqHaIHpFOPjoOoEQlQdJsNvwMuP1oWSsQUMiNuAu93JBAXh7s5PRT4wOjnsGZvRmosUMwYJQn6fVz1EqNOYi21vE9GDIcXIOluDJQ1GaPrWif2mo5OQ0htguIcF8q0UpjChSutFNPzPUXO_4?purpose=inline)

3. Zero-Cost Proxies for Lightweight NAS

Première grande démonstration qu'un réseau peut être évalué sans entraînement complet.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1

![ICLR Poster NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance](https://images.openai.com/static-rsc-4/p_9YQf0h71LyXsBFjum4detP2QGEeNRhUVW8D5AvO7i6mjFHrtaLUApXDMs6ZYY5qdrer7XxaYeey3FlB2QmbN7ViS6vk6F4se0yTKu_zpgFNMkatuUVCqZvkq72JlCOKWBKVyHDXo14S11kZexqGbPJBbK0sGmyWmmQRbnIqYw?purpose=inline)

4. NEAR: A Training-Free Pre-Estimator of Machine Learning Model Performance

Le papier le plus proche de l'idée de prédiction avant entraînement.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS 2022 Towards Learning Universal Hyperparameter Optimizers With Transformers Paper Conference | PDF](https://images.openai.com/static-rsc-4/vXk6d4jWGqX6iTHN39VPjf_WKIcdh6qQGY9XC0r3k1ptcCVWB6KAzg9hP-PM5j0sNRxJZKxWfZfX1wa7OAbo-jeRNAUlD1Lyaisf9l2RPp0sqOmE8ACnlIzPELJS7HiTwbP4mPggPazRJMVCtvYgShii3jQRedSZj-j8tcTem_Y?purpose=inline)

5. Initializing Bayesian Hyperparameter Optimization via Meta-Learning

Fondation du meta-dataset et du transfert d'expérience.

![](https://www.google.com/s2/favicons?domain=https://ojs.aaai.org\&sz=32)

ojs.aaai.org

6. Learned Optimizers that Scale and Generalize

Vers des optimiseurs appris plutôt que manuellement conçus.

![](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

![(PDF) Dynamical Isometry and a Mean Field Theory of CNNs: How to Train 10,000-Layer Vanilla Convolutional Neural Networks](https://images.openai.com/static-rsc-4/HsbMPZKPq19Rnl9yt6u2s9eeMeA8T0Bd54MqRYTgiIIqiGVr3hCEVZtwnbN4L_Ym6ezr6BBxDdbES_K-kVSWR-jaEjzzfyhzTW07wieHxDTaZNXoVxAs5Gv4Lf2bVTI6sJcAc3yfb04UcE4Wl4LJmeLQc6rGggJItWjmfAO0h0w?purpose=inline)

7. Provable Benefit of Orthogonal Initialization

Justification mathématique de l'importance de l'initialisation.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

8. Resurrecting the Sigmoid Through Dynamical Isometry

Comprendre pourquoi certains réseaux propagent mieux les gradients.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![(PDF) A Survey on Deep Active Learning: Recent Advances and New Frontiers](https://images.openai.com/static-rsc-4/7z7eD-I8KhLQvEjp-bmibfpnNj8rfJjdidU94dRuTPte_lVvdp-XesvZV_boCFwhh4hsBCrMZ6X7Mfyei6XXcLBJVEfGJzCXsJ7VVHUEnMjcdu8BgAj-nPHftvBKMX51DfpjruE9WLuhu5lWOPP8Wv0ahvS3SAemxwkVQ6IKSAA?purpose=inline)

9. A Survey of Deep Active Learning

Référence sur l'apprentissage avec moins de données.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

![NeurIPS Poster Per-Architecture Training-Free Metric Optimization for Neural Architecture Search](https://images.openai.com/static-rsc-4/VQFHmlESyOkC9tLLMbhJx18DRA1HOkHhePRex-BPvrKoDsFk05xwlEps7c8DNYsLBTyjjlavNFBvfqOLsEhJ9Dvn2gzVft15AXZa_2GYkVQLPpzpnT24u8Xpo-hOwGyfApgxUAfQT67mvC8SB-l_a0FTUHk5FRZa6jEJ4Xi5DE4?purpose=inline)

10. Zero-Shot Neural Architecture Search

Cartographie complète des méthodes training-free.

![](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv

# La philosophie commune

Tous ces travaux peuvent être résumés par une même idée :

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(255%2C%20255%2C%20255\)%22%20viewBox%3D%220%200%20320%20360%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20width%3D%22320%22%20height%3D%22360%22%20rx%3D%2218%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.15%22%20stroke-width%3D%221.5%22%2F%3E%3Crect%20x%3D%2234%22%20y%3D%2218%22%20width%3D%22252%22%20height%3D%2234%22%20rx%3D%229%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.08%22%20stroke%3D%22currentColor%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2231%22%20font-size%3D%2210%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EPhilosophie%20PRECOG%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2243%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eanalyser%20avant%20de%20d%C3%A9penser%20le%20compute%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%2252%22%20x2%3D%22160%22%20y2%3D%2266%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%2266%22%20width%3D%22248%22%20height%3D%2238%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%2280%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EMod%C3%A8le%20vierge%20%2B%20t%C3%A2che%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%2292%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Earchitecture%20%E2%80%A2%20donn%C3%A9es%20%E2%80%A2%20statistiques%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22104%22%20x2%3D%22160%22%20y2%3D%22118%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22118%22%20width%3D%22248%22%20height%3D%2246%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22132%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EAnalyse%20pr%C3%A9dictive%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22144%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Egradients%20initiaux%20%E2%80%A2%20spectre%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22154%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Eproxy%20%E2%80%A2%20m%C3%A9ta-connaissance%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22164%22%20x2%3D%22160%22%20y2%3D%22178%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22178%22%20width%3D%22248%22%20height%3D%2246%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22192%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EConfiguration%20recommand%C3%A9e%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22204%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3ELR%20%E2%80%A2%20optimizer%20%E2%80%A2%20batch%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22214%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Einitialization%20%E2%80%A2%20scheduler%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22224%22%20x2%3D%22160%22%20y2%3D%22238%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22238%22%20width%3D%22248%22%20height%3D%2240%22%20rx%3D%228%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.22%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22252%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EEntra%C3%AEnement%20minimal%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22264%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Evalidation%20rapide%20de%20l'hypoth%C3%A8se%3C%2Ftext%3E%3Cline%20x1%3D%22160%22%20y1%3D%22278%22%20x2%3D%22160%22%20y2%3D%22292%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.35%22%20stroke-width%3D%221.2%22%20stroke-linecap%3D%22round%22%2F%3E%3Crect%20x%3D%2236%22%20y%3D%22292%22%20width%3D%22248%22%20height%3D%2244%22%20rx%3D%228%22%20fill%3D%22currentColor%22%20fill-opacity%3D%220.06%22%20stroke%3D%22currentColor%22%20stroke-opacity%3D%220.25%22%20stroke-width%3D%221.2%22%2F%3E%3Ctext%20x%3D%22160%22%20y%3D%22306%22%20font-size%3D%229%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%20font-weight%3D%22bold%22%3EObjectif%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22318%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Emoins%20de%20donn%C3%A9es%20%E2%80%A2%20moins%20de%20steps%3C%2Ftext%3E%3Ctext%20x%3D%22160%22%20y%3D%22328%22%20font-size%3D%228%22%20text-anchor%3D%22middle%22%20font-family%3D%22Arial%2C%20Helvetica%2C%20sans-serif%22%20fill%3D%22currentColor%22%3Emoins%20de%20compute%20%E2%80%A2%20m%C3%AAme%20performance%3C%2Ftext%3E%3C%2Fsvg%3E)

La différence essentielle est la suivante :

|
Domaine

|

Question posée

|
| --- | --- |
|

Google Vizier

|

Quels hyperparamètres donnent le meilleur résultat après des essais ?

|
|

Optuna / Ray Tune

|

Comment rechercher efficacement les meilleures configurations ?

|
|

Zero-Cost NAS

|

Peut-on évaluer un réseau sans l'entraîner ?

|
|

Dynamical Isometry

|

Quelle initialisation favorise la propagation des gradients ?

|
|

Learned Optimizers

|

Peut-on apprendre une meilleure règle d'optimisation ?

|
|

Active Learning

|

Comment atteindre une performance avec moins de données ?

|
|

PRECOG

|

Peut-on prédire avant le training les meilleures conditions de convergence en combinant toutes ces connaissances ?

|

C'est précisément là que se situe l'originalité potentielle de ton projet : PRECOG n'invente pas un nouveau domaine, il cherche à unifier plusieurs branches de recherche aujourd'hui séparées dans un même système de prédiction de la dynamique d'entraînement.

## Les 6 domaines de recherche que tu dois maîtriser

![Automatic Hyperparameter Optimization - RL Tutorial ICRA 2022](https://images.openai.com/static-rsc-4/uHucCXbBcTqLviwG1efqR-0lFz6DBKjOHiewtHnkaMkXRpN16XKiWfCbQ85QKtgEdVUSa3b16i_WPxgv0rQM_P80ScuBVZV6qO5eDeTUFpa6JPVXEWJiyLi9dGt4y7XhTBLTpx7m4fD_4leiyJT4O0GoVSsR4e342tQ4YBCAiS4?purpose=inline)

Hyperparameter Optimization

Vizier, BOHB, Hyperband, Random Search.

![Information, Inference and Machine Learning Group at University College London](https://images.openai.com/static-rsc-4/W0Y6dIDu1ACySqnN25hzrw8DglOi-_BiCkZ0okn5xaONyhPKIPmtHm48RN1FqtkEWORd_9KaXk8GKowbqhg_xze7JkrnEh78wzg8PITAUDywCpSrlyttOR-6OELXdWa41h4iPItQEQUkwE-cuoMBPxR2ywGbbLoUqT1EO0ZiOS0?purpose=inline)

Meta-Learning

Apprendre des expériences passées pour prédire les futures.

![Mathematics Visualizations for Machine Learning | Apatero](https://images.openai.com/static-rsc-4/0AWPuqYscnQA0DMmm25yrU7eIvcUin8o0hlj73pRLfz9itUNUnd73JGsp5u5FzROjKfRSvAWu0wF13sSCOD6c_4jbZLYUBZZ4hpPX5WsaJpqlB7oCwEmdw8YA_Ibftq3DK3SHSFrH9loudZYcpETG6zPjtMlSjDhsMny391s1XU?purpose=inline)

Training Dynamics

Gradients, Hessian, Jacobian, courbure et stabilité.

![7 Ways to Initialize Deep Learning Models | by Maryum Arif | Medium](https://images.openai.com/static-rsc-4/Iu46Imjq_1PpXzXpQ-qxatYH_QkTVTecoHuq9tjqGevVy4nnAO82IfcfrA_CR_OVtjaSWZTFLQC3DzHI-7GulU_3L3_1g8X6bLDaG89XAaxViIG2veaa6WLmjtyDT2t3g56YTGQCkuXbAhqKs90MLmCFDGtSPe1QYmjIrIkMykM?purpose=inline)

Initialization Theory

Xavier, He, orthogonal, dynamical isometry.

![Iclr 2024 openreview](https://images.openai.com/static-rsc-4/QsVJC_RfmdR3spk-oksHDpYySZs8IZUhni3W4IBg3x7EgCFNEzs187C2ql1GlXka-V6toQVVnwCogSKxuMvScw0vXZyW7a9iTQKS4zUqlYW48xVYRAfELM9VSL4Rz4vBMEwVKriZXjuZXJNxmGeCCtjzmTPLjpXuhl0iLypuUwQ?purpose=inline)

Training-Free Prediction

Zero-cost proxies, NEAR, NASWOT, SynFlow.

![Optimizing the Labeling Process](https://images.openai.com/static-rsc-4/iA_uJ-UNZo9D6D9Gcy08Nk0-K8DktUd7MOY1RwrJV_CrkW-VsC2ZuKgKTPzfPbnr-X6EO1HdsDcXGLd4bI6T6nEnajLwi0o7LCuns4iz3fh7RvWbyML2QO4nB0y9q2H7AwCFqC8MwqdO3mi58iCM0HhNHiV7G8H4E9HNVA0pYSY?purpose=inline)

Sample Efficiency

Active learning, data selection, curriculum et dataset valuation.

## Bibliothèque officielle de départ

Je te conseille de créer un dossier `papers/` contenant exactement ces références :

papers/ │ ├── 01_hyperparameter_optimization/ │ ├── Google_Vizier.pdf │ ├── HPO_Foundations.pdf │ └── BOHB.pdf │ ├── 02_meta_learning/ │ ├── Meta_BO.pdf │ └── Learned_Optimizers.pdf │ ├── 03_training_free/ │ ├── Zero_Cost_Proxies.pdf │ ├── Zero_Shot_NAS.pdf │ ├── NEAR.pdf │ └── ProxyBO.pdf │ ├── 04_initialization/ │ ├── Orthogonal_Initialization.pdf │ ├── Dynamical_Isometry.pdf │ └── NTK_Orthogonal.pdf │ ├── 05_sample_efficiency/ │ ├── Deep_Active_Learning.pdf │ └── Comparative_Active_Learning.pdf │ └── 06_benchmarks/ ├── NAS_Bench.pdf ├── OpenML.pdf └── AutoML_Frameworks.pdf

Ce corpus constitue une excellente base scientifique pour écrire le State of the Art de PRECOG, construire les hypothèses de recherche et identifier précisément ce qui existe déjà avant de proposer une contribution originale.
