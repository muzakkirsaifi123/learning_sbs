# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4663E24WD5W%2F20261125%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261125T074941Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjENj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCICnvCvxHOEzvGi8cfAIJ8KlsmADIKik90WBY0X6wJwhOAiEA%2FTBaaFTqFnpSZv2zCgFiiYFnN3C5twwTE8p2ZYF0hVwqiAQIoP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDJF1Bh4iU5TedM50XircA570YD0WtCQKg%2FtNq6U0XoTWVMxmYU8pcrCG7FgNgKhyUm8e4ie%2B5KMtE9mlko8dROKA%2FpV3Tr%2Bmy1oGZiCXtu8lw3qDcEbzvIW8%2F5fDkGNb9X0KPcRDYW7uaQG5qtg0RRyKQV0OF1G43JPBVXD32h1Wa2TZasbzqp8zbB3OJpMjRnQfvfPWnHRg7jNRWCTWZb3BDry4Ir6qTHaEjAfU1MvxzJG4WvvcjJN1JckZ%2Be2emcUB4x81yiGYkzbwhGV7wITvyH9iWKPZ6CiBN0Tfa5FIR%2F1p7mlSp%2BF%2BiSWGBsNNj8y08FeH1LMiR%2FcKs8ZpEtZN7MBwwG27tOjFyeGsN2bVvIbghXTsRxtnWBE9w1227nGhAEioj0vOeXStZdhCHuh17vV26TVYm2uYn87GtYSkqa2x6t4XW%2F9ISeOHfZCeueCjrZJXfFHhbQCqClsc2YyyQt1Cc9wJZSL238vITc%2FnBF4jWTmh9UJd7BHQFBkIv03MdYRq7pxa0Ic2zdtw2ba1yVZx1wlnN4PLEC9rN2xjQaYjnV8k4aWOVhmA1yAzUQ4eetyDzn%2B8SCIrGP6fD2D2lxwSz2MGTYOi7ncdD1T781NhWRzJDUI6hlBYqJZCBd4eW140M3TnEZFBMNOZmtgGOqUBj6eiqrmHQgfjEr1YKl6Qnnb3YXS%2FGiZzab4uAujS5Ker0Yotq0EedIgI3a5H3vy6CyGyPt3a3kTGfsNYxk5OP4k7eGOeCL2eJuALgsWTgR%2FThUr3iUbEXnG%2B45c5pfLPfz7aroBnkIgEgsApZwqB%2B7yv2oXBzlZRrmOYYDdrpEJeUabNRsYWTT6MfmosagZLE2E1%2Fi%2B9Nt4F%2FIhiHwd5DO0DZnNR&X-Amz-Signature=69fdd86003f05073e459edad93454bc108fae4d94b403a61d1c1b69e4fcef02b&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4663E24WD5W%2F20261125%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261125T074941Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjENj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCICnvCvxHOEzvGi8cfAIJ8KlsmADIKik90WBY0X6wJwhOAiEA%2FTBaaFTqFnpSZv2zCgFiiYFnN3C5twwTE8p2ZYF0hVwqiAQIoP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDJF1Bh4iU5TedM50XircA570YD0WtCQKg%2FtNq6U0XoTWVMxmYU8pcrCG7FgNgKhyUm8e4ie%2B5KMtE9mlko8dROKA%2FpV3Tr%2Bmy1oGZiCXtu8lw3qDcEbzvIW8%2F5fDkGNb9X0KPcRDYW7uaQG5qtg0RRyKQV0OF1G43JPBVXD32h1Wa2TZasbzqp8zbB3OJpMjRnQfvfPWnHRg7jNRWCTWZb3BDry4Ir6qTHaEjAfU1MvxzJG4WvvcjJN1JckZ%2Be2emcUB4x81yiGYkzbwhGV7wITvyH9iWKPZ6CiBN0Tfa5FIR%2F1p7mlSp%2BF%2BiSWGBsNNj8y08FeH1LMiR%2FcKs8ZpEtZN7MBwwG27tOjFyeGsN2bVvIbghXTsRxtnWBE9w1227nGhAEioj0vOeXStZdhCHuh17vV26TVYm2uYn87GtYSkqa2x6t4XW%2F9ISeOHfZCeueCjrZJXfFHhbQCqClsc2YyyQt1Cc9wJZSL238vITc%2FnBF4jWTmh9UJd7BHQFBkIv03MdYRq7pxa0Ic2zdtw2ba1yVZx1wlnN4PLEC9rN2xjQaYjnV8k4aWOVhmA1yAzUQ4eetyDzn%2B8SCIrGP6fD2D2lxwSz2MGTYOi7ncdD1T781NhWRzJDUI6hlBYqJZCBd4eW140M3TnEZFBMNOZmtgGOqUBj6eiqrmHQgfjEr1YKl6Qnnb3YXS%2FGiZzab4uAujS5Ker0Yotq0EedIgI3a5H3vy6CyGyPt3a3kTGfsNYxk5OP4k7eGOeCL2eJuALgsWTgR%2FThUr3iUbEXnG%2B45c5pfLPfz7aroBnkIgEgsApZwqB%2B7yv2oXBzlZRrmOYYDdrpEJeUabNRsYWTT6MfmosagZLE2E1%2Fi%2B9Nt4F%2FIhiHwd5DO0DZnNR&X-Amz-Signature=1e6aa4d2dd076579baabb555598c8e592d664f34cf33adf70e174d8c86cc900e&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

