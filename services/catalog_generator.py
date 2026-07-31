class CatalogService:
    def __init__(self):
        pass
    """Servicio encargado de armar y estructurar el catálogo de indicadores final."""
    def construir_catalogo_por_ids(self,indicators:dict,selected_ids:list,dataset:str,category_value:str)->dict:

        conjunto_ids = set(selected_ids)

        catalog = {
            indicator["id"]:{
                "name":indicator["name"],
                "dataset": dataset,
                "type":category_value,
                "fact_table": f"fact_{dataset}",
                "short_name": indicator["short_name"]
            }
            for indicator in indicators["indicators"] 
            if isinstance(indicator,dict) and indicator.get("id") in conjunto_ids
        }
        return catalog
