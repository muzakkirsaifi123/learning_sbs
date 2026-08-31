# Operator lab

`myapp-operator`—Phased Learning Lab (Kubebuilder)
A tiny Kubernetes Operator that watches `MyApp` custom resources and
creates/manages an nginx `Deployment` + `Service` for each one.
Each phase below explains **what every command does**, **what file
you're editing and why**, and **what to leave alone**. Complete a
phase, verify it works, then move to the next.

---

## PHASE 1 — Environment & Project Scaffolding

### Goal
Get Kubebuilder installed, a cluster running, and an empty operator
project skeleton generated — nothing app-specific yet.

### Commands
```bash
go version
kubectl version --client
minikube version
```
**What this does:** sanity-checks your toolchain. Kubebuilder needs
Go 1.21+; `kubectl` and `minikube` just need to exist and respond.
Nothing is installed or changed here — pure verification.
```bash
curl -L -o kubebuilder "https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)"
chmod +x kubebuilder
sudo mv kubebuilder /usr/local/bin/
kubebuilder version
```
**What this does:** downloads the Kubebuilder binary for your OS/arch,
makes it executable, and puts it on your `PATH` so you can call
`kubebuilder` from anywhere. `kubebuilder version` just confirms the
install worked.
```bash
minikube start --driver=docker --cpus=4 --memory=6144
kubectl get nodes
```
**What this does:** boots a local single-node Kubernetes cluster
inside a Docker container. `--cpus`/`--memory` just size the VM so
the control plane has enough headroom. `kubectl get nodes` confirms
the cluster is up and `kubectl` is pointed at it (via
`~/.kube/config`, which minikube writes automatically).
```bash
mkdir myapp-operator && cd myapp-operator
go mod init github.com/yourname/myapp-operator
```
**What this does:** creates your project folder and initializes a Go
module. The module path (`github.com/yourname/myapp-operator`)
becomes the import prefix for every package you write — it does
**not** need to be a real, pushed repo to work locally, but keep it
consistent because you'll reference it later in imports.
```bash
kubebuilder init --domain example.com --repo github.com/yourname/myapp-operator
```
**What this does — the important one:** this is the actual scaffold
step. It generates:
| File/Dir | Purpose |
| --- | --- |
| `main.go` | Entry point — starts the manager process that runs your controllers |
| `PROJECT` | Metadata file Kubebuilder itself reads to know what APIs/controllers exist in this project |
| `Makefile` | All the `make install`, `make run`, `make deploy` targets you'll use later |
| `config/` | Kustomize-based YAML manifests (CRDs, RBAC, manager deployment) |
| `Dockerfile` | Builds your operator into a container image later |
| `go.mod` / `go.sum` | Dependency tracking |

- **`-domain example.com`** matters because it becomes part of your
CRD's API group: `apps.example.com`. This is just a namespacing
convention (like a Java package name) — it doesn't need to be a real
domain you own for a local lab.

### What NOT to touch yet
Don't hand-edit `main.go`, `PROJECT`, or anything in `config/` right
now — they're auto-managed and Phase 2's `create api` command will
extend them correctly. Editing them manually now just risks breaking
the scaffolding logic that later commands depend on.

### ✅ Phase 1 check
```bash
ls
# should show: Dockerfile  Makefile  PROJECT  bin/  cmd/  config/  go.mod  go.sum  hack/  main.go
kubectl get nodes
# should show a Ready node
```

---

## PHASE 2 — Define the `MyApp` API (CRD types)

### Goal
Tell Kubernetes "there is a new resource type called `MyApp`, and
here's its schema." This phase is entirely about **data shape**, not
behavior — no reconcile logic yet.

