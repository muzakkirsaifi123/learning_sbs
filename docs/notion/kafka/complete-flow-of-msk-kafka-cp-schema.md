# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466UORJ3N2D%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T115502Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAkaCXVzLXdlc3QtMiJHMEUCIQD7C3jpR6UTYtBScAVP0cej%2FdLwpD3spFFhDZGz0GodswIgNU%2FNg%2FI7lKSk0Ma66aMOZURG%2F6Ay1sRzRiz3EDWE7UQqiAQI0v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDAeVX%2BUebh%2Bh8QFkJyrcAxNiPsTWpvHFe%2BBa%2FK04%2BivgK0Hk%2FegOB6tyYg%2BzHwE9bjf7hi8kSpS1yggwmRUduAhMxXzEpd%2FVqbDBS5NVfE2xKs5G%2BYxGpnwk1ffqAoRzqekbs8QdxtXhtLgxyuGx68nrXZ1hX8HOAolReDc9UXJzt7K0XDdveNuz1hL76sVyyqEUTkp2cyl0nGFkq04vfty%2FP2gz%2BVMUBBADb%2B2oDnyzYjeP3kZqIXw1g%2Ft9ArDlKqUkC2%2FwZVdmCYN%2Bcq6aTsCH%2F7l1G5Xx76jRMCc8YojevHHk5FTNp04dLU%2FSl5XTokSdY9FP4qHgrjBVM5druw2BuCKEq1aWOLy1lnnJ0zqN%2BQuDGtO2wDs3RRHm3vVEq%2FZe3YZjsmrx56k3lRACnPcx%2BRiGTc84yoYOF4sB617b3yq6BtmIIUpNleVfHqZZ1jCyd4hK3Zipbn4dDIQ%2By4cLCVRzo5c7kuam6amuP6I31EuWUXO4ohRV9PrFX4NtaMG%2FxP4xIb%2FJpNVlO5EMn4k8%2Bf0GJ0WSFX8PCj0jpJm4Mej%2B%2F3uisQNQZhJBjvveQXrdKYz53wC%2B1WgPirc%2FvI1w%2BhUJBD0EIZ7bSEyIGAwXod2wAKgng6LkI1QtLIvT%2Bk7bPxKs5knGxA4WMJ%2BEpdgGOqUBvLgaK5KviscRLQCy%2FYlGsnZ2aumULDGJvMv5svNAjpZofb78tfsfOsS0%2F4YjyP6eRsuFwE02D41o%2BIVioskG1lshCdbrv%2FtAlIoYs%2FnGCj7FfHhI3SstSovb9k8nwy1eAKj6w6ZsqS%2BcgVJn%2FXMh1GwRc9uH8itvfNh%2FqhOOdQmrex3gKvfCQQve00P09kqwLq%2BYuYaCEYK743mByQW8dRt%2B%2BohB&X-Amz-Signature=973a926e33e74f79cf8258cad2cf820b3dac4f23cb624a3834438487e08aa79c&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466UORJ3N2D%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T115502Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAkaCXVzLXdlc3QtMiJHMEUCIQD7C3jpR6UTYtBScAVP0cej%2FdLwpD3spFFhDZGz0GodswIgNU%2FNg%2FI7lKSk0Ma66aMOZURG%2F6Ay1sRzRiz3EDWE7UQqiAQI0v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDAeVX%2BUebh%2Bh8QFkJyrcAxNiPsTWpvHFe%2BBa%2FK04%2BivgK0Hk%2FegOB6tyYg%2BzHwE9bjf7hi8kSpS1yggwmRUduAhMxXzEpd%2FVqbDBS5NVfE2xKs5G%2BYxGpnwk1ffqAoRzqekbs8QdxtXhtLgxyuGx68nrXZ1hX8HOAolReDc9UXJzt7K0XDdveNuz1hL76sVyyqEUTkp2cyl0nGFkq04vfty%2FP2gz%2BVMUBBADb%2B2oDnyzYjeP3kZqIXw1g%2Ft9ArDlKqUkC2%2FwZVdmCYN%2Bcq6aTsCH%2F7l1G5Xx76jRMCc8YojevHHk5FTNp04dLU%2FSl5XTokSdY9FP4qHgrjBVM5druw2BuCKEq1aWOLy1lnnJ0zqN%2BQuDGtO2wDs3RRHm3vVEq%2FZe3YZjsmrx56k3lRACnPcx%2BRiGTc84yoYOF4sB617b3yq6BtmIIUpNleVfHqZZ1jCyd4hK3Zipbn4dDIQ%2By4cLCVRzo5c7kuam6amuP6I31EuWUXO4ohRV9PrFX4NtaMG%2FxP4xIb%2FJpNVlO5EMn4k8%2Bf0GJ0WSFX8PCj0jpJm4Mej%2B%2F3uisQNQZhJBjvveQXrdKYz53wC%2B1WgPirc%2FvI1w%2BhUJBD0EIZ7bSEyIGAwXod2wAKgng6LkI1QtLIvT%2Bk7bPxKs5knGxA4WMJ%2BEpdgGOqUBvLgaK5KviscRLQCy%2FYlGsnZ2aumULDGJvMv5svNAjpZofb78tfsfOsS0%2F4YjyP6eRsuFwE02D41o%2BIVioskG1lshCdbrv%2FtAlIoYs%2FnGCj7FfHhI3SstSovb9k8nwy1eAKj6w6ZsqS%2BcgVJn%2FXMh1GwRc9uH8itvfNh%2FqhOOdQmrex3gKvfCQQve00P09kqwLq%2BYuYaCEYK743mByQW8dRt%2B%2BohB&X-Amz-Signature=5c01da49eb7c866498014bc0f8065c4407048275e94606d98328cc48ed5f6bb7&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

