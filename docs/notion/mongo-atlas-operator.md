# Mongo-atlas-operator

In the code, there are two concept of making the cred isolation.
1. Application Scope
1. namespace Scope
This is the feature about the making the cred that will be use for the access or perform any action over the atlas will be taking care. This is not something that comes in the kubernetes or atlas. It is define in the mongo operator code. So the concept is:


# Terminology (fixed)

**Namespace **= a Kubernetes namespace (like a folder for grouping apps)
**App **= a microservice (e.g., order-service). One app = one Deployment = one or more Pods (replicas). I'll just say "app" from now on.

**The Structure:**

Namespace: "team-payments"
├── App: order-service      (needs database: order-db)
├── App: invoice-service    (needs database: invoice-db)
└── App: refund-service     (needs database: refund-db)
3 apps, 1 namespace, 3 databases in Atlas.
**Namespace Scope:**
One Atlas user for the entire namespace. All apps share it.
**Atlas side:
**User: "prod-team-payments"
Password: "abc123"
Can access: [order-db, invoice-db, refund-db]
**Kubernetes side (namespace "team-payments"):
**Secret "mongo-cred"       → password: abc123  (master secret)
Secret "order-mongodb"    → password: abc123  (copied from mongo-cred)
Secret "invoice-mongodb"  → password: abc123  (copied from mongo-cred)
Secret "refund-mongodb"   → password: abc123  (copied from mongo-cred)
1 Atlas user total
All 3 apps connect to Atlas with the same username+password
Each app has its own Secret name, but the password inside is the same

**Application Scope:**

One Atlas user per app. Each app has its own credentials.
Atlas side:
User: "prod-order-service"     Password: "xyz111"  Can access: [order-db]
User: "prod-invoice-service"   Password: "xyz222"  Can access: [invoice-db]
User: "prod-refund-service"    Password: "xyz333"  Can access: [refund-db]
**Kubernetes side (namespace "team-payments"):
**Secret "order-mongodb"    → password: xyz111
Secret "invoice-mongodb"  → password: xyz222
Secret "refund-mongodb"   → password: xyz333
3 Atlas users total (one per app)
Each app connects to Atlas with its own unique username+password
Each app can only access its own database
| Scope	 | How many Atlas users? | Who shares credentials? |
| --- | --- | --- |
| Namespace	 | 1 per namespace | All apps in the namespace |
| Application	 | 1 per app	 | Nobody — each app is isolated |

- **Namespace scope **→ all apps in that namespace use the same Atlas credentials
- **Application scope **→ each app in that namespace uses its own Atlas credentials

