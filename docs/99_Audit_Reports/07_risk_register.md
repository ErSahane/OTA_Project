# Risk Register

| ID | Risk | Severity | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Payment compliance gaps | Critical | High regulatory and financial exposure | Add PCI-DSS control mapping and payment governance |
| R2 | Privacy compliance gaps | High | Potential GDPR and data handling issues | Define privacy policy, consent, retention, and deletion controls |
| R3 | Weak disaster recovery detail | High | Extended outage and recovery uncertainty | Define RTO/RPO, failover runbooks, and restore tests |
| R4 | Incomplete observability targets | High | Harder to manage incidents and capacity | Add SLOs, dashboards, alert thresholds, and test plans |
| R5 | API security ambiguity | High | Inconsistent authorization and token handling | Formalize gateway security policy and token model |
| R6 | Multi-product schema evolution risk | Medium | Future rework for hotels, buses, visas, insurance | Introduce a product-agnostic reservation abstraction |
| R7 | Localization and SEO gaps | Medium | Reduced global reach and search discoverability | Add localization and SEO strategy |
| R8 | Testing strategy under-specification | Medium | Increased defect risk during implementation | Add complete test pyramid and release validation checklist |
