# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4665O7FDW4G%2F20261128%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261128T031116Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBoaCXVzLXdlc3QtMiJHMEUCIGhtDR4osMhjBz1dc6YthpUPkq%2FhzK9xyneJ0vq2imXEAiEA8RsnMXcX0b3EF1NqJXTPw4Sf0F%2Fx%2F0di39BAOOZRB%2B0qiAQI4v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDL7HUTq%2FPeUK7q%2B5mircA3et1G2p%2BhWuK8z%2FX5eVCHwMROfMyvgHitZkHOS2%2BiJ7vTPfWLqf30PeOoMPku%2FvQNUIEtunYM%2FOwt0Dpoue13n%2Bbb81ykqIIQKdOtvixvzXr2SIXsMXdxr5l%2B2et1%2FE0tJYpcBxhbpfZI6RHefKsG7Lm457%2FwVciAcZMtpR%2FF2hobYN6KiWzYP7s4Zm6hN9zarnVmyld6hzw1KZXQAslXo5xvD%2BrwL5BeCqV1I%2FYnkMcLvfJ3mDWP992qAg3OAFdDQzV8hT8kVB1e3KnVNePlGDdjNGVc7s3FF%2F%2BEBW%2Bh3WhOQfNSo8VhrNEj91PculW2270JaTzLV6zuyCLnghecLatezNSpWgSgxAy2KRfTuAxxj6DjKQ%2FzX8EoJ1D1Hm9Xx6va8ZoMGD2bJnKz3j5rRFtw01A38HxNCPhMXhVnRAujgWHoE1h8y4T6GcZ8QWmyEFp2daMymkl434bgcXkV%2FhvI5jUrtYDB27SA71gp23OSOt9dJ30c3Z33ziQcYhmyzzPdxNlqmGOxSXz8aDlOrme6RylsrJRWYmz7d%2F5Cd%2BDL2EEdf7s60iObt1Hn9CETjZxCaed%2BcRWDzOO6neVunLSG3GjuR1D%2FE0ROXqTR0Zhtrc0sMbaaJ%2Bz%2F%2BTMNHpqNgGOqUBn6opUGvYtGC87fTrUyha5mY1EDogCHNF5ShyUCfvjm%2BxrPBmrjZwga2RuLzXdDSOpsh05U7Bi8V4rXHUzKIgfl2FtcjiSxE50bXL25zTH8%2F8YqhcVHakksLiZU2AbbkIKB3POmhs4yv4FlZs%2BVeIb7U0Dc9UaAa06qrXvZVXyQSOhKpdzFg7HNdwkgP%2FBq7oBWA0KlhV7UWiuCOaJLtymrzmH5S1&X-Amz-Signature=da6d80a40b0594506c2deafeba819b6b36ad305e02685b00ea4578e4b4e0decc&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4665O7FDW4G%2F20261128%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261128T031116Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBoaCXVzLXdlc3QtMiJHMEUCIGhtDR4osMhjBz1dc6YthpUPkq%2FhzK9xyneJ0vq2imXEAiEA8RsnMXcX0b3EF1NqJXTPw4Sf0F%2Fx%2F0di39BAOOZRB%2B0qiAQI4v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDL7HUTq%2FPeUK7q%2B5mircA3et1G2p%2BhWuK8z%2FX5eVCHwMROfMyvgHitZkHOS2%2BiJ7vTPfWLqf30PeOoMPku%2FvQNUIEtunYM%2FOwt0Dpoue13n%2Bbb81ykqIIQKdOtvixvzXr2SIXsMXdxr5l%2B2et1%2FE0tJYpcBxhbpfZI6RHefKsG7Lm457%2FwVciAcZMtpR%2FF2hobYN6KiWzYP7s4Zm6hN9zarnVmyld6hzw1KZXQAslXo5xvD%2BrwL5BeCqV1I%2FYnkMcLvfJ3mDWP992qAg3OAFdDQzV8hT8kVB1e3KnVNePlGDdjNGVc7s3FF%2F%2BEBW%2Bh3WhOQfNSo8VhrNEj91PculW2270JaTzLV6zuyCLnghecLatezNSpWgSgxAy2KRfTuAxxj6DjKQ%2FzX8EoJ1D1Hm9Xx6va8ZoMGD2bJnKz3j5rRFtw01A38HxNCPhMXhVnRAujgWHoE1h8y4T6GcZ8QWmyEFp2daMymkl434bgcXkV%2FhvI5jUrtYDB27SA71gp23OSOt9dJ30c3Z33ziQcYhmyzzPdxNlqmGOxSXz8aDlOrme6RylsrJRWYmz7d%2F5Cd%2BDL2EEdf7s60iObt1Hn9CETjZxCaed%2BcRWDzOO6neVunLSG3GjuR1D%2FE0ROXqTR0Zhtrc0sMbaaJ%2Bz%2F%2BTMNHpqNgGOqUBn6opUGvYtGC87fTrUyha5mY1EDogCHNF5ShyUCfvjm%2BxrPBmrjZwga2RuLzXdDSOpsh05U7Bi8V4rXHUzKIgfl2FtcjiSxE50bXL25zTH8%2F8YqhcVHakksLiZU2AbbkIKB3POmhs4yv4FlZs%2BVeIb7U0Dc9UaAa06qrXvZVXyQSOhKpdzFg7HNdwkgP%2FBq7oBWA0KlhV7UWiuCOaJLtymrzmH5S1&X-Amz-Signature=43cf56403cef3957a1d50737bbe0f285c1f5f925eb1fd6f96f164a260100bcf1&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
For example:
1. User places an order.
1. Order Service publishes **`OrderCreated`** to Kafka.
1. Payment Service consumes that event.
1. Inventory Service consumes that event.
1. Notification Service consumes that event.
Now:
- Order Service doesn't need to know all the consumers.
- Services can process events independently.
- A new service can subscribe to the same event without changing the order service.
- If a consumer is temporarily down, Kafka can retain the event for later processing (subject to retention and consumer configuration).


## **Direct communication vs Kafka communication**
| **Direct communication** | **Kafka communication** |
| --- | --- |
| Service A calls Service B | Service A publishes an event |
| Service A knows the destination | Service A knows the Kafka topic |
| Often synchronous | Commonly asynchronous |
| Receiver must be available for an immediate response | Consumer can process the event later |
| More direct dependencies | Looser coupling |


## **5. How to explain Kafka in simple terms (interview answer)**
You can use this definition:
"Apache Kafka is a distributed event-streaming platform that allows multiple applications or microservices to communicate through events without directly depending on each other. Instead of one service calling another service directly, it publishes an event to Kafka, and other interested services consume that event independently."
**Remember this important difference:**
- REST API: I want to talk directly to a particular service.
- Kafka: I want to publish an event, and whoever is interested can consume it.
That's the main problem Kafka helps solve: **tight coupling and direct dependencies between services.**

