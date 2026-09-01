# 🏛️ PRAGATI-Land : Statutory Compliance & Delay Mitigation Engine

> **An AI-Powered Geospatial Decision Support System (DSS) for Proactive Land Acquisition Monitoring, Explainable Delay Prediction, and Administrative Execution under the RFCTLARR Act, 2013.**

---

## 📌 Executive Summary & Problem Statement

Land acquisition for major infrastructure corridors (e.g., *Delhi-Amritsar Expressway*, Dedicated Freight Corridors) is frequently disrupted by fragmented land records, succession disputes, litigation stays, and slow inter-departmental clearances. 

### ⚠️ The Critical Challenge: Statutory Lapsing (Section 19(7))
Under the **Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement (RFCTLARR) Act, 2013**:
* A mandatory deadline of **12 months (365 days)** exists between the Section 11 Preliminary Notification and Section 19 Final Gazette Declaration.
* If this timeline expires, the entire acquisition proceeding **legally lapses (cancelled)**, forcing administration to restart surveys from Day-1, incurring thousands of crores in public exchequer losses and idling civil construction.

**PRAGATI-Land** monitors contiguous corridors in real time, predicts project lifecycle delays using Machine Learning, isolates root causes with **TreeSHAP Explainable AI**, dynamically assigns nodal officers, and auto-generates **ready-to-sign administrative order memos** to eliminate bureaucratic latency.

---

## 🎯 Key Features

* **🛰️ Cadastral GIS Satellite Overlay:** Interactive parcel boundaries rendered over high-resolution **Esri World Imagery**, exposing genuine farmland bunds, crops, and rural terrain.
* **⏱️ Section 19 Lapsing Watchdog:** Real-time countdown tracking parcels with `< 45 days` left before statutory lapsing.
* **🤖 Predictive Delay Engine:** **XGBoost Regressor** trained on real-world acquisition variables to project total lifecycle delay days.
* **🔍 Explainable AI (TreeSHAP):** Game-theoretic feature attribution breaking down exact delay drivers (e.g., Court Stay: 78.5%, Succession Gridlock: 21.3%).
* **⚖️ Prescriptive Administrative Mapping:** Automatically maps bottlenecks to authorized nodal officers (SDM, DM, CALA Legal Cell, DFO).
* **📄 One-Click Statutory Order / Memo Drafting:** Instant generation of formal government directives with official dispatch reference numbers, legal clauses, and signature blocks.
* **🎛️ "What-If" Counterfactual Simulator:** Interactive policy simulation allowing authorities to model interventions (e.g., 90% disbursement target) and quantify **Days Saved** live.

---

## 🏗️ System Architecture