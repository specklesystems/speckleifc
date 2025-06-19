from typing import cast

from ifcopenshell.entity_instance import entity_instance
from specklepy.objects.base import Base
from specklepy.objects.data_objects import DataObject
from specklepy.objects.models.collections.collection import Collection


def spatial_element_to_speckle(
    display_value: list[Base],
    step_element: entity_instance,
    relational_children: list[Base],
) -> Collection:

    direct_geometry = _convert_as_data_object(display_value, step_element)
    all_children = [direct_geometry] + relational_children

    guid = cast(str, step_element.GlobalId)
    name = cast(str, step_element.Name or step_element.LongName or guid)

    data_object = Collection(applicationId=guid, name=name, elements=all_children)
    data_object["expressId"] = step_element.id()
    data_object["ifcType"] = step_element.is_a()

    return data_object


def _convert_as_data_object(
    display_value: list[Base], step_element: entity_instance
) -> DataObject:

    guid = cast(str, step_element.GlobalId)
    name = cast(str, step_element.Name or step_element.LongName or guid)
    data_object = DataObject(
        applicationId=guid,
        properties={},
        name=name,
        displayValue=display_value,
    )

    data_object["expressId"] = step_element.id()
    data_object["ifcType"] = step_element.is_a()
    data_object["description"] = cast(str | None, step_element.Description)
    data_object["objectType"] = step_element.ObjectType
    data_object["compositionType"] = step_element.CompositionType
    data_object["longName"] = step_element.LongName

    return data_object
