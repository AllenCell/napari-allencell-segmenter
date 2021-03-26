from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget

class ViewMeta(type(QWidget), type(ABC)):
    pass

class View(ABC, QWidget, metaclass=ViewMeta):
    """
    Base class for all Views to derive from
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

    @abstractmethod
    def setup_ui(self):
        """
        Construct the view's UI hierarchy
        """
        pass

# class View(ABC):
#     _template = None

#     def __init__(self, template_type: Type = None):
#         if template_type is not None:
#             if not issubclass(template_type, ViewTemplate):
#                 raise TypeError(f"Template type must be a subclass of {ViewTemplate}")
            
#             self._template = template_type()
        
#     @property
#     def template(self):
#         """
#         Returns the view template
#         """
#         return self._template

#     def has_template(self) -> bool:
#         """
#         True if the view has a template view, False otherwise
#         """
#         return self.template is not None

#     @abstractmethod
#     def get_layout(self) -> QLayout:
#         """
#         Get the view's main layout 
#         This should be top level layout of the view. This layout can contain nested child layouts.
#         """
#         pass

#     @abstractmethod
#     def setup_ui(self):
#         """
#         Construct the view's UI hierarchy
#         """
#         pass

# class ViewTemplate(View):
#     @abstractmethod
#     def get_container_layout(self):
#         """
#         Get the template's container layout
#         This should be an inner / child layout in which the child View or ViewTemplate be displayed
#         """
#         pass