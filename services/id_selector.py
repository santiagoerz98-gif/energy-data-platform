class IdSelector:
    """Contiene la lógica para clasificar o identificar IDs según el nombre del indicador."""

    def __init__(self,category_map:dict):
        self.category_map = category_map

    def obtener_ids(self,indicators_data:dict,category:str)->set:

        category_key = category.lower()

        if category_key not in self.category_map:
            valid_categories = list(self.category_map.keys())
            raise ValueError(
                f"Categoría '{category}' no soportada. "
                f"Opciones disponibles: {valid_categories}"
            )

        keywords = {kw.lower() for kw in self.category_map[category_key] }

        found_ids = set()

        for indicator in indicators_data:
            name = indicator.get("name","").lower()

            if all(kw in name for kw in keywords):
                if "id" in indicator:
                    found_ids.add(indicator["id"])

        return found_ids


