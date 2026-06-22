# Kubernetes Operator Learning Notes

## Table of Contents

1. [Exercise: Build a Greeter Operator (Step by Step)](#part-1-exercise-build-a-greeter-operator)
2. [What This Demo Does and Why](#part-2-what-this-demo-does-and-why)
3. [Q&A: Boilerplate vs Your Code](#part-3-qa-boilerplate-vs-your-code)
4. [Deep Explanation: What Happens on Your Machine](#part-4-deep-explanation-what-happens-on-your-machine)
5. [The 2 Files You Edit (Go Explained for Beginners)](#part-5-the-2-files-you-edit)
6. [How It Scales (Minimum Files Per CRD)](#part-6-how-it-scales)

---

## Part 1: Exercise — Build a Greeter Operator

### Your Environment (confirmed)

- Go: 1.13.15 ✓
- Operator SDK: v0.15.2 ✓
- Minikube: v1.38.1 (running, Kubernetes v1.35.1) ✓
- Shell: zsh
- Working path: `/home/saifi/sbs/self_learning/operator/`

---

### Step 1: Clean up any previous attempts

```bash
rm -rf /home/saifi/sbs/self_learning/operator/greeter-operator
```

**What happens:** Removes any leftover project folder.

---

### Step 2: Create the operator project

```bash
cd /home/saifi/sbs/self_learning/operator/
operator-sdk new greeter-operator --repo=github.com/saifi/greeter-operator
```

**Why `--repo=...`:** Your path (`/home/saifi/sbs/...`) is outside `$GOPATH/src`. Go 1.13 can't auto-detect the import path, so `--repo` tells it explicitly.

**What happens:**
- Creates a folder `greeter-operator/` with the full operator structure
- Downloads all dependencies (controller-runtime, Kubernetes client libraries, etc.)
- Runs `go build` at the end to validate

**Expected:** All files created, no error at the end.

**If you get a validation error at the end:** The project files are still created. Just continue — we'll build manually later.

---

### Step 3: Enter the project

```bash
cd greeter-operator
```

Verify:
```bash
ls
```

**Expected:**
```
build  cmd  deploy  go.mod  go.sum  pkg  tools.go  version
```

This is the same layout as the mongo-operator.

---

### Step 4: Create the API (CRD type definition)

```bash
operator-sdk add api --api-version=demo.example.com/v1 --kind=Greeter
```

**What each flag means:**
- `--api-version=demo.example.com/v1` → group is `demo.example.com`, version is `v1`
- `--kind=Greeter` → the resource type name

**What happens:**
- Creates `pkg/apis/demo/v1/greeter_types.go` — Go struct defining what a Greeter CR looks like
- Creates `pkg/apis/demo/v1/zz_generated.deepcopy.go` — auto-generated code Kubernetes requires
- Creates `deploy/crds/demo.example.com_greeters_crd.yaml` — CRD YAML for the cluster
- Creates `deploy/crds/demo.example.com_v1_greeter_cr.yaml` — sample CR
- Updates `pkg/apis/` registration files

**Comparison to mongo-operator:**

| Created file | Mongo-operator equivalent |
|---|---|
| `greeter_types.go` | `mongoatlas_types.go` |
| `demo.example.com_greeters_crd.yaml` | `db.sbcp.io_mongoatlas_crd.yaml` |

---

### Step 5: Edit the CRD types

Open `pkg/apis/demo/v1/greeter_types.go` in your editor (nano/vim) and replace the entire content with:

```go
package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// GreeterSpec defines the desired state of Greeter
// This is what the USER writes in their CR YAML under "spec:"
type GreeterSpec struct {
    // Name is the person to greet
    // User writes: spec.name: "Muzakkir" → this becomes greeter.Spec.Name
    Name string `json:"name"`
}

// GreeterStatus defines the observed state of Greeter
// This is what the OPERATOR fills in after doing its work
// The user never writes this — the controller updates it
type GreeterStatus struct {
    // Message shows what greeting was generated
    Message string `json:"message,omitempty"`
    // Ready indicates the ConfigMap was successfully created
    Ready bool `json:"ready,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// Greeter is the Schema for the greeters API
// +kubebuilder:subresource:status
// +kubebuilder:resource:path=greeters,scope=Namespaced
type Greeter struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   GreeterSpec   `json:"spec,omitempty"`
    Status GreeterStatus `json:"status,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// GreeterList contains a list of Greeter
type GreeterList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []Greeter `json:"items"`
}

func init() {
    SchemeBuilder.Register(&Greeter{}, &GreeterList{})
}
```

**What each part means:**

| Code | Purpose |
|------|---------|
| `GreeterSpec` | User input — the `spec:` section in the CR YAML |
| `GreeterStatus` | Operator output — the `status:` section (controller fills this) |
| `// +k8s:deepcopy-gen:...` | Tells code generator to create DeepCopy methods (Kubernetes requires all objects to be copyable) |
| `// +kubebuilder:subresource:status` | Enables separate status updates (spec and status can be updated independently) |
| `// +kubebuilder:resource:path=greeters,scope=Namespaced` | REST path is `/greeters`, CRs live inside namespaces |
| `SchemeBuilder.Register(...)` | Registers type with Kubernetes so it can serialize/deserialize |

---

### Step 6: Regenerate code

```bash
operator-sdk generate k8s
```

**What happens:** Reads your updated `greeter_types.go` and regenerates `zz_generated.deepcopy.go` with proper `DeepCopyObject()` methods for your new struct fields.

```bash
operator-sdk generate crds
```

**What happens:** Reads the Go struct + annotations and regenerates `deploy/crds/demo.example.com_greeters_crd.yaml` to include `spec.name` as a required field in the schema.

---

### Step 7: Create the Controller

```bash
operator-sdk add controller --api-version=demo.example.com/v1 --kind=Greeter
```

**What happens:**
- Creates `pkg/controller/greeter/greeter_controller.go` — where the reconciliation logic goes
- Creates `pkg/controller/add_greeter.go` — registers this controller with the manager at startup

**Comparison to mongo-operator:**

| Created file | Mongo-operator equivalent |
|---|---|
| `greeter_controller.go` | `mongoatlas_controller.go` |
| `add_greeter.go` | `add_mongoatlas.go` |

---

### Step 8: Write the controller logic

Open `pkg/controller/greeter/greeter_controller.go` in your editor and replace the entire content with:

```go
package greeter

import (
    "context"
    "fmt"

    demov1 "github.com/saifi/greeter-operator/pkg/apis/demo/v1"

    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/controller"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    "sigs.k8s.io/controller-runtime/pkg/handler"
    logf "sigs.k8s.io/controller-runtime/pkg/log"
    "sigs.k8s.io/controller-runtime/pkg/manager"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"
    "sigs.k8s.io/controller-runtime/pkg/source"
)

var log = logf.Log.WithName("controller_greeter")

// ═══════════════════════════════════════════════════════
// REGISTRATION — Runs once at startup
// ═══════════════════════════════════════════════════════

// Add creates the controller and adds it to the Manager.
// Called at startup from pkg/controller/controller.go
func Add(mgr manager.Manager) error {
    return add(mgr, newReconciler(mgr))
}

func newReconciler(mgr manager.Manager) reconcile.Reconciler {
    return &ReconcileGreeter{client: mgr.GetClient(), scheme: mgr.GetScheme()}
}

func add(mgr manager.Manager, r reconcile.Reconciler) error {
    c, err := controller.New("greeter-controller", mgr, controller.Options{Reconciler: r})
    if err != nil {
        return err
    }

    // WATCH #1: Watch for Greeter CRs
    // When kubectl apply/delete is used on a Greeter, trigger Reconcile()
    err = c.Watch(&source.Kind{Type: &demov1.Greeter{}}, &handler.EnqueueRequestForObject{})
    if err != nil {
        return err
    }

    // WATCH #2: Watch ConfigMaps owned by a Greeter
    // If someone deletes our ConfigMap, trigger Reconcile() to recreate it
    err = c.Watch(&source.Kind{Type: &corev1.ConfigMap{}}, &handler.EnqueueRequestForOwner{
        IsController: true,
        OwnerType:    &demov1.Greeter{},
    })
    if err != nil {
        return err
    }

    return nil
}

// ═══════════════════════════════════════════════════════
// RECONCILER — Runs every time something changes
// ═══════════════════════════════════════════════════════

type ReconcileGreeter struct {
    client client.Client
    scheme *runtime.Scheme
}

// Reconcile is the MAIN FUNCTION.
// Called when: CR created, CR updated, CR deleted, owned ConfigMap changed
// Goal: Ensure a ConfigMap with a greeting exists for every Greeter CR
func (r *ReconcileGreeter) Reconcile(request reconcile.Request) (reconcile.Result, error) {
    reqLogger := log.WithValues("Namespace", request.Namespace, "Name", request.Name)
    reqLogger.Info("Reconciling Greeter")

    // STEP 1: Get the Greeter CR that triggered this
    greeter := &demov1.Greeter{}
    err := r.client.Get(context.TODO(), request.NamespacedName, greeter)
    if err != nil {
        if errors.IsNotFound(err) {
            reqLogger.Info("Greeter deleted. ConfigMap will be garbage collected.")
            return reconcile.Result{}, nil
        }
        return reconcile.Result{}, err
    }

    // STEP 2: Check if our ConfigMap exists
    configMapName := fmt.Sprintf("greeting-%s", greeter.Name)
    found := &corev1.ConfigMap{}
    err = r.client.Get(context.TODO(), types.NamespacedName{
        Name: configMapName, Namespace: greeter.Namespace,
    }, found)

    if err != nil && errors.IsNotFound(err) {
        // STEP 3: ConfigMap missing — CREATE it
        cm := &corev1.ConfigMap{
            ObjectMeta: metav1.ObjectMeta{
                Name:      configMapName,
                Namespace: greeter.Namespace,
            },
            Data: map[string]string{
                "message": fmt.Sprintf("Hello, %s! Welcome to Kubernetes!", greeter.Spec.Name),
            },
        }

        // Set owner reference: Greeter CR owns this ConfigMap
        // When Greeter is deleted → ConfigMap auto-deletes
        controllerutil.SetControllerReference(greeter, cm, r.scheme)

        reqLogger.Info("Creating ConfigMap", "name", configMapName)
        err = r.client.Create(context.TODO(), cm)
        if err != nil {
            return reconcile.Result{}, err
        }
        reqLogger.Info("ConfigMap created!")

    } else if err != nil {
        return reconcile.Result{}, err
    } else {
        reqLogger.Info("ConfigMap already exists", "name", configMapName)
    }

    // STEP 4: Update CR status
    greeter.Status.Message = fmt.Sprintf("Greeting created for %s", greeter.Spec.Name)
    greeter.Status.Ready = true
    err = r.client.Status().Update(context.TODO(), greeter)
    if err != nil {
        reqLogger.Error(err, "Failed to update status")
        return reconcile.Result{}, err
    }

    reqLogger.Info("Done!")
    return reconcile.Result{}, nil
}
```

---

### Step 9: Build

```bash
go build ./...
```

**Expected:** No output = success.

If you get errors, run:
```bash
go mod tidy
go build ./...
```

---

### Step 10: Fix the CRD for Kubernetes v1.35

Your Minikube runs Kubernetes v1.35 which doesn't support `apiextensions.k8s.io/v1beta1`. Replace the generated CRD file `deploy/crds/demo.example.com_greeters_crd.yaml` with:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: greeters.demo.example.com
spec:
  group: demo.example.com
  names:
    kind: Greeter
    listKind: GreeterList
    plural: greeters
    singular: greeter
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              name:
                type: string
            required:
            - name
          status:
            type: object
            properties:
              message:
                type: string
              ready:
                type: boolean
    subresources:
      status: {}
```

**Why:** The old SDK generates `v1beta1` CRDs, but Kubernetes 1.22+ removed that. We manually use `v1`.

---

### Step 11: Update the sample CR

Edit `deploy/crds/demo.example.com_v1_greeter_cr.yaml`:

```yaml
apiVersion: demo.example.com/v1
kind: Greeter
metadata:
  name: my-greeter
  namespace: default
spec:
  name: "Muzakkir"
```

---

### Step 12: Deploy the CRD to Minikube

```bash
kubectl apply -f deploy/crds/demo.example.com_greeters_crd.yaml
```

**What happens:** Registers the `Greeter` resource type in the cluster.

**Expected:** `customresourcedefinition.apiextensions.k8s.io/greeters.demo.example.com created`

Verify:
```bash
kubectl get crd greeters.demo.example.com
```

---

### Step 13: Run the operator locally

```bash
operator-sdk run --local --namespace=default
```

If that doesn't work, use:
```bash
operator-sdk up local --namespace=default
```

Or directly:
```bash
go run cmd/manager/main.go
```

**What happens:**
- Compiles and runs the operator on your machine
- Connects to Minikube via `~/.kube/config`
- Starts watching for Greeter CRs and owned ConfigMaps

**Expected logs:**
```
{"msg":"Starting the Cmd."}
{"msg":"Starting Controller","controller":"greeter-controller"}
{"msg":"Starting workers","controller":"greeter-controller","worker count":1}
```

**Keep this terminal open.**

---

### Step 14: Apply the sample CR (NEW terminal)

```bash
cd /home/saifi/sbs/self_learning/operator/greeter-operator
kubectl apply -f deploy/crds/demo.example.com_v1_greeter_cr.yaml
```

**Expected:** `greeter.demo.example.com/my-greeter created`

---

### Step 15: Check operator logs

Go back to the operator terminal. You should see:

```
{"msg":"Reconciling Greeter","Namespace":"default","Name":"my-greeter"}
{"msg":"Creating ConfigMap","name":"greeting-my-greeter"}
{"msg":"ConfigMap created!"}
{"msg":"Done!"}
```

---

### Step 16: Verify

```bash
# Check ConfigMap
kubectl get configmap greeting-my-greeter -o yaml
```
**Expected:** `message: "Hello, Muzakkir! Welcome to Kubernetes!"`

```bash
# Check CR status
kubectl get greeter my-greeter -o yaml
```
**Expected:** `status.message: "Greeting created for Muzakkir"` and `status.ready: true`

---

### Step 17: Test self-healing

```bash
kubectl delete configmap greeting-my-greeter
```

**What happens:** Operator detects the owned ConfigMap was deleted → re-reconciles → recreates it.

Verify:
```bash
kubectl get configmap greeting-my-greeter
```
**Expected:** It's back.

---

### Step 18: Test garbage collection

```bash
kubectl delete greeter my-greeter
kubectl get configmap greeting-my-greeter
```

**Expected:** Both CR and ConfigMap are gone (owner reference auto-cleanup).

---

### Step 19: Clean up

```bash
# Ctrl+C in operator terminal
kubectl delete crd greeters.demo.example.com
minikube stop  # optional
```

---

---

## Part 2: What This Demo Does and Why

### What is this "Greeter Operator" demo?

It's a **learning exercise** that shows you how a Kubernetes operator works by building the simplest possible one. Instead of talking to MongoDB Atlas (which needs credentials), it creates ConfigMaps (which need nothing).

### The Story (What's Happening)

Imagine you're Kubernetes. Normally you know about Pods, Deployments, Services — built-in stuff. But you **don't** know what a "Greeter" is.

This demo teaches Kubernetes a **new concept** (Greeter) and gives it a **robot** (operator) that knows what to do when someone asks for a Greeter.

### Step by step — What happened and why

**Step 2: `operator-sdk new greeter-operator`**
- **What:** Creates a blank operator project — all the folders and boilerplate code.
- **Why:** Same as creating a new empty project in any language. You need the skeleton before you write logic.
- **Result:** An empty operator that starts up but does nothing because it has no CRDs or controllers yet.

**Step 4: `operator-sdk add api`**
- **What:** Tells the operator "you will manage a resource type called Greeter."
- **Why:** Kubernetes only understands built-in types (Pod, Service, etc.). You need to teach it a new type. This step defines what a Greeter looks like as a Go struct.
- **Analogy:** You're creating a new form template. Right now the form is blank — you haven't decided what fields it has yet.

**Step 5: Editing `greeter_types.go`**
- **What:** You define the fields: `spec.name` (user fills this in) and `status.message` (operator fills this in)
- **Why:** Without fields, the CR is useless. This is like designing a form with actual questions on it.
- **Analogy in mongo-operator:** Instead of `spec.name`, it's `spec.database`. Instead of `status.message`, it's `status.created`.

**Step 6: `operator-sdk generate k8s` and `generate crds`**
- **What:** Auto-generates helper code and the CRD YAML from your Go structs.
- **Why:** Kubernetes needs a YAML definition (CRD) to register the type. The code generator creates it automatically from your Go code so you don't write it by hand.

**Step 7: `operator-sdk add controller`**
- **What:** Creates the controller file — the "brain" of the operator.
- **Why:** A CRD alone just stores data. You need a controller that watches for CRs and reacts to them. Without this, Kubernetes accepts Greeter CRs but nothing happens.

**Step 8: Writing the controller logic (`Reconcile()`)**
- **What you wrote:** The actual decision-making code:
  1. "Someone created a Greeter CR? Let me check."
  2. "Does a greeting ConfigMap already exist? No? Let me create one."
  3. "Let me update the CR's status to say I'm done."
- **Why:** This is the whole point of an operator — automating manual work. Without this code, the operator starts but does nothing.

**Mongo-operator comparison:**

| Our code | Mongo-operator |
|----------|---------------|
| "Does ConfigMap exist?" | "Does database exist in Atlas?" |
| "Create ConfigMap with greeting" | "Create database via Atlas API" |
| "Update CR status" | "Update CR status" |

**Step 10: Fixing the CRD YAML**
- **What:** Changed `v1beta1` → `v1` in the CRD file.
- **Why:** The old SDK generates outdated YAML format. Your Minikube (Kubernetes 1.35) only accepts the new format. This is just a version compatibility fix.

**Step 12: `kubectl apply -f ...crd.yaml`**
- **What:** Installs the CRD into the cluster.
- **Why:** Now Kubernetes knows "Greeter is a valid resource type." Before this, if you tried `kubectl get greeter`, it would say "unknown resource."
- **After this:** Kubernetes accepts Greeter CRs but nothing processes them yet (no operator running).

**Step 13: `operator-sdk run --local`**
- **What:** Starts the operator on your machine, connected to Minikube.
- **Why:** The operator needs to be running to watch for CRs. It's like starting a service — it sits there waiting for work.
- **What it does internally:**
  1. Connects to Kubernetes API via your kubeconfig
  2. Says "tell me whenever a Greeter CR is created/updated/deleted"
  3. Waits...

**Step 14: `kubectl apply -f ...cr.yaml`**
- **What:** Creates a Greeter CR with `spec.name: "Muzakkir"`.
- **Why:** This is the **trigger**. The operator was waiting for this moment.
- **What happens behind the scenes:**
  1. Kubernetes API receives the CR
  2. Kubernetes stores it
  3. Kubernetes notifies the operator "hey, a new Greeter appeared"
  4. Operator's `Reconcile()` function fires
  5. Reconcile creates the ConfigMap and updates status

**Step 17: Self-healing test**
- **What:** You deleted the ConfigMap manually. The operator detected it and recreated it.
- **Why this matters:** In the real world, things break. Someone accidentally deletes a secret, a resource gets corrupted. The operator continuously ensures the desired state matches reality. This is the core value of an operator — **self-healing automation**.
- **Mongo-operator equivalent:** If someone deletes the credentials secret, the operator recreates it.

**Step 18: Garbage collection test**
- **What:** You deleted the Greeter CR, and the ConfigMap auto-deleted too.
- **Why:** The owner reference says "this ConfigMap belongs to this Greeter." When the parent is deleted, Kubernetes cleans up the children. This prevents orphaned resources cluttering your cluster.

### The Big Picture

```
YOU (user)                    KUBERNETES                     OPERATOR
    │                              │                            │
    │ kubectl apply greeter.yaml   │                            │
    │─────────────────────────────>│                            │
    │                              │  "New Greeter appeared"    │
    │                              │───────────────────────────>│
    │                              │                            │
    │                              │                            │ Check: ConfigMap exists?
    │                              │                            │ No → Create it
    │                              │  Create ConfigMap          │
    │                              │<───────────────────────────│
    │                              │                            │
    │                              │  Update CR status          │
    │                              │<───────────────────────────│
    │                              │                            │
    │ kubectl get configmap        │                            │
    │─────────────────────────────>│                            │
    │ "Hello, Muzakkir!"           │                            │
    │<─────────────────────────────│                            │
```

### Why this matters for the mongo-operator

Everything you saw here is **exactly** what the mongo-operator does:

| This demo | Mongo-operator | Concept |
|-----------|---------------|---------|
| `Greeter` CR | `MongoAtlas` CR | User's request |
| `spec.name: "Muzakkir"` | `spec.database: "dev_myapp"` | What user wants |
| Creates ConfigMap | Creates database in Atlas | What operator does |
| Updates `status.ready: true` | Updates `status.created: "true"` | Confirms it's done |
| Self-healing (recreates ConfigMap) | Self-healing (recreates users/secrets) | Ensures desired state |
| Owner reference (auto-delete) | Handles cleanup on CR deletion | No orphans |

The only difference is the mongo-operator talks to an external API (MongoDB Atlas) instead of creating local ConfigMaps. The pattern, structure, and flow are identical.

---

## Part 3: Q&A — Boilerplate vs Your Code

### What is "boilerplate code"?

Boilerplate = code that **you don't write** — the SDK generates it for you. It's the boring, repetitive setup code that every operator needs but has nothing to do with your specific logic.

**What SDK gives you (boilerplate):**
- `cmd/manager/main.go` — startup code
- `pkg/apis/apis.go` — registration code
- `pkg/controller/controller.go` — controller registration
- `build/Dockerfile` — container setup
- `deploy/*.yaml` — Kubernetes manifests
- `go.mod`, `tools.go` — dependency management

**What YOU write (your logic):**
- `pkg/apis/demo/v1/greeter_types.go` — what fields your CR has
- `pkg/controller/greeter/greeter_controller.go` — what to do when CR appears

### Why do you need `greeter_types.go`?

This file teaches Go **what a Greeter CR looks like**. When someone applies this YAML:

```yaml
spec:
  name: "Muzakkir"
```

Go needs to know: "Ok, `name` is a string field inside `spec`." Without `greeter_types.go`, Go has no idea how to read the YAML.

- **File path:** `pkg/apis/demo/v1/greeter_types.go`
- **Who creates it:** `operator-sdk add api` creates a skeleton. **You edit it** to add your fields.

### Step 5 explained (what you actually DO)

- **What the SDK gave you:** A nearly empty `greeter_types.go` with placeholder comments like "INSERT ADDITIONAL SPEC FIELDS HERE"
- **What YOU do:** Open that file and replace the placeholder with YOUR fields (`Name string`). This is YOUR code — you're deciding what your CR should contain.

### Step 6 explained (what it generates and WHERE)

After you edit `greeter_types.go`, you run two commands:

**`operator-sdk generate k8s`**
- Reads: `pkg/apis/demo/v1/greeter_types.go` (your file)
- Creates: `pkg/apis/demo/v1/zz_generated.deepcopy.go` (auto-generated, never edit this)
- Why: Kubernetes requires every object to have a `DeepCopy()` method. Writing it by hand is tedious, so the tool generates it.

**`operator-sdk generate crds`**
- Reads: `pkg/apis/demo/v1/greeter_types.go` (your file)
- Creates/Updates: `deploy/crds/demo.example.com_greeters_crd.yaml`
- Why: Turns your Go struct into a YAML CRD that Kubernetes understands

**You write NO code in this step.** You just run the commands and they auto-generate files.

### Step 7 explained (what it generates)

`operator-sdk add controller` generates TWO files:
1. `pkg/controller/greeter/greeter_controller.go` — a **skeleton** with placeholder Reconcile logic
2. `pkg/controller/add_greeter.go` — registration code (boilerplate, don't touch)

The skeleton it gives you has dummy code like "check if a Pod exists, create one if not." It's a template. **You must replace it** with YOUR logic in Step 8.

### Step 8 explained (what YOU write and where)

- **File:** `pkg/controller/greeter/greeter_controller.go`
- **What SDK gave you:** A template with example code that doesn't do what you want.
- **What YOU do:** Replace it entirely with the code I provided — the Reconcile function that creates ConfigMaps.
- **This is the ONLY file where you write real logic.** Everything else is either auto-generated or boilerplate.

### Step 13 explained (do you write code?)

**No.** You write ZERO code for this step. The command `operator-sdk run --local` just **compiles and runs** all the code you already wrote in Steps 5 and 8.

It's like pressing "play" — it takes your code, builds it, and starts it connected to Minikube.

### The Complete Picture — What YOU write vs What SDK gives you

| File | Who creates it | Do you edit it? | What it does |
|------|---------------|----------------|--------------|
| `cmd/manager/main.go` | SDK | No | Starts the operator |
| `pkg/apis/demo/v1/greeter_types.go` | SDK creates skeleton | **YES — you define your fields** | Defines CR structure |
| `pkg/apis/demo/v1/zz_generated.deepcopy.go` | `generate k8s` command | No (auto-generated) | Copy methods for Kubernetes |
| `pkg/controller/greeter/greeter_controller.go` | SDK creates skeleton | **YES — you write the Reconcile logic** | What to do when CR appears |
| `pkg/controller/add_greeter.go` | SDK | No | Registers controller |
| `pkg/controller/controller.go` | SDK | No | Registers all controllers |
| `deploy/crds/*_crd.yaml` | `generate crds` command | Only to fix v1beta1→v1 | CRD for the cluster |
| `deploy/crds/*_cr.yaml` | SDK | Yes (set your values) | Sample CR |
| `deploy/operator.yaml` | SDK | Only to set image name | Operator deployment |
| `deploy/role.yaml` | SDK | No | Permissions |
| `build/Dockerfile` | SDK | No | Container image |
| `go.mod` | SDK | No | Dependencies |

### The exercise connected step by step

```
Step 2: operator-sdk new greeter-operator
         → SDK creates: ALL folders + boilerplate files
         → You write: NOTHING

Step 4: operator-sdk add api
         → SDK creates: greeter_types.go (skeleton), CRD yaml, sample CR
         → You write: NOTHING yet

Step 5: Edit greeter_types.go
         → SDK creates: nothing
         → You write: YOUR CR fields (Name, Message, Ready)
         → File: pkg/apis/demo/v1/greeter_types.go

Step 6: operator-sdk generate k8s + generate crds
         → SDK creates: zz_generated.deepcopy.go + updated CRD yaml
         → You write: NOTHING (just run commands)

Step 7: operator-sdk add controller
         → SDK creates: greeter_controller.go (skeleton), add_greeter.go
         → You write: NOTHING yet

Step 8: Edit greeter_controller.go
         → SDK creates: nothing
         → You write: YOUR LOGIC (create ConfigMap, update status)
         → File: pkg/controller/greeter/greeter_controller.go

Step 9: go build
         → Compiles everything. You write nothing.

Step 10-11: Fix CRD yaml + sample CR
         → You edit: deploy/crds/ files (fix version format, set values)

Step 12: kubectl apply CRD
         → Deploys CRD to cluster. You write nothing.

Step 13: operator-sdk run --local
         → Runs your code. You write nothing.
         → Your Reconcile() from Step 8 is now LIVE and watching.

Step 14: kubectl apply CR
         → Triggers your Reconcile(). You write nothing.
         → Your Step 8 code runs: creates ConfigMap, updates status.
```

### One sentence summary

The SDK gives you 95% of the project. **You only write 2 things:** what your CR looks like (types) and what to do when it appears (controller logic). Everything else is generated or provided.

---

## Part 4: Deep Explanation — What Happens on Your Machine

### The Goal of This Exercise

You want to understand how the **mongo-operator** works. Instead of reading its complex code that talks to MongoDB Atlas, we build a **tiny copy** of it that does something simple (creates ConfigMaps) so you can see the pattern in action.

### Step 1: `rm -rf greeter-operator`

- **What you did on your machine:** Deleted the old broken folder.
- **Why:** Previous attempts left corrupted files. Starting clean ensures no leftover garbage.
- **Connection to mongo-operator:** If someone cloned the mongo-operator fresh, they'd start with a clean folder too.

### Step 2: `operator-sdk new greeter-operator`

**What you did:** Asked the Operator SDK tool to create a new empty project.

**What it created on disk:**

```
/home/saifi/sbs/self_learning/operator/greeter-operator/
├── cmd/manager/main.go          ← SDK wrote this. You DON'T touch it.
├── pkg/apis/apis.go             ← SDK wrote this. You DON'T touch it.
├── pkg/controller/controller.go ← SDK wrote this. You DON'T touch it.
├── build/Dockerfile             ← SDK wrote this. You DON'T touch it.
├── build/bin/entrypoint         ← SDK wrote this. You DON'T touch it.
├── build/bin/user_setup         ← SDK wrote this. You DON'T touch it.
├── deploy/operator.yaml         ← SDK wrote this. You edit ONLY the image name later.
├── deploy/role.yaml             ← SDK wrote this. You DON'T touch it.
├── deploy/role_binding.yaml     ← SDK wrote this. You DON'T touch it.
├── deploy/service_account.yaml  ← SDK wrote this. You DON'T touch it.
├── version/version.go           ← SDK wrote this. You DON'T touch it.
├── go.mod                       ← SDK wrote this. You DON'T touch it.
├── go.sum                       ← SDK wrote this. You DON'T touch it.
└── tools.go                     ← SDK wrote this. You DON'T touch it.
```

**What this code does if you ran it right now:** Starts up, connects to Kubernetes, does NOTHING, sits there. Because there's no CRD to watch and no controller logic yet.

**Connection to mongo-operator:** The mongo-operator started exactly like this. Someone ran this command years ago, then added their MongoDB-specific stuff on top.

### Step 4: `operator-sdk add api`

**What you did:** Told the SDK "I want to manage a resource called Greeter."

**What it created on disk (new files):**

```
pkg/apis/demo/v1/
├── greeter_types.go              ← SDK created SKELETON. You WILL edit this.
├── zz_generated.deepcopy.go     ← SDK generated. You NEVER touch this.
├── doc.go                       ← SDK created. You DON'T touch.
├── register.go                  ← SDK created. You DON'T touch.

deploy/crds/
├── demo.example.com_greeters_crd.yaml    ← SDK generated. You'll fix version later.
├── demo.example.com_v1_greeter_cr.yaml   ← SDK created sample. You'll edit values.
```

**What the skeleton `greeter_types.go` looks like before you edit:**

```go
type GreeterSpec struct {
    // INSERT ADDITIONAL SPEC FIELDS
}

type GreeterStatus struct {
    // INSERT ADDITIONAL STATUS FIELD
}
```

It's empty! The SDK doesn't know what fields YOUR resource needs. That's YOUR job in Step 5.

**Connection to mongo-operator:** Someone ran this same command with `--api-version=db.sbcp.io/v1 --kind=MongoAtlas` and got `mongoatlas_types.go` as a skeleton.

### Step 5: Editing `greeter_types.go`

**What you did:** Opened the file and wrote YOUR fields.

**Why:** The SDK gave you an empty form. Now you're filling in "what does a Greeter CR contain?"

**Your decision:**
- User should provide: a `name` (who to greet) → `GreeterSpec.Name`
- Operator will report: a `message` (what greeting was made) + `ready` (was it done?) → `GreeterStatus`

**How this connects to the CR YAML the user writes later:**

```yaml
apiVersion: demo.example.com/v1    ← matches --api-version from Step 4
kind: Greeter                       ← matches --kind from Step 4
metadata:
  name: my-greeter                  ← Kubernetes standard field
spec:
  name: "Muzakkir"                  ← YOUR field from GreeterSpec.Name
status:                             ← Operator fills this (GreeterStatus)
  message: "Greeting created..."
  ready: true
```

**Connection to mongo-operator:** They wrote `Database string` in `MongoAtlasSpec`. The user writes `spec.database: "dev_myapp"` in their CR.

### Step 6: `generate k8s` and `generate crds`

**What you did:** Ran two commands. You wrote ZERO code.

**What happened behind the scenes:**

1. `generate k8s` → the tool read your `greeter_types.go`, saw you have `Name`, `Message`, `Ready` fields, and auto-generated `DeepCopy()` methods in `zz_generated.deepcopy.go`. Kubernetes requires these to work properly internally.

2. `generate crds` → the tool read your `greeter_types.go` and updated `deploy/crds/demo.example.com_greeters_crd.yaml` to include:
   - `spec.name`: type: string, required: true
   - `status.message`: type: string
   - `status.ready`: type: boolean

**Why:** These generated files connect your Go code to Kubernetes. Without them, Kubernetes wouldn't know what fields to accept in the YAML.

### Step 7: `operator-sdk add controller`

**What you did:** Told the SDK "give me a controller skeleton for Greeter."

**What the skeleton controller looks like (SDK's template):**

```go
func (r *ReconcileGreeter) Reconcile(request reconcile.Request) (reconcile.Result, error) {
    // Fetch the Greeter instance
    instance := &demov1.Greeter{}
    err := r.client.Get(context.TODO(), request.NamespacedName, instance)

    // ... template code that creates a Pod (not what we want)

    return reconcile.Result{}, nil
}
```

The SDK gives you a **generic example** that creates a Pod. It's not useful for us. We need to replace it with ConfigMap logic in Step 8.

**Connection to mongo-operator:** Someone ran this for `--kind=MongoAtlas` and got `mongoatlas_controller.go` skeleton, then replaced it with Atlas API calls.

### Step 8: Writing the controller logic

**What you did:** Opened `pkg/controller/greeter/greeter_controller.go` and replaced the SDK's template with YOUR logic.

**This is the ONLY file where you write "business logic."**

**Registration part (runs ONCE at startup):**
```go
func Add(mgr manager.Manager) error { ... }
```
"Hey Manager, register me as a controller. I'll watch for Greeter CRs and ConfigMaps."

**Watch setup:**
```go
c.Watch(&source.Kind{Type: &demov1.Greeter{}}, &handler.EnqueueRequestForObject{})
```
"Kubernetes, notify me whenever someone creates/updates/deletes a Greeter."

```go
c.Watch(&source.Kind{Type: &corev1.ConfigMap{}}, &handler.EnqueueRequestForOwner{...})
```
"Also notify me if someone messes with ConfigMaps that I created."

**Reconcile function (runs EVERY TIME something changes):**

This function is called by Kubernetes whenever:
- A Greeter CR is created (`kubectl apply`)
- A Greeter CR is deleted (`kubectl delete`)
- A ConfigMap we own is deleted/changed

**Inside Reconcile — what it does step by step:**

1. **Get the CR:** "What Greeter triggered this? Let me read it."
2. **Check ConfigMap:** "Does a ConfigMap already exist for this Greeter?"
3. **Create if missing:** "It doesn't exist, let me create it with a greeting message."
4. **Update status:** "Tell the user it's done."

**Connection to mongo-operator:**

| Our code does | Mongo-operator does | Same pattern? |
|---|---|---|
| `r.client.Get(... greeter)` | `r.client.Get(... mongoatlas)` | Yes — fetch CR |
| Check if ConfigMap exists | Check if database exists in Atlas | Yes — check state |
| `r.client.Create(... configmap)` | Call Atlas API to create database | Yes — do the work |
| `r.client.Status().Update(...)` | `r.client.Status().Update(...)` | Yes — report back |

### Step 13: Running the operator

**You wrote ZERO code for this step.** You just pressed "play."

**What happens internally:**
1. Go compiles your code (Steps 5 + 8)
2. `cmd/manager/main.go` (SDK boilerplate) runs:
   - Connects to Minikube via `~/.kube/config`
   - Calls `controller.AddToManager()` which calls your `Add()` function from Step 8
   - Your `Add()` function registers watches for Greeter CRs and ConfigMaps
   - Manager starts listening for events
3. The operator is now **live and waiting**

**Connection to mongo-operator:** In production, the `operator.yaml` Deployment starts a pod that runs this same code inside the cluster.

### Step 14: Applying the CR

**What you did:** Created a Greeter CR saying "greet Muzakkir."

**What happens:**
1. `kubectl` sends the YAML to Kubernetes API
2. Kubernetes validates it against the CRD schema (Step 12)
3. Kubernetes stores it
4. Kubernetes tells your operator "hey, new Greeter appeared" (because of WATCH #1 from Step 8)
5. Your `Reconcile()` function fires (Step 8 code runs)
6. `Reconcile()` creates a ConfigMap with "Hello, Muzakkir!"
7. `Reconcile()` updates the CR status to `ready: true`

**This is the moment where Steps 5, 8, 12, and 13 all come together.** Your types (Step 5) define how to read the CR. Your controller (Step 8) decides what to do. The CRD (Step 12) allows the CR to exist. The running operator (Step 13) processes it.

### Summary: What you wrote vs what SDK gave you

```
SDK gave you (don't touch):        YOU wrote (your logic):
─────────────────────────          ─────────────────────────
cmd/manager/main.go                pkg/apis/demo/v1/greeter_types.go
pkg/apis/apis.go                     → Your fields (Name, Message, Ready)
pkg/controller/controller.go       
pkg/controller/add_greeter.go      pkg/controller/greeter/greeter_controller.go
build/Dockerfile                     → Your logic (create ConfigMap, update status)
deploy/role.yaml                   
deploy/operator.yaml               deploy/crds/*_crd.yaml (fixed version format)
deploy/service_account.yaml        deploy/crds/*_cr.yaml (set test values)
version/version.go                 
go.mod                             
```

**Total: You wrote 2 files. SDK generated everything else.**

---

## Part 5: The 2 Files You Edit

### File 1: `pkg/apis/demo/v1/greeter_types.go`

**Purpose:** Defines WHAT your CR contains — the fields.

**How to think about it:** You're designing a form. What questions does it ask? What does the report look like after it's processed?

**Ask yourself 2 questions:**
1. "What does the USER need to provide?" → This goes in `Spec`
2. "What does the OPERATOR report back?" → This goes in `Status`

#### The code, explained line by line:

```go
package v1
```
Every Go file starts with `package <name>`. This file is in the `v1` package because it lives in the `v1/` folder. Don't change this.

```go
import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)
```
`import` brings in external code you need. `metav1` gives you Kubernetes standard fields like `metadata.name`, `metadata.namespace`. Every types file needs this.

```go
type GreeterSpec struct {
    Name string `json:"name"`
}
```

Breaking it down:
- `type` — Go keyword meaning "I'm defining a new data structure"
- `GreeterSpec` — the name. Convention: `<YourKind>Spec`
- `struct { }` — Go's version of an object/class. Contains fields.
- `Name string` — one field called `Name`, type is `string` (text)
- `` `json:"name"` `` — when this becomes YAML, the field is called `name` (lowercase)

This maps to YAML:
```yaml
spec:
  name: "Muzakkir"   ← this "name" comes from json:"name"
```

If you wanted more fields, you'd add them:
```go
type GreeterSpec struct {
    Name     string `json:"name"`
    Language string `json:"language"`    // added a second field
    Repeat   int    `json:"repeat"`      // added a number field
}
```

Then the user would write:
```yaml
spec:
  name: "Muzakkir"
  language: "english"
  repeat: 3
```

#### Recipe for ANY operator types file:

```go
package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type <YourKind>Spec struct {
    // YOUR fields here
    FieldName FieldType `json:"yamlName"`
}

type <YourKind>Status struct {
    // YOUR output fields here
    FieldName FieldType `json:"yamlName,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
// +kubebuilder:subresource:status
// +kubebuilder:resource:path=<plural>,scope=Namespaced
type <YourKind> struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   <YourKind>Spec   `json:"spec,omitempty"`
    Status <YourKind>Status `json:"status,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type <YourKind>List struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []<YourKind> `json:"items"`
}

func init() {
    SchemeBuilder.Register(&<YourKind>{}, &<YourKind>List{})
}
```

**Go field types you can use:**
- `string` — text
- `int` — whole number
- `bool` — true/false
- `[]string` — list of texts
- `[]Role` — list of a custom struct (like mongo-operator's roles)

---

### File 2: `pkg/controller/greeter/greeter_controller.go`

**Purpose:** Defines WHAT TO DO when a CR appears/changes/deletes.

**How to think about it:** "When someone asks for a Greeter, what actions should I perform?"

**Ask yourself:**
1. "What resource am I watching?" → Greeter CRs
2. "What should I CREATE when a CR appears?" → A ConfigMap
3. "How do I know if I already did the work?" → Check if ConfigMap exists
4. "What do I report back?" → Update status
5. "What happens on delete?" → Owner reference handles cleanup

#### The code structure (always the same pattern):

```
┌─────────────────────────────────────────────┐
│ IMPORTS                                      │
│ (external libraries you need)                │
├─────────────────────────────────────────────┤
│ REGISTRATION FUNCTIONS                       │
│ Add() → registers controller at startup      │
│ add() → sets up watches                      │
├─────────────────────────────────────────────┤
│ RECONCILE FUNCTION                           │
│ The main logic — called on every change      │
│  1. Fetch the CR                             │
│  2. Check if work is done                    │
│  3. Do the work if needed                    │
│  4. Update status                            │
└─────────────────────────────────────────────┘
```

#### Recipe for ANY controller:

```go
func (r *Reconcile<YourKind>) Reconcile(request reconcile.Request) (reconcile.Result, error) {

    // 1. FETCH the CR
    instance := &yourv1.<YourKind>{}
    r.client.Get(context.TODO(), request.NamespacedName, instance)

    // 2. CHECK if your work is already done
    r.client.Get(context.TODO(), ..., found)

    // 3. DO THE WORK if needed
    if notFound {
        // Create resource / call API / whatever your operator does
        r.client.Create(context.TODO(), yourResource)
    }

    // 4. UPDATE STATUS
    instance.Status.SomeField = "done"
    r.client.Status().Update(context.TODO(), instance)

    return reconcile.Result{}, nil
}
```

#### Go basics you need for these 2 files

| Go syntax | What it means | Example |
|---|---|---|
| `type X struct { }` | Define a data structure | `type GreeterSpec struct { Name string }` |
| `func name() { }` | Define a function | `func Add(mgr manager.Manager) error { }` |
| `:=` | Create variable and assign | `name := "hello"` |
| `err != nil` | Check if there's an error | Always check after API calls |
| `&something{}` | Create a pointer to a new object | `&corev1.ConfigMap{}` |
| `fmt.Sprintf("Hello %s", name)` | String formatting | `"Hello Muzakkir"` |
| `map[string]string{"key": "value"}` | Key-value dictionary | ConfigMap data |
| `` `json:"name"` `` | Tag telling YAML/JSON field name | Maps Go field to YAML |

That's all the Go you need for a basic operator. The rest is just using the controller-runtime library functions (`r.client.Get`, `r.client.Create`, etc.).

---

## Part 6: How It Scales

### Do you always write only 2 files?

For a **simple** operator with one CRD — yes, 2 files is the minimum you write.

But for **real-world** operators (like the mongo-operator), you'll typically write more:

| Scenario | Files you write |
|----------|----------------|
| Simple operator, 1 CRD, logic fits in one file | 2 files (types + controller) |
| Operator needs to talk to an external API (like Atlas) | 3+ files (types + controller + API client like `pkg/config/config.go`) |
| Operator has multiple CRDs (like mongo-operator has 6) | 2 files × number of CRDs (each CRD gets its own types + controller) |
| Shared helper functions across controllers | +1 file (`pkg/utils/`) |

### The mongo-operator breakdown:

- 6 CRDs → 6 types files + 6 controller files = 12 files you'd write
- 1 API client (`pkg/config/config.go`) = 1 more
- 1 utility file (`pkg/utils/`) = 1 more
- Total: ~14 files of custom code

### But the pattern is always the same:

- Each CRD = 1 types file + 1 controller file
- Plus any helper/utility code your logic needs

So "2 files" is the **minimum per CRD**. It scales with complexity, but the recipe doesn't change.
