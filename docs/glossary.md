---
hide:
  - toc
---

# Glossary

Terms that come up repeatedly across these notes. Hover a highlighted term anywhere on the site for a quick reminder — the same definitions here are wired in as tooltips via `snippets/abbreviations.md`.

CRD
:   **CustomResourceDefinition.** Teaches the Kubernetes API a new resource type (e.g. `Greeter`, `MongoAtlas`) that doesn't exist built-in. Registering one is what makes `kubectl get <kind>` work at all. See [Kubernetes Operator](kubernetes_operators/kubernetes_operator.md#step-4-create-the-api-crd-type-definition).

CR
:   **Custom Resource.** An instance of a CRD — the actual YAML object a user applies (`spec:` you write, `status:` the operator writes back).

Operator
:   A controller plus one or more CRDs, packaged to automate the operational knowledge a human would otherwise apply by hand (create this, wait for that, heal this if it disappears).

Controller
:   The running process that watches for changes to a resource and reconciles reality toward the desired state described in its spec.

Reconcile loop
:   The core function every controller implements: given a changed object, figure out what's true right now, compare it to what's wanted, and take the minimum action to close the gap. Runs on every create/update/delete, not just once.

Owner reference
:   A link from a child object (e.g. a ConfigMap) back to the CR that created it. Kubernetes garbage-collects children automatically when the owner is deleted — this is what makes an operator's cleanup free.

Kubebuilder / Operator SDK
:   Scaffolding tools that generate the boilerplate (registration code, manager wiring, Dockerfile) around a controller so you only have to write the types file and the reconcile logic yourself.

Kubeconfig
:   The file (`~/.kube/config`) that tells `kubectl` and any operator running locally which cluster to talk to and how to authenticate.

Minikube
:   A single-node Kubernetes cluster that runs locally, used throughout these notes for hands-on exercises instead of a real cluster.

Namespace scope (credential isolation)
:   One shared set of Atlas/database credentials for every app in a Kubernetes namespace. Simple, but a leak or rotation affects every app at once. See [Mongo Atlas Operator](notion/mongo-atlas-operator.md).

Application scope (credential isolation)
:   One dedicated set of credentials per app, even within the same namespace. Each app can only reach its own database — more setup, less blast radius.

cp-schema / Schema Registry
:   Short for Confluent Platform's schema-registry component — the Kafka-adjacent service that enforces a consistent message format (Avro/JSON Schema/Protobuf) between producers and consumers. See [Kafka](notion/kafka/kafka.md).

ISR
:   **In-Sync Replicas** — the set of Kafka broker replicas for a partition that are fully caught up with the leader. A partition can only stay available if enough of its ISR set is alive.

Helm chart
:   A packaged, templated set of Kubernetes manifests. `helm create <name>` scaffolds one; `helm install <release> <chart>` deploys it. See [Helm](notion/helm.md).

Helm release
:   A named, installed instance of a chart in a cluster — the thing `helm upgrade`/`helm get values` operate on.

Istio / sidecar
:   A service mesh that injects a proxy container (the sidecar) alongside every app pod to handle traffic routing, mTLS, and observability without app code changes. See [Istio and Mesh](notion/kubernetes/network-security/istio-and-mesh-basic-qa-and-confusion-before-start.md).

Keycloak realm
:   An isolated tenant inside Keycloak — its own users, credentials, and SMTP/email settings, independent of other realms on the same server. See [Keycloak](notion/keycloak.md).
