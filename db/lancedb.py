import os
import lancedb
from dotenv import load_dotenv

load_dotenv()

LANCEDB_API_KEY = os.getenv("LANCEDB_API_KEY")
LANCEDB_REGION = os.getenv("LANCEDB_REGION")
LANCEDB_URI = os.getenv("LANCEDB_URI")

db = lancedb.connect(uri=LANCEDB_URI, api_key=LANCEDB_API_KEY, region=LANCEDB_REGION)

table_names = [ # maps to dataset names
    "annual_reports",
    "inventory_receiving",
    "product_catalogs",
    "promotional_flyers",
    "purchase_orders",
    "quarterly_reports",
    "sales_receipts",
    "shipping_manifests",
    "store_reports",
    "warehouse_picking_slips",
]
