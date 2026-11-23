# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466YBLFPS7S%2F20261123%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261123T092832Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDn53qob5wfJjnmzHvQZGmYmxos%2FbGGkSH1vXVp7VY5DwIgZQD7hXv4%2BEY3o7Pwyn3tvO6Xn0zLoDhC%2F7NQEuOhgyQq%2FwMIchAAGgw2Mzc0MjMxODM4MDUiDAcIm5pp%2B8SyLPRjdSrcA1un4aOYgwfO4pWjgI8G01mkqTVCnBfA6xTTf%2FeLb90ou0H0NPHrpennUlFyYHVPOxfK8rmTDvG6eCgCd5v%2FXYd4m3vS%2B7o%2Beorxj00vrgKqndStl3Ql120MghWHW37ZD3lm9Cht9VIi4cS4wxKUvbgaBK9bmnfsOvw%2B1K14xs30tbEXr7UMOZEW4re09KsYaYwRxt%2B3cbnBQeCoUGfiVk6yCXJYeLZsS491NxrauFru0Pi2Xf4qF0MDv6FjWU8nLnd%2FegMkVcqlh%2BYh3W6g8TMz%2FN9MUxd%2B7nTlIkk%2BSE%2FlR6WeJU9WAy81093WaI7X32j0PfZcoq6STlNnldmFYHg%2FPQIe%2FuBA3Q5mqHaqoVlTzkVKs2dB%2B8ZJMzZ2Yvh09V%2FAhg1dA%2Fbu9hII3NKEEx2FUJPueCbh4eBs42OzYmBuOOA8uUwtqUKUW7EPvRjY5yjfBZt5iDJx9e84WYRWiy%2B%2Fh9HIv7l8ib6lPGFhSjoOB%2BxRhtPoJ6gbh0Cm04dtTd8ssvJraDaL6GzdfjbIuX0Fptt1B%2BDwZgqpWJkWKoqBtLtE9rr644vJTXhQ8nl2r%2F%2FTql2ygWKCqwP7nWwp8FXNy80u7guO2qm%2F889VDReQ6IgvAINwmkuqfuCnMNOFkNgGOqUBv8JTbct3LH4DRDPjCgmZ73pxmGXHWHCJVzVqsShWou1GsBiVvYNWl4ej64aUnoLYucSULxI%2BYKHYYyjyP6DkxEo7JAVw%2BtJE4KpH91mDNd%2BKGYFZ5cUXVWc7GwP%2BkyJnlKE9ztio4dLdf8eYbNrjVzWf7tXDpAZH9fA5asMz9U0qHmsSBcHUtlZsKCmU%2BjYqp%2BXgj84LUX%2Ftg6xOtcWfeUUjfc3w&X-Amz-Signature=107cff7a5520f7c52e6fda303f91e3c355861fa3817ad9b8acdbd4a8f89d3041&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466YBLFPS7S%2F20261123%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261123T092832Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDn53qob5wfJjnmzHvQZGmYmxos%2FbGGkSH1vXVp7VY5DwIgZQD7hXv4%2BEY3o7Pwyn3tvO6Xn0zLoDhC%2F7NQEuOhgyQq%2FwMIchAAGgw2Mzc0MjMxODM4MDUiDAcIm5pp%2B8SyLPRjdSrcA1un4aOYgwfO4pWjgI8G01mkqTVCnBfA6xTTf%2FeLb90ou0H0NPHrpennUlFyYHVPOxfK8rmTDvG6eCgCd5v%2FXYd4m3vS%2B7o%2Beorxj00vrgKqndStl3Ql120MghWHW37ZD3lm9Cht9VIi4cS4wxKUvbgaBK9bmnfsOvw%2B1K14xs30tbEXr7UMOZEW4re09KsYaYwRxt%2B3cbnBQeCoUGfiVk6yCXJYeLZsS491NxrauFru0Pi2Xf4qF0MDv6FjWU8nLnd%2FegMkVcqlh%2BYh3W6g8TMz%2FN9MUxd%2B7nTlIkk%2BSE%2FlR6WeJU9WAy81093WaI7X32j0PfZcoq6STlNnldmFYHg%2FPQIe%2FuBA3Q5mqHaqoVlTzkVKs2dB%2B8ZJMzZ2Yvh09V%2FAhg1dA%2Fbu9hII3NKEEx2FUJPueCbh4eBs42OzYmBuOOA8uUwtqUKUW7EPvRjY5yjfBZt5iDJx9e84WYRWiy%2B%2Fh9HIv7l8ib6lPGFhSjoOB%2BxRhtPoJ6gbh0Cm04dtTd8ssvJraDaL6GzdfjbIuX0Fptt1B%2BDwZgqpWJkWKoqBtLtE9rr644vJTXhQ8nl2r%2F%2FTql2ygWKCqwP7nWwp8FXNy80u7guO2qm%2F889VDReQ6IgvAINwmkuqfuCnMNOFkNgGOqUBv8JTbct3LH4DRDPjCgmZ73pxmGXHWHCJVzVqsShWou1GsBiVvYNWl4ej64aUnoLYucSULxI%2BYKHYYyjyP6DkxEo7JAVw%2BtJE4KpH91mDNd%2BKGYFZ5cUXVWc7GwP%2BkyJnlKE9ztio4dLdf8eYbNrjVzWf7tXDpAZH9fA5asMz9U0qHmsSBcHUtlZsKCmU%2BjYqp%2BXgj84LUX%2Ftg6xOtcWfeUUjfc3w&X-Amz-Signature=b635fa120c8a310b02cad0aaa0a761c4b8a6babec4c0b9568b8f0835c412f9b7&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