### Command
```bash
kubebuilder create api --group apps --version v1alpha1 --kind MyApp --resource --controller
```
**What this does:** this single command generates **two** things at
once, because you passed both `--resource` and `--controller`:
1. **The Resource (****`-resource`****)** → creates
`api/v1alpha1/myapp_types.go` — a Go struct that defines what
fields a `MyApp` YAML can have (this becomes your CRD schema) and
registers the type with Kubernetes' type system.
1. **The Controller (****`-controller`****)** → creates
`internal/controller/myapp_controller.go` — a skeleton reconciler
with an empty `Reconcile()` function. This is what Phase 3 fills in.
It also updates `main.go` automatically to wire the new controller
into the manager, and updates `PROJECT` to record that this API now
exists. **You don't need to touch ****`main.go`**** for this** — the
scaffolding does it for you.
- `-group apps --version v1alpha1 --kind MyApp` together define the
full API identity: `apps.example.com/v1alpha1`, `Kind: MyApp`. This
is what you'll write in every `MyApp` YAML's `apiVersion`/`kind`.

### File you edit: `api/v1alpha1/myapp_types.go`
This is the **only** file in this phase you hand-edit. You're
defining `MyAppSpec` (what the user *declares* they want) and
`MyAppStatus` (what the operator *reports back*).
```go
type MyAppSpec struct {
	// +kubebuilder:default="nginx:latest"
	Image string `json:"image,omitempty"`

	// +kubebuilder:default=1
	Replicas int32 `json:"replicas,omitempty"`

	// +kubebuilder:default=80
	Port int32 `json:"port,omitempty"`
}

type MyAppStatus struct {
	AvailableReplicas int32  `json:"availableReplicas,omitempty"`
	Phase             string `json:"phase,omitempty"`
}
```
**Why ****`Spec`**** vs ****`Status`**** are separate structs — this is a core K8s
convention, not a style choice:**
- **`Spec`** = desired state, written by the *user* (`kubectl apply`).
- **`Status`** = observed/actual state, written by the *controller*,
never by the user directly. Kubernetes enforces this split via the
`+kubebuilder:subresource:status` marker (already on the `MyApp`
struct) — it makes `/status` a separate API endpoint so a `kubectl apply` to spec can't accidentally clobber status, and vice versa.
**The ****`// +kubebuilder:...`**** comments are not decoration** — they're
machine-read markers. `controller-gen` (invoked by `make manifests`)
parses these comments to generate the actual CRD YAML schema and
`kubectl` print columns. `+kubebuilder:default="nginx:latest"` means:
if a user creates a `MyApp` without specifying `image`, Kubernetes
itself fills in `nginx:latest` at the API server level — your Go code
never has to handle "what if image is empty."
The `+kubebuilder:printcolumn` markers on the `MyApp` struct control
what `kubectl get myapp` displays as columns (Replicas, Phase) —
purely a UX nicety for `kubectl`.

