# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZCHEHIJ2%2F20261126%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261126T163921Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEPj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQDWvJSRjffkjQOxhbD4FFyQHHsvxXs1JyBVt5WYX7FjogIhAIkob3qUs6JrrlPUPKgZADEDPCRyPdKn8crrt0jRxbMHKogECMH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMNjM3NDIzMTgzODA1IgwZir3djmf8QoNfGSgq3AMkUsk%2FggOva6Qydzu4pHKoqBX15mI1qcs9P%2FiRuhWlUz%2BLmhxcJpUK5%2BhPYs6cH2iImMP24ibzO6hWYpIwVRurFoX5SOf9jMk8CmrYgb7OIRQMRXWsO0n1c7JUXhDf%2FooAUclpBLnDYOoO74Knz%2Bq54BAcHWFq1H130rLzS9qPvfqM2ZJGPTkdnfDX8RHk%2BPj3Wi8qAoDYfbMlN4Xbn4DcTgXK4NlzadOOedmnN5fgI9u6YxH1JQ86Fxmtwf6gTEPVFlU8CnvUaeOhRjEAtQHMxNQXTrxqhRPKQWu08IwdPm7%2FWruymYEEum3eQ0heD3fIDRZTDUjBwrzBfJlUOXn9dQWSAMVyWa1JN0XWaySNeOgL%2FGGYDnSZbkvQngyidrgQWqsGhYJTfTB6RTRxuPWi5MMwNmnlec0vk9v%2ByEPANkohMkUSgVniwXZd566vjdE7bb7vAGCqBJS%2FndgURaAhZNpNb4cqouH8aenKpc%2BuC9oLoZh1FQY6%2BkkOuuuWaYHmj296ptQFng1xzbL5Z%2FC8EY2c6MgFYvK17kaCAdtPlh9aLhw1v5PAGO%2Bv255Qzeu5r%2FpZHko%2FOrCpVgLty2UjOc0v7qu3tKeI%2B%2BZTSnWaMVtlpBs%2FU1Tm2Wz7ljCOrqHYBjqkAWA2Pn%2F8HScUbosK6EmI%2F9zA2bXf50x%2F1pqKZhstyZmoKk9mo%2BF6l8Ry5b9TOOAT2yLcweK%2B%2F1D3hfo%2FPORf%2F8KaZyHwtZM3hzQa6V%2F2K7wadnyb70KJ4TlGQCx6RgU2dss%2B9Q86nl%2FZFfa6cHE6lbcoxeYVLhdjg75P%2Fhg6c9QKWKYQy%2FBM5u7HCJtwiUX1UjyhWzl7WGK%2Bs81b%2BjHqkJmExmrU&X-Amz-Signature=5a8bb89abfbde2055ae4d5ee9927a8c686b56e093739d2a65a1d09096fb40c15&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZCHEHIJ2%2F20261126%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261126T163921Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEPj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQDWvJSRjffkjQOxhbD4FFyQHHsvxXs1JyBVt5WYX7FjogIhAIkob3qUs6JrrlPUPKgZADEDPCRyPdKn8crrt0jRxbMHKogECMH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMNjM3NDIzMTgzODA1IgwZir3djmf8QoNfGSgq3AMkUsk%2FggOva6Qydzu4pHKoqBX15mI1qcs9P%2FiRuhWlUz%2BLmhxcJpUK5%2BhPYs6cH2iImMP24ibzO6hWYpIwVRurFoX5SOf9jMk8CmrYgb7OIRQMRXWsO0n1c7JUXhDf%2FooAUclpBLnDYOoO74Knz%2Bq54BAcHWFq1H130rLzS9qPvfqM2ZJGPTkdnfDX8RHk%2BPj3Wi8qAoDYfbMlN4Xbn4DcTgXK4NlzadOOedmnN5fgI9u6YxH1JQ86Fxmtwf6gTEPVFlU8CnvUaeOhRjEAtQHMxNQXTrxqhRPKQWu08IwdPm7%2FWruymYEEum3eQ0heD3fIDRZTDUjBwrzBfJlUOXn9dQWSAMVyWa1JN0XWaySNeOgL%2FGGYDnSZbkvQngyidrgQWqsGhYJTfTB6RTRxuPWi5MMwNmnlec0vk9v%2ByEPANkohMkUSgVniwXZd566vjdE7bb7vAGCqBJS%2FndgURaAhZNpNb4cqouH8aenKpc%2BuC9oLoZh1FQY6%2BkkOuuuWaYHmj296ptQFng1xzbL5Z%2FC8EY2c6MgFYvK17kaCAdtPlh9aLhw1v5PAGO%2Bv255Qzeu5r%2FpZHko%2FOrCpVgLty2UjOc0v7qu3tKeI%2B%2BZTSnWaMVtlpBs%2FU1Tm2Wz7ljCOrqHYBjqkAWA2Pn%2F8HScUbosK6EmI%2F9zA2bXf50x%2F1pqKZhstyZmoKk9mo%2BF6l8Ry5b9TOOAT2yLcweK%2B%2F1D3hfo%2FPORf%2F8KaZyHwtZM3hzQa6V%2F2K7wadnyb70KJ4TlGQCx6RgU2dss%2B9Q86nl%2FZFfa6cHE6lbcoxeYVLhdjg75P%2Fhg6c9QKWKYQy%2FBM5u7HCJtwiUX1UjyhWzl7WGK%2Bs81b%2BjHqkJmExmrU&X-Amz-Signature=dbf1f93a297fb9a416a8c617b49c383ec22cfe0e3a1cc963623fd4116f235879&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

