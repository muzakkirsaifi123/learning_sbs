# Kubernetes Operator


## **1. First: What is a Kubernetes Operator?**
A Kubernetes operator is basically
> **A program running inside Kubernetes that knows how to manage a particular kind of application or service.**
Normally, Kubernetes knows how to manage things like the following:
- Pods
- Deployments
- Services
- ConfigMaps
- Secrets
But Kubernetes does **not automatically know how to manage MongoDB Atlas users, databases, clusters, projects, etc.**
That's where an Operator comes in.
Think about it this way:
```text
Kubernetes
    |
    | understands
    v
Pods, Deployments, Services, Secrets...
```
But:
```text
Kubernetes
    |
    X---- doesn't inherently understand MongoDB Atlas
```
So we install an operator:
```text
Kubernetes
    |
    v
MongoDB Atlas Operator
    |
    v
MongoDB Atlas
```
Now Kubernetes has a component that understands how to talk to MongoDB Atlas.

## **2. What problem is the operator solving?**
Imagine you want to create a MongoDB Atlas database user.
Without an operator, you might manually do this:
1. Log in to MongoDB Atlas.
1. Go to your project.
1. Go to Database Access.
1. Create a user.
1. Give the user a username.
1. Give it a password.
1. Give it roles.
1. Save it.
1. Repeat this for another environment.
1. Somehow keep Kubernetes configuration synchronized with Atlas.
That's manual management.
With an operator, you can describe what you want in Kubernetes:
```yaml
apiVersion: ...
kind: ...
metadata:
  name: my-mongodb-user
spec:
  username: application-user
  ...
```
Then the operator says:
> "I see that you want this MongoDB user to exist. I'll create/manage it in MongoDB Atlas."
So you declare the **desired state**, and the operator works to make reality match that desired state.

---

## **3. The most important concept: Desired State**
This is the key idea I want you to understand before we go further.
Kubernetes is largely based on:
> **You tell Kubernetes what you want, rather than manually telling it every action to perform.**
For example:
```yaml
kind: Deployment

spec:
  replicas: 3
```
You're saying:
> "I want 3 replicas."
You're not saying
> "Create Pod #1, then create Pod #2, then create Pod #3."
Kubernetes figures out how to achieve that.
An operator follows the same philosophy.
You say:
```text
I want MongoDB Atlas user "my-app" to exist
```
The operator figures out the following:
```text
How do I create/update/delete that user in Atlas?
```

---

## **4. So what do we actually create?**
There are several pieces involved, and this is where beginners often get confused.
For an operator-based system, you typically have
```text
1. Operator
      ↓
2. CRD
      ↓
3. Custom Resource
      ↓
4. Controller
      ↓
5. External system
```
Let's understand each one.

---

# **5. What is a CRD?**
CRD means:
> **CustomResourceDefinition**
This is extremely important.
Kubernetes already has built-in resource types:
```text
Pod
Deployment
Service
ConfigMap
Secret
```
But suppose we want Kubernetes to understand:
```text
MongoDBAtlasUser
```
Kubernetes doesn't know what that is by default.
So we install a CRD that essentially tells Kubernetes:
> "There is a new type of Kubernetes object called **`MongoDBAtlasUser`**."
Conceptually:
```text
Kubernetes
│
├── Pod
├── Deployment
├── Service
├── Secret
│
└── MongoDBAtlasUser   ← added through CRD
```
The CRD defines the **kind of object**.

---

# **6. Then what is a Custom Resource?**
Once the CRD exists, you can create an actual object of that type.
For example, conceptually:
```yaml
apiVersion: mongodb.example.com/v1
kind: MongoDBAtlasUser

metadata:
  name: application-user

spec:
  username: application
  roles:
    - readWrite
```
The important distinction is:

### **CRD**
Defines the **type**.
```text
MongoDBAtlasUser
```

