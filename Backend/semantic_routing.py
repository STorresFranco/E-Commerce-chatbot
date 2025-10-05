from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

#%% Class definition
class ROUTER():
    def __init__(self,router):
        self.router=router


#%% Defining the router
#Embedding function for semantic routing (Lighter model)
'''
Description
    File to initiaize a semantic router for query classification
Inputs
    encoder (Huggingface encoder)
Returns
    router (semantic router): Object to route queries as product or faq
'''
semantic_encoder=HuggingFaceEncoder(
name="sentence-transformers/all-mpnet-base-v2",
device="cpu"
)

#FAQ rout definition
faq = Route(
    name="FAQ",
    utterances=[
"What is the return policy of the products?",
"What is the refund policy for products?",
"How can I track my order?",
"How long does it take to process a refund?",
"Can I cancel or modify my order after placing it?",
"What should I do if I receive a damaged product?",
"How do I use a promo code during checkout?",
"Can I pay with cash?",
"Can I pay with credit card?"
    ],
)

#Route for product consultation
sql = Route( #We call it sql because we will transform it into a query
    name="Products",
    utterances=[
"I want to buy the most expensive nikes",
"Are your shoes under 3000 RS?",
"Are there any PUMA shoes for sell?",
"What's the price of a running shoe?",
"Give me shoes below 1000 range?",
"Help me find nike shoes in this price range",
"Show me the top five most expensive shoes listed by price",
"Give me the top 5 products listed by rating",
"Show me nike or puma products with ratings higher than 3 and lower than 5",
"Give me Puma Shoes with these attributes"
"What are the male top rated shoes or products?",
"What are the female top reated shoes or products"],
)


#Conversational Route
conversation=Route(
    name="Conversation",
    utterances=[
        "How are you?",
        "How is your day?",
        "Hello, good morning",
        "Hi friend",
        "How do I use you?",
        "How do I use this app?"
    ]
)

#Define routes

routes=[faq,sql,conversation]
router=SemanticRouter(encoder=semantic_encoder,routes=routes,auto_sync="local")
rl=ROUTER(router)