### What NOT to touch
- `MyAppList` struct — boilerplate required so `kubectl get myapp`
(plural, listing) works. Never needs edits for a simple operator.
- `zz_generated.deepcopy.go` (doesn't exist yet) — this file is
**auto-generated** by the next command; never hand-edit generated
files, your changes get silently overwritten.

### Commands to run after editing
```bash
make generate
make manifests
```
**`make generate`** — runs `controller-gen` to create
`zz_generated.deepcopy.go`. Every Kubernetes API type needs a
`DeepCopyObject()` method (part of the `runtime.Object` interface) so
the client-go machinery can safely clone objects internally. You
never write this by hand — the tool derives it from your struct
fields.
**`make manifests`** — regenerates `config/crd/bases/apps.example.com_myapps.yaml`,
the actual CRD YAML that gets installed into the cluster, translating
your Go struct + markers into an OpenAPI schema Kubernetes
understands.

### ✅ Phase 2 check
```bash
cat config/crd/bases/apps.example.com_myapps.yaml
# should show a schema with image/replicas/port properties under spec
```
No cluster interaction yet — this is all local codegen.

---

## PHASE 3 — The Reconciler (the actual "operator" logic)

### Why this exists — the core concept
Kubernetes controllers work on a **reconcile loop**: something
changes (a `MyApp` is created/updated/deleted, or a `Deployment` it
owns is changed), and your `Reconcile()` function is called with just
a name+namespace. Its entire job is:
> "Given the desired state (`MyApp.Spec`) and whatever currently
exists in the cluster, make reality match desired state."
This is **level-based, not edge-based** — your function doesn't get
told *what changed*, only *that something relevant to this object
might have changed*. So every `Reconcile()` call re-derives the full
desired state from scratch and compares it to what's actually there.
This is why the function is safe to call repeatedly, on a timer, or
after a crash-restart — it's idempotent by design.
**Why you need this instead of just running ****`kubectl apply`**** once:**
a plain manifest apply is "fire and forget" — if someone later
deletes the Deployment by hand, or edits its image, nothing puts it
back. The reconciler runs continuously in the background and
self-heals drift.

### File you edit: `internal/controller/myapp_controller.go`
Everything else generated in Phase 2 stays as-is. This is the file
where the actual behavior lives.
**Step-by-step what the logic does and why:**
```go
myApp := &myappv1alpha1.MyApp{}
if err := r.Get(ctx, req.NamespacedName, myApp); err != nil {
    if apierrors.IsNotFound(err) {
        return ctrl.Result{}, nil
    }
    return ctrl.Result{}, err
}
```
Fetch the `MyApp` object that triggered this reconcile. `IsNotFound`
means the object was deleted between the event firing and this code
running — that's expected and fine, not an error: you just return
and do nothing (cleanup of owned resources happens automatically —
see the owner reference explanation below).
```go
deployment := buildDeployment(myApp)
if err := controllerutil.SetControllerReference(myApp, deployment, r.Scheme); err != nil {
    return ctrl.Result{}, err
}
```
`buildDeployment()` is a plain Go function (not part of the
Kubernetes API) that you write to construct the `Deployment` object
you *want* to exist, based on the `MyApp`'s spec fields.
`SetControllerReference` is critical: it stamps an `ownerReference`
on the Deployment pointing back to the `MyApp`. **This is what makes
Kubernetes' built-in garbage collector delete the Deployment and
Service automatically when the ****`MyApp`**** is deleted** — you don't write
any manual delete logic for that case. It's also what makes
`Owns(&appsv1.Deployment{})` in `SetupWithManager` (bottom of the
file) work: it tells the controller "also re-trigger my Reconcile if
an owned Deployment changes," which is how drift-correction (Phase 6
test) works.
```go
foundDeploy := &appsv1.Deployment{}
err := r.Get(ctx, types.NamespacedName{...}, foundDeploy)
if err != nil && apierrors.IsNotFound(err) {
    r.Create(ctx, deployment)
} else if err != nil {
    return ctrl.Result{}, err
} else {
    // compare & update if drifted
}
```
This is the **create-or-update pattern**, the heart of every
reconciler:
1. Try to fetch what currently exists.
1. If it doesn't exist → create it.
1. If it exists but differs from desired state (replicas/image
changed) → update just those fields.
1. If it exists and matches → do nothing (this is why the function is
safe to call every few seconds without causing API churn).
The Service block right below repeats the exact same
create-or-update pattern for the `Service` object.
```go
myApp.Status.AvailableReplicas = foundDeploy.Status.AvailableReplicas
myApp.Status.Phase = "Running"
r.Status().Update(ctx, myApp)
```
Writes back to `MyApp.Status` (via the separate `/status`
subresource, per Phase 2's note) so `kubectl get myapp` shows live
info without the user needing to inspect the Deployment separately.
```go
func (r *MyAppReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&myappv1alpha1.MyApp{}).
		Owns(&appsv1.Deployment{}).
		Owns(&corev1.Service{}).
		Complete(r)
}
```
This wires up **what events trigger ****`Reconcile()`**:
- `For(&MyApp{})` → any create/update/delete of a `MyApp`.
- `Owns(&Deployment{})` / `Owns(&Service{})` → any change to a
Deployment/Service that has this controller's owner reference on
it (set earlier via `SetControllerReference`). This is what makes
the "delete the Deployment by hand, operator recreates it" test in
Phase 6 actually work.

### The `// +kubebuilder:rbac:...` markers above `Reconcile()`
```go
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
```
These aren't runtime code — `controller-gen` reads them to generate
`config/rbac/role.yaml`. They declare the exact permissions your
operator's ServiceAccount needs. Miss one (e.g. forget `create` on
`services`) and the operator will compile fine but fail at runtime
with a Kubernetes `Forbidden` error the moment it tries that
operation in-cluster (this matters once you deploy in-cluster in
Phase 5 — `make run` locally uses your own kubeconfig permissions, so
RBAC bugs can hide until then).

