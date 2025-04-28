from utils.scraper_utils import crawl_ecommerce_site
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import argparse
from config import ECOMMERCE_SITES, CATEGORIES
from utils.data_utils import save_products_to_csv, format_product_summary


async def main():
    parser = argparse.ArgumentParser(description="E-commerce Deal Finder")
    parser.add_argument("--site", choices=list(ECOMMERCE_SITES.keys()) + ["all"], default="all",
                        help="E-commerce site to search")
    parser.add_argument("--category", choices=CATEGORIES + ["all"], default="all",
                        help="Product category to search for")
    parser.add_argument("--search", type=str, default=None,
                        help="Custom search term (otherwise category will be used)")
    
    args = parser.parse_args()
    
    sites_to_search = list(ECOMMERCE_SITES.keys()) if args.site == "all" else [args.site]
    categories_to_search = CATEGORIES if args.category == "all" else [args.category]
    
    all_results = []
    
    for site_name in sites_to_search:
        site_config = ECOMMERCE_SITES[site_name]
        for category in categories_to_search:
            search_term = args.search if args.search else category
            print(f"\nSearching for '{search_term}' in {category} category on {site_name}...")
            
            products = await crawl_ecommerce_site(site_name, category, search_term)
            
            if products:
                # Save products to CSV
                filename = save_products_to_csv(products, category, site_name)
                
                # Print summary of best deals
                summary = format_product_summary(products, category, site_name)
                print("\n" + summary + "\n")
                
                # Add to overall results
                all_results.extend(products)
            else:
                print(f"No products found for '{search_term}' in {category} category on {site_name}")
    
    # Save combined results if searching multiple sites/categories
    if len(sites_to_search) > 1 or len(categories_to_search) > 1:
        combined_filename = save_products_to_csv(all_results, "combined")
        print(f"\nAll results saved to {combined_filename}")
        
        # Print overall best deals
        overall_summary = format_product_summary(all_results)
        print("\nOVERALL BEST DEALS ACROSS ALL SEARCHES:")
        print(overall_summary)

if __name__ == "__main__":
    asyncio.run(main())