import json

def get_data(path_: str):
    with open(path_) as source:
        data = json.load(source)
        return data

def get_supplier_names(path_: str):
    data = get_data(path_)

    suppliers = {}  # --> {"value": id}
    for record in data:
        suppliers[record["name"]] = record["id"]

    return suppliers


if __name__ == "__main__":
    get_supplier_names("suppliers.json")