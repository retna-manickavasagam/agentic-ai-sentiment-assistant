from langchain.tools import tool
import requests, json 
from pydantic import BaseModel

API_URL = "http://localhost:8000/"
PRODUCT_URL = "api/products/retrieve"
REVIEW_URL = "api/reviews/retrieve"
ORDER_URL="api/order/insert"
REVIEW_ADD_URL = "api/reviews/add"
EMAIL_URL = "api/email/send"

class AddReviewInput(BaseModel):
        review_json: str

@tool("GetProduct")
def retrieve_product(user_query: str):
    """
    Retrieve product information using a natural language user query.
    Takes a user query string and returns product_id, product_name, and relevant data from the API.
    """
    print('inside product tool')
    payload = {"query": user_query, "k": 3}
    url = API_URL + PRODUCT_URL
    try:
        print(url)
        print(payload)
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@tool("GetReviewById")
def retrieve_review_by_id(product_id: str):
    """
    Retrieve the review for a product using its product_id.
    """
    print('inside GetReviewById tool')
    url = API_URL + REVIEW_URL
    print(url)
    payload = {"product_id": product_id}
    print(payload)
    try:
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@tool("GetReviewByName")
def retrieve_review_by_name(product_name: str):
    """
    Retrieve the review for a product using its product_name.
    """
    print('inside GetReviewByName tool')
    url = API_URL + REVIEW_URL
    print(url)
    payload = {"product_name": product_name}
    print(payload)
    res = requests.post(API_URL + REVIEW_URL, json=payload)
    return res.json()


@tool("OrderProduct")
def order_product(order: str):
    """
    Place an order for a product using its product_id.
    """
    orderObj = json.loads(order)
    print(orderObj)
    payload = {"product_id": orderObj["product_id"], "name": orderObj["name"]}
    res = requests.post(API_URL + ORDER_URL, json=payload)
    return res.json()


@tool("AddReview", args_schema=AddReviewInput)
def add_review_tool(review_json: str):
    """
    Add a review for a product. Expects a JSON string as input with keys: product_id, review_text, rating.
    Example:
        '{"product_id":"AVq...", "review_text":"Great product!", "rating":5}'
    """
    print('inside add review api_tool')
    payload = json.loads(review_json)
    print(payload)
    url = API_URL + REVIEW_ADD_URL
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        return f"Your review for product {payload['product_id']} was {'added successfully' if data.get('success') else 'not added'}."
    except Exception as e:
        return f"Failed to add review: {e}"
    
    
@tool("SendEmail")
def send_email(params: dict):
    """
    Wrapper for group email sending using a single dictionary parameter.
    Expects params: {"to_email": ..., "subject": ..., "body": ...}
    """
    to_email = params.get("to_email")
    subject = params.get("subject")
    body = params.get("body")
    payload = {"to_email": to_email, "subject": subject, "body": body}
    url = API_URL + EMAIL_URL
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        return f"Email is sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"