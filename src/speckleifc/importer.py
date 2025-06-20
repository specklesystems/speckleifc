from typing import cast

from ifcopenshell.entity_instance import entity_instance
from ifcopenshell.geom import file
from ifcopenshell.ifcopenshell_wrapper import TriangulationElement
from specklepy.logging.exceptions import SpeckleException
from specklepy.objects import Base

from speckleifc.converter.data_object_converter import data_object_to_speckle
from speckleifc.converter.geometry_converter import geometry_to_speckle
from speckleifc.converter.project_converter import project_to_speckle
from speckleifc.converter.spatial_element_converter import spatial_element_to_speckle
from speckleifc.ifc_geometry_processing import create_geometry_iterator
from speckleifc.ifc_openshell_helpers import get_children
from speckleifc.render_material_proxy_manager import RenderMaterialProxyManager


class ImportJob:
    def __init__(self, ifc_file: file):
        self._ifc_file = ifc_file
        self.cached_display_values: dict[int, list[Base]] = {}
        self._render_material_manager = RenderMaterialProxyManager()

    def convert_element(self, step_element: entity_instance) -> Base:
        children = self._convert_children(step_element)
        display_value = self.cached_display_values.get(step_element.id(), [])

        if step_element.is_a("IfcProject"):
            return project_to_speckle(step_element, children)
        elif step_element.is_a("IfcSpatialStructureElement"):
            return spatial_element_to_speckle(display_value, step_element, children)
        else:
            return data_object_to_speckle(display_value, step_element, children)

    def _convert_children(self, step_element: entity_instance) -> list[Base]:
        return [self.convert_element(i) for i in get_children(step_element)]

    def convert(self) -> Base:
        self.pre_process_geometry()

        root = self._convert_project_tree()

        return root

    def pre_process_geometry(self) -> None:
        iterator = create_geometry_iterator(self._ifc_file)
        if not iterator.initialize():
            raise SpeckleException(
                "geometry iterator failed to initialize for the given file"
            )

        while True:
            shape = cast(TriangulationElement, iterator.get())

            id = cast(int, shape.id)

            display_value = geometry_to_speckle(shape, self._render_material_manager)
            self.cached_display_values[id] = display_value

            if not iterator.next():
                break

    def _convert_project_tree(self) -> Base:
        projects = self._ifc_file.by_type("IfcProject", False)
        if len(projects) != 1:
            raise SpeckleException("Expected exactly one IfcProject in file")
        project = projects[0]

        tree = self.convert_element(project)
        tree["renderMaterialProxies"] = list(
            self._render_material_manager.render_material_proxies.values()
        )

        return tree
