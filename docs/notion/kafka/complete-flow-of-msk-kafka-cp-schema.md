# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466XGHQZUX2%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T013608Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEP7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIA5UUU02CMG4Q3fOBcRQv%2Bm4RaNvEIA%2BwXwcVHDv4943AiBpMmGintuitOPEvnG7ms46YxD3WMe2omb5Q3hDFyRBECqIBAjH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIM8%2F1gogYSQZaZ7QNQKtwD8EoHwdp1m8NOI27zdDEjibivyxKv5YY4W90jFDuHYZ39iAWVkjN%2B97gC6pFRcSkUIIBL94XZZvVXXrnmLd24Pbe54WUDKOJw1eGiGjF%2BbpFcRus7SCWc6qw%2B5qlr7f2Klmwao8Koc1QiAh%2FjWuo0HN1%2B8LDqGr%2FTcvh4F%2B0QtJI%2BhCpdZnRREJoWnFfocnil4iG4556h4D8NntnaQDc77GuBuHEFJTlbFvi9jF852UDQsInlh%2FXtNy5ADQpHI4Wr2cBf6uzLpdGrU76C4OfEeQLimTB03acCHzTlJUNh4%2FUUF%2BVmA4hq12KsWAcZTvCZdAhFUSr1RT3h6irxtwkNKBYMUL6Zd1OhOYn8XRWd3wXOCBt0oMu58YGm3hIW1IaDQBqn2ivvdyhTRcN8bzyt8Je%2BV7xXrS%2Fn6oCpOX2vaZfus4KUEcdIWnCaF%2BwublRlqrrbCPSdBXSFE0ilYDV6u%2Bo8L3S1NNiUDKxngZ8YNEn0PYIYX5Aj409UjKZV6Ypg0uCkYk11GqyQbl0eDP6El1wxbXErmyNcWLDdWUz%2F2IpvPYl%2FqpjxJwF2imBz5K5spS8Nc1cDRKKTIXyMYHY5baqeng57VK92JFD%2BRXboF5KzNZCMwaDA9e%2BgKMYwqtSi2AY6pgE1XYWN4zCO%2FC6QcS7nPOW54hqS%2F1Qs7Z%2Bzwp%2BIO1iSeM2YAVjkcxEXd2tjz628nLNQ54NBm%2B59fn51FpiLZu4Q%2Bntm8jU95rMtaYILosUZEQdQ9yTpjGt%2BjecCpH93HmsmjzH2zx16bRG0rcIB%2FURWDzt3qUMcrsXI9U0uRrH3jUYYP%2BXeUjBpt4Wi%2B62qbc4U8dvDPgVoTP1kAMQyd7vMbdqLA7bN&X-Amz-Signature=5787fe39b0535c3cd3586b47b125f732cc8b0a746d12ed092d1dec2c89eb9e4b&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466XGHQZUX2%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T013608Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEP7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIA5UUU02CMG4Q3fOBcRQv%2Bm4RaNvEIA%2BwXwcVHDv4943AiBpMmGintuitOPEvnG7ms46YxD3WMe2omb5Q3hDFyRBECqIBAjH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIM8%2F1gogYSQZaZ7QNQKtwD8EoHwdp1m8NOI27zdDEjibivyxKv5YY4W90jFDuHYZ39iAWVkjN%2B97gC6pFRcSkUIIBL94XZZvVXXrnmLd24Pbe54WUDKOJw1eGiGjF%2BbpFcRus7SCWc6qw%2B5qlr7f2Klmwao8Koc1QiAh%2FjWuo0HN1%2B8LDqGr%2FTcvh4F%2B0QtJI%2BhCpdZnRREJoWnFfocnil4iG4556h4D8NntnaQDc77GuBuHEFJTlbFvi9jF852UDQsInlh%2FXtNy5ADQpHI4Wr2cBf6uzLpdGrU76C4OfEeQLimTB03acCHzTlJUNh4%2FUUF%2BVmA4hq12KsWAcZTvCZdAhFUSr1RT3h6irxtwkNKBYMUL6Zd1OhOYn8XRWd3wXOCBt0oMu58YGm3hIW1IaDQBqn2ivvdyhTRcN8bzyt8Je%2BV7xXrS%2Fn6oCpOX2vaZfus4KUEcdIWnCaF%2BwublRlqrrbCPSdBXSFE0ilYDV6u%2Bo8L3S1NNiUDKxngZ8YNEn0PYIYX5Aj409UjKZV6Ypg0uCkYk11GqyQbl0eDP6El1wxbXErmyNcWLDdWUz%2F2IpvPYl%2FqpjxJwF2imBz5K5spS8Nc1cDRKKTIXyMYHY5baqeng57VK92JFD%2BRXboF5KzNZCMwaDA9e%2BgKMYwqtSi2AY6pgE1XYWN4zCO%2FC6QcS7nPOW54hqS%2F1Qs7Z%2Bzwp%2BIO1iSeM2YAVjkcxEXd2tjz628nLNQ54NBm%2B59fn51FpiLZu4Q%2Bntm8jU95rMtaYILosUZEQdQ9yTpjGt%2BjecCpH93HmsmjzH2zx16bRG0rcIB%2FURWDzt3qUMcrsXI9U0uRrH3jUYYP%2BXeUjBpt4Wi%2B62qbc4U8dvDPgVoTP1kAMQyd7vMbdqLA7bN&X-Amz-Signature=c8e4264b40e935261e6aa64170560f769d11700646083ad753722d9d66d677cd&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

