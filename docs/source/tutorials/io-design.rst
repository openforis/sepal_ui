What are the :code:`Model` object and how to use them ? 
=======================================================

Philosophy
----------

When we started to develop the :code:`sepal_ui` framework we face the input and output storage problem. Python is a very versatile language but base variable are not mutable objects. It means that if a value is manipulated inside a function, the changes won't be kept outside this very functions. 
the concept is easier to grasp with a simple example 

.. code-block:: python 

    def double(a)
        """multiply the value of "a" by two"""
        
        a *= 2

        return a 

    a = 4 
    res = double(a)

    print(a)
    print(res)

    >>>> 4
    >>>> 8

The value of "a" cannot be modified inside the function. 
For those who have practiced other languages such as C/C++, Fortran or Java, you know that it's possible to choose if the variable is passed to the function by reference or by value. 
The flexibility of Pyhton doesn't authorize this difference, there are just mutable and not mutable objects. 
2 solution were possible: either we return all the results from function to function (which could rapidly lead to a high number of tuples in the return statement) or use :code:`Model` objects to store inputs of our widgets and output of our processes. 

Model object 
------------

In this context we decided to store input and output in dedicated custom object created for this sole purpose. 
Each of them should be bind to tiles and used in the called processes.

a default model could look like

.. code-block:: python 

    from sepal_ui import model
    from traitlets import Any # other types are available but Any can digest anything

    class CustomIo(model.Model): # the model class embed some useful fonction as 'export', 'import' and 'bind'

        # inputs 
        username = Any(None).tag(sync=True)
        password = Any(None).tag(sync=True)

        # output
        connection_url = Any(None).tag(sync=True)


And that's all !

Exemple case 
------------

We will here describe a complete example of the usage of a model. 

in a model component, I create my custom :code:`Model`. 

.. code-block:: python

    # component/io/my_model.py

    from sepal_ui import model
    from traitlets import Any

    class MyModel(model.Model)

        input = Any(None).tag(sync=True)
        output = Any(None).tag(sync=True)

        def __init__(self, default_value = None):

            self.input = default_value

I will also create a dummy script to use in my tile 

.. code-block:: python 

    # component/scripts/double.py

    def double(model):

        return model.input * 2

Now I can create a custom tile that will use the :code:`MyModel` object as an input storage (linking :code:`my_model.input` to a slider). 
This :code:`MyModel` will then be used in the :code:`_on_click` method of my tile. 
This function will modify the value of the :code:`my_model.output` trait.

.. code-block:: python 

    # component/tile/my_tile.py 

    import ipyvuetify as v 
    from sepal_ui import sepalwidgets as sw
    from sepal_ui.scripts.utils import loading_button

    from component.scripts import *

    class MyTile(sw.Tile):

        def __init__(self, model, **kwargs):

            self.slider = v.Slider()
            self.model = model.bind(self.slider, 'input') # save the model as an attribute of the tile 

            super()._init__('my_tile', 'Tile title', [self.slider], sw.Btn(), sw.Alert())

            self.btn.on_event('click', self._on_click)

        @loading_button()
        def _on_click(self, widget, data, event):

            self.model.output = io.double(io)

            return 

Now let's test our code in situation. W'll gather everything in a partial layout and see how the model object is changed persistently by the tile function 

.. code-block:: python 

    # double_ui.ipynb

    from component import model
    from component import tile

    my_model = MyModel(default_value = 5)
    my_tile = MyTile(my_model)

    # fake the behaviour of the btn 
    my_tile.btn.fire_event('click', None)

    print(my_model.__dict__['_trait_values'])

    >>> 
    {
        'input': 5
        'output': 10
    }

The output have been persistently modified and can be used in other tiles in the final process built in :code:`ui.ipynb` or :code:`no_ui.ipynb`

Use the :code:`model` object for testing purpose
------------------------------------------------

When a new tile is created it can be bothering to launch the full app to gather all the information that we need to test our new component.
A good practice is to use faked model object in the partial ui files to reproduce the output of a previous step. 

let's assume that you process require 2 model object, a custom one and the :code:`aoi_model` object coming from the :code:`aoi_ui.ipynb`.

.. code-block:: python

    # my_ui.ipynb

    from component import model
    from component import tile 

    my_model = MyModel()
    my_tile = MyTile(my_model, aoi_tile.view.model)

Then to test your partial UI, you need a set :code:`aoi_tile` object with a asset_id value. 
In its current state, your notebook will raise an error as :code:`aoi_tile.view.model` is not set. 
You can add it in a debugging cell at the very beginning of the :code:`my_ui.ipynb`.

.. code-block:: python

    # my_ui.ipynb 

    # for debug only 
    from sepal_ui import aoi

    aoi_tile = aoi.Aoitile(asset = 'users/yourself/anAsset')

Now you have a perfectly working stand-alone notebook to test your process 

.. warning::

    Don't forget to comment or delete this cell when you finish testing. 
    If not, the output of your first steps will be overwritten in the ui and you will always end-up using the default one. 


Advanced usage of io object 
---------------------------

model objects are Python objects so they can also embed specific methods to help you build a better app.

In this framework the AOI selection is hard-coded in the :code:`AoiIModel` object and the :code:`AoiView` object. 
If you look at the documentation of the lib you'll see that :code:`AoiModel` has a lot of embedded useful method that you can call anywhere.
e.g: with the :code:`AoiIo.total_bounds` method, you can get the AOI bounding box coordnates. 

.. code-block:: python 

    from sepal_ui import aoi
    aoi_model = aoi.AoiModel(asset = 'users/yourself/anAsset')
    bb = aoi_io.total_bounds()


In our previous example the double function is not a very useful scripts. instead we should have added it to the AOI member methods

.. code-block:: python

    # component/io/my_model.py

    from sepal_ui import model
    from traitlets import Any

    class MyModel(model.Model)

        input = Any(None).tag(sync=True)
        output = Any(None).tag(sync=True)

        def __init__(self, default_value = None):

            self.input = default_value

        def double(self):

            return self.input * 2



