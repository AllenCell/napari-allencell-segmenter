import logging
from napari_aicssegmentation.util.debug_utils import debug_class, debug_func

logging.basicConfig(level=logging.DEBUG)

#@for_all_methods(debug_log)
@debug_class
class MyClass:
    def __init__(self, i: int):
        self._i = i
        
    def hello(self):
        print("hello")

    def world(self):
        print("world")


obj = MyClass(1)
obj.hello()
obj.world()
