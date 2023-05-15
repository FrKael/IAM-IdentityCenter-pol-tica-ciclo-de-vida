import chevron


def html(amis):
    props = [
        {
            "id": x["ImageId"],
            "date": x["CreationDate"],
            "name": x.get("Name", "")
        }
        for x in amis
    ]

    with open("template.mu") as f:
        return chevron.render(f, props)