### **Custom Resource**
Creates an **instance** of that type.
```text
application-user
```
A simple analogy:
```text
CRD = class / blueprint

Custom Resource = actual object created from that blueprint
```
For example:
```text
CRD:
    MongoDBAtlasUser

Resources:
    application-user
    reporting-user
    backup-user
```

---

# **7. Where does the Operator come into this?**
The CRD alone doesn't magically create anything in MongoDB Atlas.
You need a program watching those resources.
That's the Operator/controller.
Imagine you apply:
```yaml
kind: MongoDBAtlasUser

metadata:
  name: application-user
```
Kubernetes stores that object.
The MongoDB Atlas Operator is continuously watching Kubernetes.
It sees:
```text
MongoDBAtlasUser/application-user
```
and says:
> "I need to make MongoDB Atlas match this desired state."
It then talks to the MongoDB Atlas API.
Conceptually:
```text
                 Kubernetes
                     |
                     |
       MongoDBAtlasUser object
                     |
                     ↓
             MongoDB Atlas Operator
                     |
                     | API request
                     ↓
               MongoDB Atlas
                     |
                     ↓
              MongoDB Atlas User
```
That's the entire fundamental idea.

---

# **8. What is a Controller?**
You'll hear **controller** and **Operator** used together, but there is a useful distinction.
A controller is a program that watches resources and attempts to make actual state match desired state.
For example:
```text
Desired state:

MongoDB Atlas user should exist
username = application
role = readWrite
```
The controller checks:
```text
Does the user exist in Atlas?
```
If:
```text
NO
```
it creates it.
If:
```text
YES, but wrong role
```
it may update it.
If:
```text
YES and correct
```
it does nothing.
This process is often called a **reconciliation loop**.

---

# **9. The reconciliation loop**
This is probably the single most important Operator concept.
Imagine the Operator constantly doing:
```text
        ┌─────────────────────┐
        │                     │
        │  Read desired state │
        │                     │
        └──────────┬──────────┘
                   ↓
        ┌─────────────────────┐
        │                     │
        │  Check actual state │
        │                     │
        └──────────┬──────────┘
                   ↓
        ┌─────────────────────┐
        │                     │
        │ Are they different? │
        │                     │
        └──────┬────────┬─────┘
               │        │
              YES       NO
               │        │
               ↓        ↓
          Make them     Nothing
           match
               │
               └───────────────┐
                               ↓
                         Check again
```
For your MongoDB example:
```text
Desired:

MongoDB Atlas user:
    username = app-user
    role = readWrite
```
Actual Atlas state:
```text
No such user
```
Operator:
```text
Create user
```
Later:
```text
Desired:
    role = readWrite

Actual:
    role = read
```
Operator notices the difference and reconciles it.

---

# **10. Why do we need an Operator at all?**
This is the natural question.
You might ask:
> "Why don't I just create the MongoDB Atlas user manually?"
You absolutely can.
An Operator becomes useful when you want **automation and Kubernetes-native management**.
For example, imagine you have:
```text
Development
Staging
Production
```
And each environment needs:
```text
MongoDB Atlas project
MongoDB cluster
MongoDB users
Database access
Roles
Configuration
```
Without an Operator, you might have scripts or manually manage everything.
With an Operator, you can represent much of that configuration as Kubernetes resources.
For example:
```text
Git repository
      |
      ↓
Kubernetes YAML
      |
      ↓
kubectl apply
      |
      ↓
Kubernetes API
      |
      ↓
MongoDB Atlas Operator
      |
      ↓
MongoDB Atlas
```
This works very nicely with GitOps and Infrastructure-as-Code approaches.

---

# **11. What exactly would you create for a MongoDB Atlas user?**
At a high level, you need several things.

### **Step 1 — Install the MongoDB Atlas Operator**
The Operator itself needs to be running in your Kubernetes cluster.
For example:
```text
Kubernetes Cluster

┌─────────────────────────────────────┐
│                                     │
│   MongoDB Atlas Operator             │
│                                     │
│   controller                         │
│   controller                         │
│                                     │
└─────────────────────────────────────┘
```
Installing the Operator normally also installs its CRDs.

