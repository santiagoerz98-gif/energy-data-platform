from pipeline.transform import Transformer
from pathlib import Path
from services.catalog_generator import CatalogService

transformer = Transformer()


filepath = Path(r"data\raw\list_of_indicators_by_taxonomy_terms_generacion.json")

indicators_data = transformer.read_raw(filepath=filepath)

catalog_generator = CatalogService()

selected_ids = [546,547,548,549,550,551,552,553,554,555,1294,1295,1296,1297,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,2051,2344,10351,10352,10356]



print (catalog_generator.construir_catalogo_por_ids(indicators_data,selected_ids,"generation","Real"))





