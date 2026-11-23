# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4665ZRMWGVE%2F20261123%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261123T120143Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQC6Flm1O8C6F%2BOes11XZ5vDyWJ9XYeGag6a%2B50qCz7oMwIgNaiV9s6%2B%2BQvaJJ%2FVjlGOXss4mPW7FwAW6uo4QnAQ54Mq%2FwMIdBAAGgw2Mzc0MjMxODM4MDUiDHx7TIintm4Bqwta0SrcA32X6z3hee5Tjm1UAc8LgKRYUzNDXgEN06KbJSLBakkl3vQGgoi%2Brh4vYxriyfYJyq1Yb%2Bv0dCdn8hx8IHlD1SaF0mqFEq5z6KSq%2B1lpDGwbTsUJXXTmf3TMTwJKAewsDYH0LzjxqBFaLxhKgJfifGmUXFEbG2nuBF8dLED4mBFZsgZM1a5DNmLKyCJjNmOVD7rSDGqOBXULb3IazPn1pShJFpFuGuNw8OIxEPaXjFHGQWdkQEhIVx2Y56Frno2dv%2BdPG0p9nYQwbIn2S8%2BbGSQhK2OhZ7HLxQdSw7AVyeTWNlDOMSto96mDdKnCkSWE0gqKQADoU%2Fa6Mx4skgLvG2MaqiRNKfawamS8duireBrbdqMFVtUL5vLcnBCOkkAdzLxp7C3nMF0hmQdjFfDYQwJWc3qVsXRVGuWtnDOK4DZLJI9bhxB0%2BEkiX3ob1Oma3ldHkhdxPFDYaIlplJnTwowLj3VH1SfUsRGEQPfD0R6ugwqUfqTZT3N0omPcglYsO0EJZBQ8sW0pVwbmSZbeZUns7AJNLonTpCaqKsiHLrrcovbzK%2FahHW7MHhXrgkCPO7v%2BTXs5kV2GwRlbfnfgC%2BLwphDoZtzxGDzT6qAQaTM%2Fep71bV6I3MSjd69IMIXBkNgGOqUBqifWQpj%2FN0Cz2yikPZwHOE%2FziUr0CFx64q28CRe43wpzHypOEbg6rL4%2BMujQL87jdVtqFBZrvcV2ZKlxyk7SHb13f50Ayvi4nz1dCcWUyrDijOFsT2xB7ZHvP7dKLwJ1fKP2cfJM%2F889UfSPVWjQTBc6OdXZ6QzhHTV2wBsEwtBTpeajSUtasmmVJXdWK4GEDR8TaDRwLbPa%2BWs%2FAy02kF%2FF1Smb&X-Amz-Signature=7eb95a36ce5d715c362de8e169d9d32faed917731bc9cd86669fdbb86ebabe02&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4665ZRMWGVE%2F20261123%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261123T120143Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQC6Flm1O8C6F%2BOes11XZ5vDyWJ9XYeGag6a%2B50qCz7oMwIgNaiV9s6%2B%2BQvaJJ%2FVjlGOXss4mPW7FwAW6uo4QnAQ54Mq%2FwMIdBAAGgw2Mzc0MjMxODM4MDUiDHx7TIintm4Bqwta0SrcA32X6z3hee5Tjm1UAc8LgKRYUzNDXgEN06KbJSLBakkl3vQGgoi%2Brh4vYxriyfYJyq1Yb%2Bv0dCdn8hx8IHlD1SaF0mqFEq5z6KSq%2B1lpDGwbTsUJXXTmf3TMTwJKAewsDYH0LzjxqBFaLxhKgJfifGmUXFEbG2nuBF8dLED4mBFZsgZM1a5DNmLKyCJjNmOVD7rSDGqOBXULb3IazPn1pShJFpFuGuNw8OIxEPaXjFHGQWdkQEhIVx2Y56Frno2dv%2BdPG0p9nYQwbIn2S8%2BbGSQhK2OhZ7HLxQdSw7AVyeTWNlDOMSto96mDdKnCkSWE0gqKQADoU%2Fa6Mx4skgLvG2MaqiRNKfawamS8duireBrbdqMFVtUL5vLcnBCOkkAdzLxp7C3nMF0hmQdjFfDYQwJWc3qVsXRVGuWtnDOK4DZLJI9bhxB0%2BEkiX3ob1Oma3ldHkhdxPFDYaIlplJnTwowLj3VH1SfUsRGEQPfD0R6ugwqUfqTZT3N0omPcglYsO0EJZBQ8sW0pVwbmSZbeZUns7AJNLonTpCaqKsiHLrrcovbzK%2FahHW7MHhXrgkCPO7v%2BTXs5kV2GwRlbfnfgC%2BLwphDoZtzxGDzT6qAQaTM%2Fep71bV6I3MSjd69IMIXBkNgGOqUBqifWQpj%2FN0Cz2yikPZwHOE%2FziUr0CFx64q28CRe43wpzHypOEbg6rL4%2BMujQL87jdVtqFBZrvcV2ZKlxyk7SHb13f50Ayvi4nz1dCcWUyrDijOFsT2xB7ZHvP7dKLwJ1fKP2cfJM%2F889UfSPVWjQTBc6OdXZ6QzhHTV2wBsEwtBTpeajSUtasmmVJXdWK4GEDR8TaDRwLbPa%2BWs%2FAy02kF%2FF1Smb&X-Amz-Signature=5e40f39430d85940b9a6a7bb6ad2f906487469069167c6c418cb0748053435ad&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

