# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466Z4HACVQQ%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T020356Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIFSPWPn%2FZGvg3AcNe3vyEydoQeKV3%2Bx9iroOZXkMwT9eAiADMFajHJ4%2F2Wp%2FzNvrk%2FHjNFcdKcqlzljFUmBQJqZ2EiqIBAiB%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMxmaFfoDt7HvcAebrKtwDUa2UnD%2BPnfmSkSSPjfpbo9CU953ME22DZx5CXdbOt0dvBrfifuLbJKR%2FkO2m9iU546C%2BdJaPHQL8K52otbOIsHgXGYcaa4WAGsYw7F7drPkHPjhFyLjWYsxNIKJur5wOXYbdlSumC9NxZRKoCsyWqlDXmC%2FsIBMXGOLuJ5fPZTSL41bjEM1cMyB5mrcQSXXgb7u35ABYk%2FaUYWflNdq1FLc%2B2pdv3JLBpi2vkZ8XTexe7uaeN57TT1queY7fxu6zlbOqsRjP6dwkgppkfUZUAN9%2BMJkIpzRHkIWCorT6J1%2FnLpfsuWpND87bATZJk9sKw4oWTU5ypB%2FVB32hLCu6ckwt6Z%2Bw6YvH1wwVJJVv7p8vKshi%2BXmKEvlYqM%2Bi4%2BS3719zYg0UMIcYvIXk7Is9HhQ5D4KyM0h1L2JMwDo9%2F5MPnniuOuSTT4YvDxLMhKzDR53BPm8Z6Hbp%2F2q5y1Ao6Wc4Ca50eKsSZ7sARKB3kXQWCnp2%2BVLTmcHIBQA7KqMhlCjdMxKqx%2BRZEXzmY91CXxg%2FbCmwPRO7X%2FpBM4wRkOhKd2gFTQkqHWDPJdCcT0WGuu%2BsFeweN8Q1THq1hfa%2BHPrjTw7JB5LxWqDzn7vqfc90dmscbc4uDDC35yAwjKaT2AY6pgFIRuYt01GZXculgQjfogWqybJ1veimFPMrJSS43%2BIauKJa7onm35Z3xof98%2FREWH88URe7YfbO46tJNDlRicwueKgO6QqV8PrHEKOjw5eci1fxW2aLslM%2F09Hez49%2B1rtT1fXCCkt2mIa2mzJA6Sr3fBJO%2FLbJs8VewZnV5Pr2UVu%2FCcl7FmvLScFJwbW1zxyWATCBk4iO2IfIj1bpoRK1J8DBsYjO&X-Amz-Signature=4d3d14cab059e3a972d4301eb09e2ca473f81a52bee940d3c123b94be38d0835&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466Z4HACVQQ%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T020356Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIFSPWPn%2FZGvg3AcNe3vyEydoQeKV3%2Bx9iroOZXkMwT9eAiADMFajHJ4%2F2Wp%2FzNvrk%2FHjNFcdKcqlzljFUmBQJqZ2EiqIBAiB%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDYzNzQyMzE4MzgwNSIMxmaFfoDt7HvcAebrKtwDUa2UnD%2BPnfmSkSSPjfpbo9CU953ME22DZx5CXdbOt0dvBrfifuLbJKR%2FkO2m9iU546C%2BdJaPHQL8K52otbOIsHgXGYcaa4WAGsYw7F7drPkHPjhFyLjWYsxNIKJur5wOXYbdlSumC9NxZRKoCsyWqlDXmC%2FsIBMXGOLuJ5fPZTSL41bjEM1cMyB5mrcQSXXgb7u35ABYk%2FaUYWflNdq1FLc%2B2pdv3JLBpi2vkZ8XTexe7uaeN57TT1queY7fxu6zlbOqsRjP6dwkgppkfUZUAN9%2BMJkIpzRHkIWCorT6J1%2FnLpfsuWpND87bATZJk9sKw4oWTU5ypB%2FVB32hLCu6ckwt6Z%2Bw6YvH1wwVJJVv7p8vKshi%2BXmKEvlYqM%2Bi4%2BS3719zYg0UMIcYvIXk7Is9HhQ5D4KyM0h1L2JMwDo9%2F5MPnniuOuSTT4YvDxLMhKzDR53BPm8Z6Hbp%2F2q5y1Ao6Wc4Ca50eKsSZ7sARKB3kXQWCnp2%2BVLTmcHIBQA7KqMhlCjdMxKqx%2BRZEXzmY91CXxg%2FbCmwPRO7X%2FpBM4wRkOhKd2gFTQkqHWDPJdCcT0WGuu%2BsFeweN8Q1THq1hfa%2BHPrjTw7JB5LxWqDzn7vqfc90dmscbc4uDDC35yAwjKaT2AY6pgFIRuYt01GZXculgQjfogWqybJ1veimFPMrJSS43%2BIauKJa7onm35Z3xof98%2FREWH88URe7YfbO46tJNDlRicwueKgO6QqV8PrHEKOjw5eci1fxW2aLslM%2F09Hez49%2B1rtT1fXCCkt2mIa2mzJA6Sr3fBJO%2FLbJs8VewZnV5Pr2UVu%2FCcl7FmvLScFJwbW1zxyWATCBk4iO2IfIj1bpoRK1J8DBsYjO&X-Amz-Signature=865d7a018de830d6f52107105afb2d809cca0e8b50655b287312c3080ab2e767&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