---

### **Step 2 — Give the Operator access to MongoDB Atlas**
The Operator needs credentials to call the MongoDB Atlas API.
Conceptually:
```text
MongoDB Atlas API credentials
              ↓
       Kubernetes Secret
              ↓
      MongoDB Atlas Operator
              ↓
       MongoDB Atlas API
```
This is important.
The Operator can't magically access your Atlas account.
It needs authentication.

---

### **Step 3 — Tell the Operator which Atlas project it should manage**
You need to establish the relationship between Kubernetes and your Atlas project.
Conceptually:
```text
Kubernetes

MongoDBAtlasProject
        |
        ↓
Project: my-production-project
        |
        ↓
MongoDB Atlas
```
The exact resource names/API versions depend on the version of the MongoDB Atlas Operator you're using, so you should always check the current operator documentation before copying manifests.

---

### **Step 4 — Create the MongoDB Atlas user resource**
Now you create the resource representing the user you want.
Conceptually:
```yaml
kind: MongoDBAtlasUser

metadata:
  name: application-user

spec:
  username: application-user

  roles:
    - readWrite
```
Again, this is **conceptual YAML**, not something I'd recommend applying directly. The exact MongoDB Atlas Operator CRD schema varies by operator version and configuration.
The important thing is understanding what it represents.

---

# **12. What happens after you run kubectl apply?**
Suppose you have:
```text
atlas-user.yaml
```
You run:
```bash
kubectl apply -f atlas-user.yaml
```
Here's what happens.

### **Phase 1**
**`kubectl`** sends the object to the Kubernetes API server.
```text
kubectl
   |
   ↓
API Server
```

### **Phase 2**
The API server checks:
> "Do I understand this kind?"
Because the Operator installed the CRD, Kubernetes understands:
```text
MongoDBAtlasUser
```

### **Phase 3**
Kubernetes stores the resource.
```text
Kubernetes API
      |
      ↓
MongoDBAtlasUser
```

### **Phase 4**
The MongoDB Operator is watching for that resource.
It notices:
```text
New MongoDBAtlasUser appeared!
```

### **Phase 5**
The Operator reads the specification.
For example:
```text
username = application-user
role = readWrite
```

### **Phase 6**
The Operator calls MongoDB Atlas.
```text
Operator
    |
    | HTTPS/API
    ↓
MongoDB Atlas
```

### **Phase 7**
Atlas creates the user.
```text
MongoDB Atlas
      |
      ↓
application-user
```

### **Phase 8**
The Operator updates the Kubernetes resource's status.
Conceptually:
```yaml
status:
  state: ready
```
So Kubernetes can tell you:
> "The thing you asked for is now actually configured."

---

# **13. This distinction is VERY important**
There are two different things:

### **`spec`**
What you **want**.
```yaml
spec:
  username: app-user
  role: readWrite
```

### **`status`**
What the Operator **observes**.
Conceptually:
```yaml
status:
  state: ready
```
Think:
```text
SPEC
 ↓
"I want this"

       Operator

STATUS
 ↓
"This is what actually happened"
```
This pattern appears all over Kubernetes.

---

# **14. What if you delete the Kubernetes resource?**
This is another important Operator behavior.
Suppose you do:
```bash
kubectl delete -f atlas-user.yaml
```
The Custom Resource disappears.
The Operator notices:
```text
Desired resource no longer exists.
```
Depending on the resource and Operator behavior, it can then remove the corresponding object from Atlas.
This is one of the powerful aspects of the Operator model:
```text
Kubernetes desired state
        ↓
Operator
        ↓
External system
```
Kubernetes becomes your declarative control point.
**But:** whether deletion of a Kubernetes resource deletes the corresponding Atlas object is resource-specific, so you should verify the deletion/cleanup behavior for the exact MongoDB Atlas Operator resource you're using.

---

