import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from models.product import Product
from config import REQUEST_DELAY, MAX_PAGES_PER_SEARCH
import os
from dotenv import load_dotenv
import google.generativeai as genai
from bs4 import BeautifulSoup  # <-- Add this import
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_products_with_llm(html_content: str, url: str, category: str) -> List[Product]:
    MAX_HTML_CHARS = 20000

    # --- BeautifulSoup pre-parsing ---
    soup = BeautifulSoup(html_content, "html.parser")
    # Use the product selector from config (for Jumia: "article.prd")
    product_blocks = soup.select("article.prd")
    # Join only the HTML of the first 5 product blocks (or fewer if less found)
    product_html = "\n".join(str(block) for block in product_blocks[:5])
    print("Product HTML snippet:", product_html[:1000])  # Debug print

    truncated_html = product_html[:MAX_HTML_CHARS]

    prompt = f"""
    Extract product information from the following HTML snippets of e-commerce products.
    The search was for products in the category: {category}
    Page URL: {url}

    For each product, extract the following information in JSON format:
    - name: Product name/title (required)
    - price: Current price (required, just the number, no currency symbol)
    - original_price: Original/list price if available (just the number, no currency symbol)
    - description: Brief product description if available
    - rating: Star rating if available (e.g., 4.5)
    - reviews_count: Number of reviews if available
    - seller: Store or seller name
    - url: Full URL to the product detail page
    - image_url: URL of product image
    - availability: Stock status info if available
    - features: List of key features or specifications

    Only include products that have BOTH a name and a price.
    Return the result as a JSON object with a single key "products", whose value is a list of product objects.
    Do NOT wrap the JSON in markdown or code blocks. Ensure the JSON is valid and properly closed.
    If there are many products, only include up to 5.

    Example format:
    {{
      "products": [
        {{
          "name": "Product Name",
          "price": 29.99,
          "original_price": 39.99,
          "description": "Brief description",
          "rating": 4.5,
          "reviews_count": 203,
          "seller": "Store Name",
          "url": "https://example.com/product",
          "image_url": "https://example.com/image.jpg",
          "availability": "In Stock",
          "features": ["Feature 1", "Feature 2"]
        }},
        ...
      ]
    }}

    HTML content:
    {truncated_html}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        result = response.text
        print("Gemini response:", result)
        # Remove markdown code block if present
        if result.strip().startswith("```"):
            result = result.strip().lstrip("`").split("\n", 1)[-1]
            if result.endswith("```"):
                result = result.rsplit("```", 1)[0].strip()
        extracted_data = json.loads(result)["products"]

        products = []
        for item in extracted_data:
            try:
                if item.get('url') and not item['url'].startswith('http'):
                    base = '/'.join(url.split('/')[:3])
                    item['url'] = f"{base}{item['url']}" if item['url'].startswith('/') else f"{base}/{item['url']}"
                product = Product(**item)
                products.append(product)
            except Exception as e:
                print(f"Error creating product object: {e}")
                continue
        return products
    except Exception as e:
        print(f"Error extracting products with LLM: {e}")
        return []

async def fetch_html_with_playwright(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=90000)
        await page.wait_for_load_state("domcontentloaded", timeout=90000)
        await asyncio.sleep(5)  # Give JS time to render
        html = await page.content()
        await browser.close()
        return html

async def crawl_ecommerce_site(site: str, category: str, search_term: str = None):
    from config import ECOMMERCE_SITES

    site_config = ECOMMERCE_SITES[site]
    base_url = site_config["BASE_URL"]
    search = search_term or category
    url = f"{base_url}{search.replace(' ', '+')}"

    print(f"Crawling {url}")

    html = await fetch_html_with_playwright(url)
    products = extract_products_with_llm(html, url, category)
    return products