### What NOT to touch
- Don't remove the `+kubebuilder:rbac` markers even if `make run`
works without them locally — they only bite you later in Phase 5
when deployed in-cluster under the generated ServiceAccount.
- Don't add business logic to `main.go` — it stays as scaffolding
that just registers your reconciler with the manager.

### ✅ Phase 3 check
```bash
go build ./...
```
Should compile with no errors. This phase is code-only — nothing
touches the cluster yet.

---

## PHASE 4 — Install CRD & Run the Operator Locally

### Goal
Get your reconcile loop actually running against the real (mini)
cluster, watching for `MyApp` objects.

### Commands
```bash
go mod tidy
```
**What this does:** resolves and downloads any Go module dependencies
your edited files now import (e.g. `k8s.io/apimachinery/...`) that
weren't in `go.sum` yet, and removes unused ones.
```bash
make manifests generate
```
Re-run from Phase 2/3 — you already know what these do. Run again
here because you may have added new RBAC markers in Phase 3 that need
to flow into `config/rbac/role.yaml`.
```bash
make install
```
**What this does:** runs `kubectl apply -f config/crd/bases/...`
under the hood — this registers the `MyApp` CRD with your Minikube
cluster's API server. After this, the API server *understands*`apiVersion: apps.example.com/v1alpha1, kind: MyApp` as a valid
resource type — but nothing is watching it yet.
```bash
kubectl get crds | grep myapps
```
Confirms the CRD is registered.
```bash
make run
```
**What this does:** compiles and runs your operator's `main.go`**directly on your machine** (not as a container in the cluster). It
connects to the cluster using your local `~/.kube/config` (the same
credentials `kubectl` uses), and starts the manager loop —
`Reconcile()` will now fire for any `MyApp` events. Leave this running
in its own terminal; its stdout is your live controller log.

### Why "run locally" before "deploy in-cluster"
This is the standard operator dev loop: local `make run` gives you
fast iteration (edit Go code → `Ctrl+C` → `make run` again, no image
build/push needed) while still talking to a real cluster. You only
containerize and `make deploy` (Phase 5/optional) once the logic is
proven.

### ✅ Phase 4 check
`make run`'s terminal should show manager startup logs ending in
something like `Starting workers` with no error/panic. Leave it
running for Phase 5.

---

## PHASE 5 — Apply a Sample `MyApp` and Watch It Get Reconciled

### Goal
Prove the whole loop end-to-end: CR created → Deployment+Service
created → pods running.

### File: `config/samples/apps_v1alpha1_myapp.yaml`
This was scaffolded empty-ish in Phase 2; fill in real values:
```yaml
apiVersion: apps.example.com/v1alpha1
kind: MyApp
metadata:
  name: myapp-sample
spec:
  image: nginx:1.27
  replicas: 2
  port: 80
```
This is the only file you touch in this phase — it's a sample
instance of your CRD, not scaffolding.

### Commands (run in a **second** terminal — keep `make run` alive in the first)
```bash
kubectl apply -f config/samples/apps_v1alpha1_myapp.yaml
```
Creates the `MyApp` object in the cluster. This is the event that
triggers your first real `Reconcile()` call.
```bash
kubectl get myapp
```
Lists it — you should see the `Replicas`/`Phase` print columns from
Phase 2's markers, e.g. `myapp-sample   2   Running`.
```bash
kubectl get deploy,svc -l app=myapp-sample
```
Confirms `buildDeployment()`/`buildService()` from Phase 3 actually
created real objects, labeled `app=myapp-sample` as set in your Go
code.
```bash
kubectl describe myapp myapp-sample
```
Shows full spec+status, and near the bottom, `Events` — any errors
your reconciler hit (e.g. RBAC denials) surface here too if you used
an event recorder; otherwise check the `make run` terminal logs.