# **15. What if someone manually changes Atlas?**
This is where Operators become really interesting.
Suppose your Kubernetes configuration says:
```text
Desired:

user = app-user
role = readWrite
```
But someone manually goes into Atlas and changes the role:
```text
Actual:

user = app-user
role = read
```
The Operator can detect that actual state differs from desired state and reconcile it, depending on what that resource/controller manages.
So you can think of it as:
```text
                 Desired
                    |
                    ↓
              Kubernetes
                    |
                    ↓
                Operator
                    |
                    ↓
               MongoDB Atlas
                    |
                    ↓
                 Actual
```
The Operator tries to keep:
```text
Desired ≈ Actual
```

---

# **16. Operator vs CRD — don't mix these up**
This is one of the biggest beginner mistakes.

### **CRD**
**Teaches Kubernetes a new resource type.**
```text
"MongoDBAtlasUser exists as a resource type."
```

### **Custom Resource**
**An actual object of that type.**
```text
"Create this particular MongoDB user."
```

### **Operator**
**The software that understands what to do with that object.**
```text
"I know how to turn this MongoDBAtlasUser
resource into a real user in MongoDB Atlas."
```

### **Controller**
**The reconciliation logic inside the Operator.**
```text
"I'll continuously compare desired and actual state."
```
A useful mental model:
```text
          CRD
           |
           | defines
           ↓
    MongoDBAtlasUser
           |
           | actual resource
           ↓
    app-user resource
           |
           | watched by
           ↓
       Operator
           |
           | reconciles
           ↓
     MongoDB Atlas
```

---

# **17. When should you create an Operator?**
You don't create an Operator every time you deploy an application.
This is another important point.
Suppose you have:
```text
Nginx
```
You probably don't need to write an Nginx Operator yourself.
Kubernetes already has:
```text
Deployment
Service
ConfigMap
Secret
```
that can handle the basic lifecycle.
An Operator becomes particularly useful when an application/service has **complex domain-specific lifecycle operations**.
For example:
```text
MongoDB
Kafka
PostgreSQL
Redis
Cloud resources
External SaaS resources
```
An Operator can encode knowledge such as:
```text
How do I create this thing?
How do I configure it?
How do I update it safely?
How do I detect failures?
How do I scale it?
How do I perform maintenance?
How do I delete it?
How do I recover it?
```
That's why Operators are often described as putting an application's operational knowledge into software.

---

# **18. Do YOU need to create the MongoDB Atlas Operator?**
No.
This is another important distinction.
If you're using the **MongoDB Atlas Kubernetes Operator**, you normally **install the existing Operator** rather than writing your own from scratch.
Think:
```text
MongoDB already provides an Operator
              ↓
       You install it
              ↓
      You use its CRDs
              ↓
You create Custom Resources
              ↓
      Operator manages Atlas
```
You would write your **own Operator** if you had some custom system or workflow that wasn't already supported adequately by an existing Operator.

---

# **19. What does the architecture look like?**
Here's the complete picture:
```text
                    YOU
                     |
                     | kubectl apply
                     ↓
              ┌───────────────┐
              │ Kubernetes    │
              │ API Server    │
              └───────┬───────┘
                      |
                      ↓
          ┌───────────────────────┐
          │ Custom Resource       │
          │                       │
          │ MongoDBAtlasUser      │
          │                       │
          │ app-user              │
          └───────────┬───────────┘
                      |
                      | watched by
                      ↓
          ┌───────────────────────┐
          │ MongoDB Atlas        │
          │ Operator              │
          │                       │
          │ Controller            │
          └───────────┬───────────┘
                      |
                      | Atlas API
                      ↓
          ┌───────────────────────┐
          │ MongoDB Atlas         │
          │                       │
          │ Project               │
          │   └── app-user        │
          └───────────────────────┘
```
That's the picture I want you to have in your head.

---

