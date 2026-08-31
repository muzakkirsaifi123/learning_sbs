# FAQ / Common Gotchas

Recurring "if you hit this error" moments, pulled out of the notes so they're searchable in one place instead of buried mid-page.

## Kubernetes & Operators

??? question "`operator-sdk new` fails to resolve the import path"
    If your project lives outside `$GOPATH/src` (e.g. `~/sbs/self_learning/operator/`), Go 1.13 can't auto-detect the module path. Pass it explicitly:
    ```bash
    operator-sdk new my-operator --repo=github.com/<you>/my-operator
    ```
    See [Kubernetes Operator — Step 2](kubernetes_operators/kubernetes_operator.md#step-2-create-the-operator-project).

??? question "CRD apply fails with `no matches for kind` or a v1beta1 error"
    `operator-sdk generate crds` on the older SDK still emits `apiextensions.k8s.io/v1beta1` CRDs. Kubernetes 1.22+ removed that API version entirely. Rewrite the CRD manifest under `apiVersion: apiextensions.k8s.io/v1` with the schema nested under `versions[].schema.openAPIV3Schema` — see [Step 10](kubernetes_operators/kubernetes_operator.md#step-10-fix-the-crd-for-kubernetes-v135) for a worked example.

??? question "A resource an operator created doesn't get cleaned up when I delete the CR"
    Check whether the child object (ConfigMap, Secret, …) has an owner reference back to the CR. `controllerutil.SetControllerReference(cr, child, scheme)` is what makes Kubernetes garbage-collect it automatically — without that call, deleting the CR leaves orphans behind.

## Helm

??? question "Where do I start with a brand-new chart?"
    `helm create <name>` scaffolds a full chart with sane defaults (Deployment, Service, values.yaml, etc.) — don't hand-write one from scratch. See [Helm](notion/helm.md).

## Keycloak

??? question "How do I check whether SMTP/email is actually configured correctly?"
    Pull the live values straight out of the Helm release rather than guessing from the values file on disk:
    ```bash
    helm get values keycloak -n <namespace> -a | grep -B2 -A20 -i smtp
    ```
    Secrets referenced there are base64-encoded — decode with `echo "<value>" | base64 -d` to see what's actually stored. See [Keycloak](notion/keycloak.md).

## MongoDB Atlas Operator

??? question "Namespace scope vs. application scope — which one am I looking at?"
    **Namespace scope**: one shared Atlas user/password for every app in the namespace — simple, but a rotation or leak affects everyone at once.
    **Application scope**: one dedicated Atlas user per app — more credentials to manage, but a compromised app can only reach its own database.
    Neither is a Kubernetes or Atlas primitive — it's a distinction the mongo-operator's own code defines. See [Mongo Atlas Operator](notion/mongo-atlas-operator.md).

---

Have a recurring gotcha that isn't here yet? Add it directly to this file — it's hand-maintained, not generated.

--8<-- "abbreviations.md"
