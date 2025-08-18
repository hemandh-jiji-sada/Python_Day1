from fastapi import FastAPI


api=FastAPI()
products=[
    {"name":"apple","price":100},
    {"name":"banana","price":50},
    {"name":"orange","price":200}
]

@api.get("/products")
def read_products():
    return products

@api.post("/products")
def post_product(name:str,price:int):
    products.append({"name":name,"price":price})
    return {"message":"product added"}
