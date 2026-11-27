# Complete flow of MSK-Kafka-CP schema


## How we were before the Apache Kafka:
This image or design explains in detail what we were and how it was hard to make the same flow as we are doing today with the Apache Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/4400a874-b948-4e43-95e6-135e4a0836f4/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466YCYFZMPC%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T205539Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBQaCXVzLXdlc3QtMiJHMEUCIQDsrB35KJvqeB6DU874RgcUH7RgtAWQdQjwJ2SBf6FxsQIgDTA1Ba74Lxj67Of6sAib1wRIwzSdrRePEmlqO30vH3QqiAQI3P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDEuv8JtMRS92aAuLbCrcA4zTS2VxE1v9yg8KUGxiWp4sIpPfj23edzX08PXqzZOdo6QrdqZ9Zo2gRnydkZS%2Fa8BPQ2dftAB5wh1%2BrONT3ta5Dk2QLaYKpV4Dlcz5561f8gOlI8%2BkhanhH%2B1jO0jIcVxg30h6DpkvJYE3MKhaZDnwybipHMCf04iKB%2FFjdBTIciyIbOsHup2KO%2FErNPIP0U9eKvwicqbaTXhcSwfyrNuI9gyQxq2P4uon9w9GZmgAIdkbpEknYahY3rHBAcwNukQTWKuPmBkfGznMX%2BrSa5lYVz%2FxIU2XbHseTKT1JCVT2tZ%2B1K%2BPmmqwa5qmq11fo1UCM2zCFklaKtEoMk9EEVr%2BVz%2B3ElERMMLi%2FROxBvsKw8nCQEZWdFQ1pYrSK6H8uY%2FglZV7hNeYAAnCrW7OZ9xu%2FppdG1fyXXHEd94NBDId8jJjBURqVF7%2B8GQK5nmiy22uEtWogO%2B0HmxcpU1ooxJYQquhtb9TnH8ApqazZ4Gh8GglbjCvuySB3OU1ViA7gkdtB64DUuvzPkGPG1YlfPqbYUNGIAkvLg%2B6N3Q7NJQn9pMpzjgJHEg9Rln2zrJD3zZbHmlRRoaxO5Bf9reTd23wvwYnXBv3%2FZ94BDez5nFQ72RwNiEkNxNWSfezMNbBp9gGOqUBh0UrSs5co%2FenEbY%2Fnp6EqzXKUPaMxrxN5vYuvPq03J%2Bp3m8HMK%2F0yNDeqD%2FGSaSgXfrs7kqeogBtSytVgl2N%2FT18cofjrBxMpXad2o8%2BE8HcjBgSxcWuzaljo9D8G3g30x0z4ge5nBXUyRacHZa8M2S8bT0IdkynvTLJGECqqPe8NBPesEKf4CN35PmaQymkwhlTPJuFtsYmGxceg%2BSVr8QNMoV4&X-Amz-Signature=a241a0e2b2920730986cffae48370e1ae93665b070109c44a9c7ccb088432f2d&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

Possible problems:
1. **Tight coupling:** Order Service needs to know which services it must call.
1. **Dependency:** If Payment Service is down, the direct call can fail.
1. **Performance:** Order Service may need to wait for multiple services to respond.
1. **Scalability:** Adding a new service means changing the order service to call it.
1. **Failure handling:** You need to handle retries, timeouts, and failed requests.

## **How does Kafka solve this problem?**
Instead of directly calling every service, Order Service publishes an event to Kafka.
![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/2829f2a9-3248-817e-832a-00036f0016c8/9dda05c5-556e-44d6-845c-852f6235087a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466YCYFZMPC%2F20261127%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261127T205539Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBQaCXVzLXdlc3QtMiJHMEUCIQDsrB35KJvqeB6DU874RgcUH7RgtAWQdQjwJ2SBf6FxsQIgDTA1Ba74Lxj67Of6sAib1wRIwzSdrRePEmlqO30vH3QqiAQI3P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDEuv8JtMRS92aAuLbCrcA4zTS2VxE1v9yg8KUGxiWp4sIpPfj23edzX08PXqzZOdo6QrdqZ9Zo2gRnydkZS%2Fa8BPQ2dftAB5wh1%2BrONT3ta5Dk2QLaYKpV4Dlcz5561f8gOlI8%2BkhanhH%2B1jO0jIcVxg30h6DpkvJYE3MKhaZDnwybipHMCf04iKB%2FFjdBTIciyIbOsHup2KO%2FErNPIP0U9eKvwicqbaTXhcSwfyrNuI9gyQxq2P4uon9w9GZmgAIdkbpEknYahY3rHBAcwNukQTWKuPmBkfGznMX%2BrSa5lYVz%2FxIU2XbHseTKT1JCVT2tZ%2B1K%2BPmmqwa5qmq11fo1UCM2zCFklaKtEoMk9EEVr%2BVz%2B3ElERMMLi%2FROxBvsKw8nCQEZWdFQ1pYrSK6H8uY%2FglZV7hNeYAAnCrW7OZ9xu%2FppdG1fyXXHEd94NBDId8jJjBURqVF7%2B8GQK5nmiy22uEtWogO%2B0HmxcpU1ooxJYQquhtb9TnH8ApqazZ4Gh8GglbjCvuySB3OU1ViA7gkdtB64DUuvzPkGPG1YlfPqbYUNGIAkvLg%2B6N3Q7NJQn9pMpzjgJHEg9Rln2zrJD3zZbHmlRRoaxO5Bf9reTd23wvwYnXBv3%2FZ94BDez5nFQ72RwNiEkNxNWSfezMNbBp9gGOqUBh0UrSs5co%2FenEbY%2Fnp6EqzXKUPaMxrxN5vYuvPq03J%2Bp3m8HMK%2F0yNDeqD%2FGSaSgXfrs7kqeogBtSytVgl2N%2FT18cofjrBxMpXad2o8%2BE8HcjBgSxcWuzaljo9D8G3g30x0z4ge5nBXUyRacHZa8M2S8bT0IdkynvTLJGECqqPe8NBPesEKf4CN35PmaQymkwhlTPJuFtsYmGxceg%2BSVr8QNMoV4&X-Amz-Signature=a49a05989c6ca2cc1a629c190e1a316837f2e964da5b66c6e2caeeec628cdbb1&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
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

