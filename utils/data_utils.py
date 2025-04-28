import pandas as pd
import os
from datetime import datetime
from models.product import Product
from typing import List, Dict, Any

def save_products_to_csv(products: List[Product], category: str = None, site: str = None):
    """Save extracted products to a CSV file."""
    if not products:
        print("No products to save.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/products"
    if category:
        filename += f"_{category}"
    if site:
        filename += f"_{site}"
    filename += f"_{timestamp}.csv"
    
    # Convert products to dict and save as CSV
    products_dict = [product.model_dump() for product in products]
    df = pd.DataFrame(products_dict)
    
    # Calculate additional metrics if possible
    if 'original_price' in df.columns and 'price' in df.columns:
        mask = (~df['original_price'].isna()) & (df['original_price'] > df['price'])
        df.loc[mask, 'discount_amount'] = df.loc[mask, 'original_price'] - df.loc[mask, 'price']
        df.loc[mask, 'discount_percentage'] = ((df.loc[mask, 'original_price'] - df.loc[mask, 'price']) / 
                                             df.loc[mask, 'original_price'] * 100).round(2)
    
    # Sort by discount percentage if available, otherwise by price
    if 'discount_percentage' in df.columns:
        df = df.sort_values('discount_percentage', ascending=False)
    else:
        df = df.sort_values('price')
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved {len(products)} products to {filename}")
    
    return filename

def format_product_summary(products: List[Product], category: str = None, site: str = None):
    """Format a summary of the best deals found."""
    if not products:
        return "No products found."
        
    summary = []
    
    if category and site:
        summary.append(f"Top Deals for {category} on {site.title()}:")
    elif category:
        summary.append(f"Top Deals for {category}:")
    elif site:
        summary.append(f"Top Deals on {site.title()}:")
    else:
        summary.append("Top Deals Found:")
    
    # Sort products by discount percentage if available
    sorted_products = sorted(
        products, 
        key=lambda p: p.discount_percentage if p.discount_percentage is not None else 0, 
        reverse=True
    )
    
    # Take top 10 deals
    top_deals = sorted_products[:10]
    
    for i, product in enumerate(top_deals, 1):
        deal = f"{i}. {product.name} - ${product.price}"
        if product.original_price:
            discount = product.original_price - product.price
            discount_pct = (discount / product.original_price) * 100
            deal += f" (Was ${product.original_price}, Save ${discount:.2f}, {discount_pct:.1f}% off)"
        if product.rating:
            deal += f" - {product.rating}★"
        summary.append(deal)
    
    return "\n".join(summary)
