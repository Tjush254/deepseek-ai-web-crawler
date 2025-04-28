# E-commerce site configuration

ECOMMERCE_SITES = {
    "jumia": {
        "BASE_URL": "https://www.jumia.co.ke/catalog/?q=",
        "PRODUCT_SELECTOR": "article.prd",  # Update as needed
        "PAGINATION_SELECTOR": "a.pg-next", # Update as needed
    },
    # Add more sites if needed
}

CATEGORIES = [
    "electronics",
    "phones",
    "laptops",
    "home appliances",
    "fashion",
    # Add more categories as needed
]

REQUEST_DELAY = 2  # seconds between requests (adjust as needed)
MAX_PAGES_PER_SEARCH = 3  # max number of pages to crawl per search (adjust as needed)