### ✅ Phase 5 check
- `make run` terminal shows `Creating Deployment` then `Creating Service` log lines.
- `kubectl get pods -l app=myapp-sample` shows 2 nginx pods reaching `Running`.

---

## PHASE 6 — Testing: Drift Correction, Scaling, Cleanup

### Goal
Verify the reconciler actually *behaves* like an operator (self-heals
and reacts to spec changes), not just that it ran once.

### Test 1 — Spec change propagates
```bash
kubectl patch myapp myapp-sample --type=merge -p '{"spec":{"replicas":3}}'
kubectl get deploy myapp-sample -w
```
**What you're checking:** editing `MyApp.spec.replicas` should
trigger `Reconcile()` (via the `For(&MyApp{})` watch from Phase 3),
which re-runs `buildDeployment()`, sees `*foundDeploy.Spec.Replicas != myApp.Spec.Replicas`, and calls `Update()`. The `-w` watches live
— you should see the Deployment's replica count change from 2→3
within a second or two, and a 3rd pod appear.
**If it doesn't change:** check the `make run` logs — likely means
the drift-comparison `if` block in `Reconcile()` isn't matching, or
the patch didn't apply (check `kubectl get myapp -o yaml`).

### Test 2 — Self-healing on manual deletion
```bash
kubectl delete deploy myapp-sample
kubectl get deploy -w
```
**What you're checking:** this proves the `Owns(&appsv1.Deployment{})`
watch from Phase 3 works — deleting an *owned* resource should
re-trigger `Reconcile()` for the owning `MyApp`, which finds the
Deployment missing (`IsNotFound`) and recreates it. You should see it
reappear within a couple seconds without you touching the `MyApp`
object at all. **This is the single best test to confirm you built a
real operator and not just a one-shot apply script.**

### Test 3 — Status accuracy
```bash
kubectl get myapp myapp-sample -o jsonpath='{.status}'
```
Should reflect the current `availableReplicas` matching real pod
count, confirming the `Status().Update()` call in `Reconcile()` is
wired correctly.

### Cleanup
```bash
kubectl delete -f config/samples/apps_v1alpha1_myapp.yaml
kubectl get deploy,svc -l app=myapp-sample
# should return nothing — proves owner-reference garbage collection worked
make uninstall   # removes the CRD from the cluster entirely
```
Deleting the `MyApp` should cascade-delete its Deployment+Service
automatically (owner references, Phase 3) — no code in your
reconciler handles deletion explicitly, and that's intentional; it's
Kubernetes' built-in garbage collector doing the work.

### Stop your cluster
```bash
# Ctrl+C in the make run terminal first
minikube stop
```

---

## Summary map: file → phase → purpose
| File | Phase | Why it exists |
| --- | --- | --- |
| `main.go` | 1 (auto) | Boots the manager, registers controllers — rarely hand-edited |
| `api/v1alpha1/myapp_types.go` | 2 | Defines the CRD schema (Spec/Status) |
| `config/crd/bases/*.yaml` | 2 (generated) | The actual CRD installed into the cluster |
| `internal/controller/myapp_controller.go` | 3 | The reconcile loop — all the behavior |
| `config/rbac/role.yaml` | 3 (generated) | Permissions derived from `+kubebuilder:rbac` markers |
| `config/samples/*.yaml` | 5 | A sample CR instance you apply to test |

If you want, next step could be adding a **finalizer** (for cleanup
logic that must run *before* deletion, unlike the automatic
owner-reference GC used here) or wiring up `envtest` for proper Go
unit tests on the reconciler instead of manual `kubectl` testing.
