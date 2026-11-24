# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466XHHRPUJT%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T132640Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQChW%2BbB6aBu%2FWr8LLxJqlB%2ByjCKXVa2BqY1TFZ4fA%2BT2AIgXUaOh6yHG0VWl8PL6Henpxs1AHNy4zpZtsEGI1wvbr0qiAQIjv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDKcD6bvIwtZ2SCAM3ircA%2B22YxjFJPmpO3GtQMuzfyty6qa7OGv1N9usMEBUnvBGfba6VQop3OB9msUev%2BXjJpVY0rpJq3h71gh9mF1aUw0DiIk7UcojSyiEClWPIbI7EObj4tdgoSSIZIKKcb4D5t2HLLxSAjgdCV1ZCHw9YJmn%2FIbdndysi2JQPPkqrgrVYeq2so6sq7TSbc3W2TR%2Be18EFGto1posHSMoq%2FXDwNfgrxO1k0m4rutjeMzXbaj3OLNQ3%2F6Hv%2BJ5ZKo%2F5%2F9ohOyXIAHxwpujqK%2FqBfyT38Mv7KozZDXoTyeC6wHTiuzVUEQPFyqYNBX7jl5AUN9ECzWItnQOpo1GnJ43bguX3vl3QNKafYeKsBKsYJNndJUqn9rLso2G55oMsUIRNSRVQlGxmrydSoAMB7J7EkTq1iAEfSkCPMNDsU3FqSpp%2BbzyrJ6NZWX774tVxWFIEZz6Z2V3d2oN63rPfCehYWh9HYGmxgVEpU6j2O2C27zwY2V7cUD%2BrnKp%2Fk%2BfvosuiE1VQFvbJfKp4x79EnmqglPavDb9lCnTt7sEp1Cf0CUY%2BpISIQW8VzVqWBF0633MrFB4a5WDUO3JLTz88EmdySZm0OyD9sCs%2FeCIry%2FnLu4O%2BxeZtSt8Dk9wtzW3%2FXfdMNSTltgGOqUB1PvI7BCbOeVnjzJw9866gQIwC5NGts1%2FeIciQCtgIKkrIo46ZQqi4MlLjVbA40aHOL1hUugE9fgMIbARrN543yUk2wt8Gk32ZfIrfwgZEXGZGY8EmCRgbncTy4CYWKFR7DATUhbVNI9XhUPsjqRskfmoG%2FXUME14NPmfY71pOch6eNnViBdbhtrFo8v%2FfFCsbu7AvpicHcOAIw686gP7e598NfZ%2F&X-Amz-Signature=fb2b140fba950f737e187761ba5f7455fc6d645708b5307335b69adbe0259e3c&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466XHHRPUJT%2F20261124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261124T132640Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQChW%2BbB6aBu%2FWr8LLxJqlB%2ByjCKXVa2BqY1TFZ4fA%2BT2AIgXUaOh6yHG0VWl8PL6Henpxs1AHNy4zpZtsEGI1wvbr0qiAQIjv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDKcD6bvIwtZ2SCAM3ircA%2B22YxjFJPmpO3GtQMuzfyty6qa7OGv1N9usMEBUnvBGfba6VQop3OB9msUev%2BXjJpVY0rpJq3h71gh9mF1aUw0DiIk7UcojSyiEClWPIbI7EObj4tdgoSSIZIKKcb4D5t2HLLxSAjgdCV1ZCHw9YJmn%2FIbdndysi2JQPPkqrgrVYeq2so6sq7TSbc3W2TR%2Be18EFGto1posHSMoq%2FXDwNfgrxO1k0m4rutjeMzXbaj3OLNQ3%2F6Hv%2BJ5ZKo%2F5%2F9ohOyXIAHxwpujqK%2FqBfyT38Mv7KozZDXoTyeC6wHTiuzVUEQPFyqYNBX7jl5AUN9ECzWItnQOpo1GnJ43bguX3vl3QNKafYeKsBKsYJNndJUqn9rLso2G55oMsUIRNSRVQlGxmrydSoAMB7J7EkTq1iAEfSkCPMNDsU3FqSpp%2BbzyrJ6NZWX774tVxWFIEZz6Z2V3d2oN63rPfCehYWh9HYGmxgVEpU6j2O2C27zwY2V7cUD%2BrnKp%2Fk%2BfvosuiE1VQFvbJfKp4x79EnmqglPavDb9lCnTt7sEp1Cf0CUY%2BpISIQW8VzVqWBF0633MrFB4a5WDUO3JLTz88EmdySZm0OyD9sCs%2FeCIry%2FnLu4O%2BxeZtSt8Dk9wtzW3%2FXfdMNSTltgGOqUB1PvI7BCbOeVnjzJw9866gQIwC5NGts1%2FeIciQCtgIKkrIo46ZQqi4MlLjVbA40aHOL1hUugE9fgMIbARrN543yUk2wt8Gk32ZfIrfwgZEXGZGY8EmCRgbncTy4CYWKFR7DATUhbVNI9XhUPsjqRskfmoG%2FXUME14NPmfY71pOch6eNnViBdbhtrFo8v%2FfFCsbu7AvpicHcOAIw686gP7e598NfZ%2F&X-Amz-Signature=5954d14c710a6522cadc017c2e7932c83c6a8fd24453f9a6caa8d3b0be7559cb&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

