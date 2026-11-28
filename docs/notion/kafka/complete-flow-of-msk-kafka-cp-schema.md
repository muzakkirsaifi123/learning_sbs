# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SXEKH2BA%2F20261128%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261128T151725Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjECYaCXVzLXdlc3QtMiJGMEQCIBaB%2FsMVAenaGzxxryUyawFCFIhjTb4z5DvwMRoU1HLsAiBAiMxi1BH0IndG2fhf60jnmI3Kqe9aHl99MnteH5RnxCqIBAju%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMs7RNn5YZzMCa7Dr3KtwDSyKxCln1A3qgOM%2Bl2w%2B0sG1XGNEFxJlkBWAf7yObsNN4uim8Qi6ppueRtx5BBoKX3Ysc8xvkZaGdByYUExFi6NUoA4zGnm2s71rXnneBYHCgBcqLGc0r5mNPk6V3%2FFgAH%2B0uvBA%2B6bZLBDNoTASvshNCd0GNg8PMU3lmgKgIrmeeTzmAnAcNqJoPB%2FPfgFDy77JJBcnAuaj9gMfkMjB0CT7QZFMANMWcerpWfbf5%2FIlkYhJEfCJwIvb26oCzriQGmhK4vLcLANA4Q8fAUtzW5qUrVWNgTAEwCEe12DPaGNXxXul%2B0rbzmQ8ShxH2Jwgdfd3lhbG9fMNStHnfty57zpWopf8QsmQ22%2B%2F6eKUG9LcXmeo3BRIPmpdS3x0iwzib4NpEFp3V6VnT33Ncg7IAyy4%2FEJ6b%2FEnZZEHi4cVcgLn%2FgI6yOO2TFFcQqQgFuYMz1nCCy1BB8zZsj9MqqWBTrKIV8DwU6bHRJDst8s%2F6bkEy7FBNOW4OfRnBWe375G5N3idYk4UqyFAxZM9mnnjRNL63YwjWCP21g%2FJNVixeMkEOQxicC%2Fvvz2Z2%2BuY5NSo4sQQfr4kgG9LI9x2rsDNS4zS2ksDdyaJIVU%2BE7C6lo8MvhWP%2BCVqwu72bhaww9K2r2AY6pgFQl64H3ofB%2FJaFeNb%2B3AwdzXQryLXZCXfeqakYJuNF20Lot3%2BIvhQkvXzkiSJi2DDXnpOVLzpvu%2Fe5AoUuIsWvJBPDaw9l71gpVVoOo6KeiE%2FKX8prizDeFJTOaMYdocAcKN9BCnYerK%2Fs%2BFzGeOL%2Fn4J4xB%2BU31nbB4BAYix14LrLCPC6%2F1eD8u4%2FJR%2BH9pcLie%2FH3jy%2BMh%2BYyyYym94doAxdE%2BTT&X-Amz-Signature=00b876f55505099d876b65208aacac7130d2ebb516c7e46f549e50936114b6ec&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SXEKH2BA%2F20261128%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261128T151725Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjECYaCXVzLXdlc3QtMiJGMEQCIBaB%2FsMVAenaGzxxryUyawFCFIhjTb4z5DvwMRoU1HLsAiBAiMxi1BH0IndG2fhf60jnmI3Kqe9aHl99MnteH5RnxCqIBAju%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMs7RNn5YZzMCa7Dr3KtwDSyKxCln1A3qgOM%2Bl2w%2B0sG1XGNEFxJlkBWAf7yObsNN4uim8Qi6ppueRtx5BBoKX3Ysc8xvkZaGdByYUExFi6NUoA4zGnm2s71rXnneBYHCgBcqLGc0r5mNPk6V3%2FFgAH%2B0uvBA%2B6bZLBDNoTASvshNCd0GNg8PMU3lmgKgIrmeeTzmAnAcNqJoPB%2FPfgFDy77JJBcnAuaj9gMfkMjB0CT7QZFMANMWcerpWfbf5%2FIlkYhJEfCJwIvb26oCzriQGmhK4vLcLANA4Q8fAUtzW5qUrVWNgTAEwCEe12DPaGNXxXul%2B0rbzmQ8ShxH2Jwgdfd3lhbG9fMNStHnfty57zpWopf8QsmQ22%2B%2F6eKUG9LcXmeo3BRIPmpdS3x0iwzib4NpEFp3V6VnT33Ncg7IAyy4%2FEJ6b%2FEnZZEHi4cVcgLn%2FgI6yOO2TFFcQqQgFuYMz1nCCy1BB8zZsj9MqqWBTrKIV8DwU6bHRJDst8s%2F6bkEy7FBNOW4OfRnBWe375G5N3idYk4UqyFAxZM9mnnjRNL63YwjWCP21g%2FJNVixeMkEOQxicC%2Fvvz2Z2%2BuY5NSo4sQQfr4kgG9LI9x2rsDNS4zS2ksDdyaJIVU%2BE7C6lo8MvhWP%2BCVqwu72bhaww9K2r2AY6pgFQl64H3ofB%2FJaFeNb%2B3AwdzXQryLXZCXfeqakYJuNF20Lot3%2BIvhQkvXzkiSJi2DDXnpOVLzpvu%2Fe5AoUuIsWvJBPDaw9l71gpVVoOo6KeiE%2FKX8prizDeFJTOaMYdocAcKN9BCnYerK%2Fs%2BFzGeOL%2Fn4J4xB%2BU31nbB4BAYix14LrLCPC6%2F1eD8u4%2FJR%2BH9pcLie%2FH3jy%2BMh%2BYyyYym94doAxdE%2BTT&X-Amz-Signature=54cbc0851b5c53f784e8c74afc3fa32d8e907376843faabc92646187926841ee&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

