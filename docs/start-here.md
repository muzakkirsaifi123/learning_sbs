# Start Here

The nav on the left is organized by where notes live in Notion, not by what order to read them in. This page is the reading order — a suggested path through what's actually here right now.

## 1. Kubernetes fundamentals

Start with the operator pattern itself, hands-on, before anything Atlas- or Kafka-specific:

- [Kubernetes Operator — full walkthrough](kubernetes_operators/kubernetes_operator.md) — builds a toy "Greeter" operator step by step, then maps every file back to how the real mongo-operator is structured. The longest, most complete page on the site — everything else assumes you've been through this.
- [Kubernetes Operator (Notion notes)](notion/kubernetes/kubernetes-operator.md) and the accompanying [operator lab](notion/kubernetes/kubernetes-operator/operator-lab.md)
- [k8sgpt](notion/kubernetes/k8sgpt.md)

## 2. Networking & security

- [Network - Security](notion/kubernetes/network-security.md)
- [Istio and Mesh — basic Q&A](notion/kubernetes/network-security/istio-and-mesh-basic-qa-and-confusion-before-start.md)
- [Istio practice lab](notion/kubernetes/network-security/istio-practice-lab-theory-.md)

## 3. Package management

- [Helm](notion/kubernetes/helm.md), [Helm upgrade](notion/kubernetes/helm/helm-upgrade.md), [using the Helm plugin](notion/kubernetes/helm/how-to-use-the-helm-plugin.md)

## 4. Kafka

- [Kafka & cp-schema](notion/kafka/kafka.md)

## 5. Identity

- [Keycloak](notion/keycloak.md)

## 6. Putting it together — the MongoDB Atlas Operator

Once the operator pattern and the surrounding tooling both make sense, this is where they meet a real external API instead of a toy ConfigMap:

- [Mongo Atlas Operator](notion/kubernetes/mongo-atlas-operator.md) — credential isolation models (namespace vs. application scope)
- [Radar → Mongo Atlas flow](notion/radar/radar-mongoatlas-flow.md) — the deepest, most complete integration write-up on the site

---

Not sure where something fits, or looking for a specific term? Check the [Glossary](glossary.md) or the [Tags](tags.md) index. Recently touched pages are on [Recently Updated](recently-updated.md).

--8<-- "abbreviations.md"
