# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4666ASXFMFM%2F20261125%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261125T190237Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQD5rGnEmoTdoAjUm8A0RJh3kyP3tkufZV0EHLc2gm%2BM3AIhAPBrV%2FBZhidbe7E%2BHBV%2FnA6ZnezQgEtuKj%2BJLXwciD1HKogECKv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMNjM3NDIzMTgzODA1IgyPWQYgc%2FX6x9pVruQq3AOywAd%2BQPB8xurnyiuPzh4Dhvoh3JsYzixvdw6uGF3TSd4JgFfpGvLt%2BvdkP6mi6aa3lky4GNSv%2Fvz%2FkLCwbyfvwYGkSvZqPMfCsCKhms9qEtFeNjraOm1pTta2CLUBahdGOv3MPgMBvfL9dDIOPGIPMyIQ%2F3G%2BEYYXVld4ac6H7glbe1I%2B2RePxBCLLy7Q0vAm8zJAbiWaAf4QF55jAEJHGTIeH%2BUCJqK8kPPw6WuljDllA9marqAn7O7Her7LOLzQ4TJfx3gLy7D8sX5CAHOLVweNJuEfrxu9DYs%2F%2BacnKMMDNETv8NH7UGM6VKfoVhn6Mz8YYFtEO71KVv6Z2LWaNNGLm4n0fDaz%2Fg1lYQL2%2BGkXKSFE94jPaUWkWc55tPpkrf72qAxXvqTftqxNCyTKLhQU8g8UElrReWBQaF9q8PYdOgitBF7eOXZJnQl0J8q%2BWEmo3ojNrS4w3d%2FUV1fCuVcscynEZOrr9VcpfYgQoi0w%2BOJWiPkSVAqG922Bz%2FIbcZKDLQiaXmCLLWDiNus5xFMbx7OoubnGZDthBgwoDQKeE%2FZoH%2BLZ5Q0%2FYgCotNGCJZdeR36YDZSd%2FI2oas7qSEvp6XcBwhKOqQSruXA2P9iW%2FPO8cc1nUlmwzzDHzZzYBjqkAaf6rxdC4FoGXGp31r%2FaToEmlWIkDKxEwhOnIvpRsgMUZMtjKFXC0%2F7ygyt7Oasal0BAW5V91Af1uM2DWVBC%2Br17gbeRguFlEku86p6PFrFAi4BvyFH6lfijpVtXB8TX7DonzI9tXS0MMgC4dqxvqhQ5bpED228yvw7Y7WX8sABgYExS7p8asvEEH1gYBtmXm2Wx6RadkWfeKlLuKv9F1g5MRLD%2B&X-Amz-Signature=1cac2d128dd97c3a0bf5cf027bce639e369d3b8e00e7be695a8623501dc9e6e2&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4666ASXFMFM%2F20261125%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261125T190237Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQD5rGnEmoTdoAjUm8A0RJh3kyP3tkufZV0EHLc2gm%2BM3AIhAPBrV%2FBZhidbe7E%2BHBV%2FnA6ZnezQgEtuKj%2BJLXwciD1HKogECKv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMNjM3NDIzMTgzODA1IgyPWQYgc%2FX6x9pVruQq3AOywAd%2BQPB8xurnyiuPzh4Dhvoh3JsYzixvdw6uGF3TSd4JgFfpGvLt%2BvdkP6mi6aa3lky4GNSv%2Fvz%2FkLCwbyfvwYGkSvZqPMfCsCKhms9qEtFeNjraOm1pTta2CLUBahdGOv3MPgMBvfL9dDIOPGIPMyIQ%2F3G%2BEYYXVld4ac6H7glbe1I%2B2RePxBCLLy7Q0vAm8zJAbiWaAf4QF55jAEJHGTIeH%2BUCJqK8kPPw6WuljDllA9marqAn7O7Her7LOLzQ4TJfx3gLy7D8sX5CAHOLVweNJuEfrxu9DYs%2F%2BacnKMMDNETv8NH7UGM6VKfoVhn6Mz8YYFtEO71KVv6Z2LWaNNGLm4n0fDaz%2Fg1lYQL2%2BGkXKSFE94jPaUWkWc55tPpkrf72qAxXvqTftqxNCyTKLhQU8g8UElrReWBQaF9q8PYdOgitBF7eOXZJnQl0J8q%2BWEmo3ojNrS4w3d%2FUV1fCuVcscynEZOrr9VcpfYgQoi0w%2BOJWiPkSVAqG922Bz%2FIbcZKDLQiaXmCLLWDiNus5xFMbx7OoubnGZDthBgwoDQKeE%2FZoH%2BLZ5Q0%2FYgCotNGCJZdeR36YDZSd%2FI2oas7qSEvp6XcBwhKOqQSruXA2P9iW%2FPO8cc1nUlmwzzDHzZzYBjqkAaf6rxdC4FoGXGp31r%2FaToEmlWIkDKxEwhOnIvpRsgMUZMtjKFXC0%2F7ygyt7Oasal0BAW5V91Af1uM2DWVBC%2Br17gbeRguFlEku86p6PFrFAi4BvyFH6lfijpVtXB8TX7DonzI9tXS0MMgC4dqxvqhQ5bpED228yvw7Y7WX8sABgYExS7p8asvEEH1gYBtmXm2Wx6RadkWfeKlLuKv9F1g5MRLD%2B&X-Amz-Signature=cace30024c1c5c45bad454c1383c6dd4fd2964d2e99e58ef742f9bd7080585f3&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

