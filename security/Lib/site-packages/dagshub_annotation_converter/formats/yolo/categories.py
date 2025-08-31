from typing import Union, Optional, Dict, List

from dagshub_annotation_converter.util.pydantic_util import ParentModel


class Category(ParentModel):
    name: str
    id: int

    def __hash__(self):
        return hash(self.name)


class Categories(ParentModel):
    categories: List[Category] = []
    _id_lookup: Dict[int, Category] = {}
    _name_lookup: Dict[str, Category] = {}

    def __getitem__(self, item: Union[int, str]) -> Category:
        if isinstance(item, int):
            return self._id_lookup[item]
        else:
            return self._name_lookup[item]

    def __iter__(self):
        return self.categories.__iter__()

    def __len__(self):
        return len(self.categories)

    def get(self, item: Union[int, str], default=None) -> Category:
        try:
            return self[item]
        except KeyError:
            return default

    def get_or_create(self, name: str) -> Category:
        if name not in self:
            return self.add(name)
        return self[name]

    def __contains__(self, item: str):
        return item in self._name_lookup

    def add(self, name: str, id: Optional[int] = None) -> Category:
        if id is None:
            if len(self._id_lookup):
                id = max(self._id_lookup.keys()) + 1
            else:
                id = 0
        new_category = Category(name=name, id=id)
        self.categories.append(new_category)
        self.regenerate_dicts()
        return new_category

    def regenerate_dicts(self):
        self._id_lookup = {k.id: k for k in self.categories}
        self._name_lookup = {k.name: k for k in self.categories}


def determine_category(category: Union[int, str], categories: Categories) -> Category:
    res = categories.get(category)
    if res is None:
        raise ValueError(f"Unknown category {category}. Imported categories from the .yaml: {categories}")
    return res
