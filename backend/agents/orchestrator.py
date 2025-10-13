from .memory import ConversationMemory
from .api_tools import retrieve_product, retrieve_review_by_id,retrieve_review_by_name, order_product, add_review_tool
from textblob import TextBlob
import json

memory = ConversationMemory()



def get_review_rating(msg):
    print('reg_review_rating')
    print(msg)
    polarity = TextBlob(msg).sentiment.polarity
    if polarity > 0.5:
        return 5
    elif polarity > 0.1:
        return 4
    elif polarity > -0.1:
        return 3
    elif polarity > -0.5:
        return 2
    else:
        return 1


def handle_user_message(user_message, agent):
    lower = user_message.lower()
    product_id = memory.get("product_id")
    product_name = memory.get("product_name")
    print(f"orchestor: {product_id} {product_name}")
    # Recommend or search
    if "recommend" in lower or "suggest" in lower or "find" in lower or "search" in lower:
        print('inside recommend')
        result = retrieve_product(user_message)
        # result is a dict response shown above
        if "results" in result and len(result["results"]) > 0:
            # Pick the top product (you can add user selection later!)
            top_product = result["results"][0]
            pid = top_product.get("product_id")
            pname = top_product.get("product_name")
            memory.set("product_id", pid)
            memory.set("product_name", pname)
            return f"Recommended: {pname}\n Sentiment: {top_product['sentiment_summary']}"
        else:
            return "No products found for your query."

    # For reviews -- use product_id from memory
    if "review" in lower:
        print('inside review')
        if product_id:
            review_response = retrieve_review_by_id(product_id)
            return summarize_reviews(review_response)
        elif product_name:
            review_response = retrieve_review_by_name(product_name)
            return summarize_reviews(review_response)
        else:
            return "No product context found."

    # For orders
    if "order" in lower:
        print('inside order')
        if product_id:
            order = order_product(product_id)
            return f"Product {product_name} ordered successfully!" if order.get("success") else "Order failed."
        else:
            return "Cannot order: No product ID found."
    
    # Add feedback as a review (any feedback about product)
    if product_id:
        print('inside review rating')
        rating = get_review_rating(user_message)
        print(rating)
        if rating != 3 or ("good" in lower or "bad" in lower or "like" in lower or "love" in lower or "hate" in lower):
            payload = {
            "product_id": product_id,
            "review_text": user_message,
            "rating": rating
            }
            str_payload = json.dumps(payload)
            print(str_payload)
            backend_resp = add_review_tool({"review_json": json.dumps(payload)})
        
            print(backend_resp)
            context_message = (
                f'The user just left a review for "{product_id}" (rating {rating}): "{user_message}". '
                "Review was saved to the database. Please respond empathetically. "
                "If the rating is low, offer an alternative."
            )
            print(context_message)
            return agent.run(context_message)

    # Generic fallback
    return agent.run(user_message)


def summarize_reviews(review_response):
    """
    Creates a chat-friendly summary of reviews from the API response.
    """
    results = review_response.get("results", [])
    if not results:
        return "No customer reviews found for this product."

    # Extract product name from the first review's metadata (if available)
    product_name = None
    for r in results:
        product_name = r.get("metadata", {}).get("product_name")
        if product_name:
            break  # Stop after finding the first available product name
    if not product_name:
        product_name = "the selected product"

    review_texts = [r.get("text") for r in results if r.get("text")]
    if not review_texts:
        return f"No customer review text found for {product_name}."

    # Add sentiment summary if available
    sentiment_summary = None
    for r in results:
        sentiment_summary = r.get("metadata", {}).get("review_sentiment_label")
        if sentiment_summary:
            break

    # Format the reply
    summary_lines = [
        f"Customer reviews for **{product_name}**:",
    ]
    if sentiment_summary:
        summary_lines.append(f"Sentiment: {sentiment_summary.capitalize()}")

    # Show up to 3 reviews in a bulleted list
    for review in review_texts[:3]:
        summary_lines.append(f"- {review}")

    return "\n".join(summary_lines)