# **20. A real-world analogy**
Imagine you run a hotel.
You tell a hotel manager:
> "I need room 301 cleaned every day."
You don't personally go into the room every day.
You give the manager the desired state:
```text
Room 301 → clean
```
The manager:
1. Checks the room.
1. If dirty → sends someone to clean it.
1. Checks again later.
1. If something changes → fixes it.
The manager is similar to the **Operator**.
The instruction is similar to the **Custom Resource**.
The definition of what an instruction like "room cleaning" looks like is similar to the **CRD**.

---

# **21. The terminology you should memorize**
If you're learning Kubernetes Operators, learn these terms first:
| **Term** | **Meaning** |
| --- | --- |
| Kubernetes | Platform/orchestrator |
| API Server | Entry point for Kubernetes API |
| Resource | Object managed by Kubernetes |
| CRD | Defines a new resource type |
| Custom Resource | An instance of that new type |
| Controller | Watches resources and reconciles state |
| Operator | Usually a controller/application that manages a specific domain |
| **`spec`** | Desired state |
| **`status`** | Observed/current state |
| Reconciliation | Process of making actual state match desired state |

The most important relationship is:
```text
CRD
 ↓
defines
 ↓
Custom Resource
 ↓
watched by
 ↓
Controller / Operator
 ↓
changes
 ↓
real system
```

---

# **22. MongoDB Atlas example in one sentence**
If someone asks you:
> "What is the MongoDB Atlas Operator doing?"
A good answer is:
> **The MongoDB Atlas Operator watches Kubernetes resources that describe the desired MongoDB Atlas configuration and uses the MongoDB Atlas API to reconcile Atlas so that its actual state matches that desired state.**
That's the core idea.

---

# **23. How I recommend you learn this**
Don't jump immediately into complicated Operator code.
Learn it in this order:

### **Level 1 — Kubernetes basics**
Understand:
```text
Pod
Deployment
Service
ConfigMap
Secret
Namespace
kubectl
API Server
```

### **Level 2 — Kubernetes declarative model**
Understand:
```text
spec
status
desired state
actual state
reconciliation
```

### **Level 3 — CRDs**
Learn:
```text
What is a CRD?
Why do we need it?
How does Kubernetes register a new kind?
```

### **Level 4 — Custom Resources**
Create something like:
```text
kind: MyDatabase
```
and understand what Kubernetes stores.

### **Level 5 — Controllers**
Understand:
```text
watch
event
reconcile
desired state
actual state
```

### **Level 6 — Operators**
Then understand:
```text
Operator = domain-specific controller(s)
```

### **Level 7 — MongoDB Atlas Operator**
Finally put it all together:
```text
Kubernetes
   +
CRD
   +
Custom Resource
   +
MongoDB Atlas Operator
   +
Atlas API
   =
Kubernetes-managed MongoDB Atlas resources
```

---

## **The one mental model to remember**
If you remember nothing else, remember this:
```text
YOU
 │
 │ "I want a MongoDB Atlas user"
 ↓
CUSTOM RESOURCE
 │
 │ desired state
 ↓
KUBERNETES API
 │
 ↓
MONGODB ATLAS OPERATOR
 │
 │ reconciliation
 ↓
MONGODB ATLAS API
 │
 ↓
REAL MONGODB ATLAS USER
```
And the Operator keeps watching and reconciling:
```text
                 ┌─────────────────────┐
                 │                     │
                 │   Desired State     │
                 │   Kubernetes        │
                 │                     │
                 └──────────┬──────────┘
                            ↓
                       OPERATOR
                            ↓
                 ┌─────────────────────┐
                 │                     │
                 │    Actual State     │
                 │    Atlas            │
                 │                     │
                 └─────────────────────┘
                            │
                            │
                     keep reconciling
                            │
                            └──────────→
```
**That is why we need an Operator.**
If you want to go hands-on next, the best next lesson is to build a **tiny Kubernetes Operator example from scratch** (not MongoDB yet): first create a CRD, then create a Custom Resource, then write a controller that watches it. Once you understand that, the MongoDB Atlas Operator becomes much easier to understand.

