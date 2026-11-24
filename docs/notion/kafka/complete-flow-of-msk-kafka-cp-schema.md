# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466TGWQCUJF%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T234835Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIHVJTMfSM0R9yr3rt48kAModnWxG8DeMYSvqwZ4nUU10AiAevSaVu5TgPhbUdsAaiJLlaf0sRqwew0uyVHrqitoVeSqIBAiZ%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMFKaeSd5eK6gI1IGZKtwDPPVCl9Z5t7cJxTR1MjYoS0vD668cXGDw21AWR1HGTWiHWge93KFlBfvnSMWhwYs9dxlX78GzAOOEpPdiVvODCi6ic9S806mBL2xUHy8vdSb2rh5PXhteW2VxEabMS6z7w5NsN2YWAObiCW0UciDE0Ef2q5CPtlLtnmcHSOr3MOGcOC%2Be08cpBp8LKlDhHnIynemQTuen%2FRtPjasZb1x%2FEzXCj6EWERCtotm4OqIYK%2Blifd6uE2WS3FI3EJqPncFdYHly197UmNjz79322wYGedssm3b51tRy4YfALqX9%2BAOrGGeTjYuh0RtNkeTQTgo60S4DX3PFvI9R5%2FUIC%2Fzqp2gEMeYjAq%2FOrRBWwgz%2BYW3A0atK8%2B0NV2PXsgoo0pexZ5gsFKtoNuYgQKCNNzZQDd0dKaUe3HrN4RJeR6UQGd3Zf%2FeZr6mPa9rEQ8aZLD87EbVGvQzBrNDAsQ4BGHOSwrxchwHRylEjy3bN%2FfUJXcJKze8uDF56aufPqKmje01IUdF%2Btmig4dWIs%2FbaPqtLv%2FaMvKjzNy3YaCf%2B9guXr0aV6BXVU69efBV%2BeUGmGrqMeD5J8%2BFCe8eSCauwSmQ58fXv1TPSXdl7qc3YRGf1qLfIRjjN%2F0%2F8Ljnpqc8w5cOY2AY6pgHZRfuqAblB7YKVxjto7Fg9twW3R8FbM0ZRoGV%2F2RUbTjqdPJBk4x5WWJakqp%2BMCmfvaYNA2f7FuCznxRzKNWhK8%2BOa83pRQUtlqyWGY%2FV4KRL45Tb9fmx%2FcgunFA6CNH%2FZ9r7CQtH%2B8E5osCKm0WfGA47M46CgYNIvojKZdbv4FsTDUUHx7aWmAbwz0LA8%2F0klOgsqYD2dALQku%2B2qfrR1ZlNpJyyn&X-Amz-Signature=5ae1774be2b6cabfbecfba122b1a19dd8e3a62a3047e62adf5b61e7bb336e272&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466TGWQCUJF%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T234835Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIHVJTMfSM0R9yr3rt48kAModnWxG8DeMYSvqwZ4nUU10AiAevSaVu5TgPhbUdsAaiJLlaf0sRqwew0uyVHrqitoVeSqIBAiZ%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMFKaeSd5eK6gI1IGZKtwDPPVCl9Z5t7cJxTR1MjYoS0vD668cXGDw21AWR1HGTWiHWge93KFlBfvnSMWhwYs9dxlX78GzAOOEpPdiVvODCi6ic9S806mBL2xUHy8vdSb2rh5PXhteW2VxEabMS6z7w5NsN2YWAObiCW0UciDE0Ef2q5CPtlLtnmcHSOr3MOGcOC%2Be08cpBp8LKlDhHnIynemQTuen%2FRtPjasZb1x%2FEzXCj6EWERCtotm4OqIYK%2Blifd6uE2WS3FI3EJqPncFdYHly197UmNjz79322wYGedssm3b51tRy4YfALqX9%2BAOrGGeTjYuh0RtNkeTQTgo60S4DX3PFvI9R5%2FUIC%2Fzqp2gEMeYjAq%2FOrRBWwgz%2BYW3A0atK8%2B0NV2PXsgoo0pexZ5gsFKtoNuYgQKCNNzZQDd0dKaUe3HrN4RJeR6UQGd3Zf%2FeZr6mPa9rEQ8aZLD87EbVGvQzBrNDAsQ4BGHOSwrxchwHRylEjy3bN%2FfUJXcJKze8uDF56aufPqKmje01IUdF%2Btmig4dWIs%2FbaPqtLv%2FaMvKjzNy3YaCf%2B9guXr0aV6BXVU69efBV%2BeUGmGrqMeD5J8%2BFCe8eSCauwSmQ58fXv1TPSXdl7qc3YRGf1qLfIRjjN%2F0%2F8Ljnpqc8w5cOY2AY6pgHZRfuqAblB7YKVxjto7Fg9twW3R8FbM0ZRoGV%2F2RUbTjqdPJBk4x5WWJakqp%2BMCmfvaYNA2f7FuCznxRzKNWhK8%2BOa83pRQUtlqyWGY%2FV4KRL45Tb9fmx%2FcgunFA6CNH%2FZ9r7CQtH%2B8E5osCKm0WfGA47M46CgYNIvojKZdbv4FsTDUUHx7aWmAbwz0LA8%2F0klOgsqYD2dALQku%2B2qfrR1ZlNpJyyn&X-Amz-Signature=24d6ea8fe6f3161bc2284bdab9c132ec85ffcc1a4b1ed5ca3c04be090ef85939&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

