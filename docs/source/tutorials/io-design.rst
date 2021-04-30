What are the io object and how to use them ? 
============================================

Philosophy
----------

When we started to develop the sepal_ui framework we face the input and output storage problem. Python is a very versatile language but base variable are not mutable objects. It means that if a value is manipulated inside a function, the changes won't be kept outside this very functions. 
the concept is easier to grasp with a simple example 

.. code-block:: python 

    def double(a)
        """multiply the value of a by two"""
        
        a *= 2

        return a 

    a = 4 
    res = double(a)

    print(a)
    print(res)

    >>>> 4
    >>>> 8

The value of a cannot be modified inside the function. 
For those who have practiced other languages such as C/C++, Fortran or Java, you know that it's possible to choose if the variable is passed to the function by reference or by value. 
The flexibility of Pyhton doesn't authorize this differences, there are just mutable and not mutable objects. 
2 solution were possible : either we return all the results from function to function (which could rapidly to a high number of tuples in the return statement) or use io objects to store inputs of our widgets and output of our processes. 

IO object 
---------

In this context we decided to store input and output in dedicated custom object created on this sole purpose. 
Each of them should be bind to tiles and used in the called processes

a default io could look like

.. code-block:: python 

    class CustomIo()

        def __init__(self):

            # inputs 
            self.username = None
            self.password = None
            
            # output 
            self.connection_url


And that's all !

Exemple case 
------------

We will here describe a complete example of the usage of an io. 

in a io component, I create my custom io 

.. code-block:: python

    # component/io/my_io.py

    class MyIo()

        def __init__(self, default_value = None):
            self.input = default_value
            self.output = None

I will also create a dummy script to use in my tile 

.. code-block:: python 

    # component/scripts/double.py

    def double(io):

        return io.input * 2

Now I can create a custom tile that will use the :code:`io` object as an input storage (linking :code:`io.input` to a slider). 
This :code:`io` will then be used in the :code:`_on_click` method of my tile. 
This function will modify the value of the :code:`io.output` attribute.

.. code-block:: python 

    # component/tile/my_tile.py 

    import ipyvuetify as v 
    from sepal_ui import sepalwidgets as sw

    from component.scripts import *

    class MyTile(sw.Tile):

        def __init__(self, io, **kwargs):

            self.io = io # save the io as an attribute of the tile 
            self.slider = v.Slider()
            self.output = sw.Alert().bind(self.slider, self.io, 'input')
            self.btn = sw.Btn()

            super()._init__('my_tile', 'Tile title', [self.slider], self.btn, self.output)

            self.btn.on_event('click', self._on_click)

        def _on_click(self, widget, data, event):

            widget.toggle_loading()
            self.output = io.double(io)
            widget.toggle_loading()

            return 

Now let's test our code in situation. W'll gather everything in a partial layout and see how the io object is changed persistently by the tile function 

.. code-block:: python 

    # double_ui.ipynb

    from component import io
    from component import tile

    my_io = MyIo(default_value = 5)
    my_tile = MyTile(my_io)

    # fake the bahviour of the btn 
    my_tile.btn.fire_event('click')

    print(my_io.__dict__)

    >>> 
    {
        'input': 5
        'output': 10
    }

The output have been persistently modified and can be used in other tiles in the final process built in :code:`ui.ipynb` or :code:`no_ui.ipynb`

Use the :code:`io` object for testing purpose
---------------------------------------------

When a new tile is created it can be bothering to launch the full app to gather all the information that we need to test our new component.
A good practice is to use fake io object in the partial ui files to reproduce the output of a previous step. 

let's assume that you process require 2 io object, a custom one and the :code:`aoi_io` object coming from the :code:`aoi_ui.ipynb`.

.. code-block:: python

    # my_ui.ipynb

    from component import io
    from component import tile 

    my_io = MyIo()
    my_tile = MyTile(my_io, aoi_io)

Then to test your partial UI, you need a set :code:`aoi_io` object with a asset_id value. 
In its current state, your notebook will raise an error as :code:`aoi_io` is not set. 
You can add it in a debugging cell at the very beginning of the :code:`my_ui.ipynb`.

.. code-block:: python

    # my_ui.ipynb 

    # for debug only 
    from sepal_ui import aoi_io

    aoi_io = aoi.AoiIo(default_asset = 'users/yourself/anAsset')

Now you have a perfectly working stand-alone notebook to test your process 

.. warning::

    Don't forget to comment or delete this cell when you finish testing. 
    If not, the output of your first steps will be overwritten in the ui and you will always end-up using the default one. 


Advanced usage of io object 
---------------------------

io objects are Python objects so they can also embed specific methods to help you build a better app.

In this framework the AOI selection is hard-coded in the :code:`AoiIo` object and the :code:`AoiTile` object. 
If you look at the documentation of the lib you'll see that :code:`AoiIo` has a lot of embedded useful method that you can call anywhere.
with the :code:`AoiIo.get_aoi_ee` method, you can get the AOI corresponding ee object as a variable. 

.. code-block:: python 

    from sepal_ui import aoi
    aoi_io = aoi.AoiIo(default_asset = 'users/yourself/anAsset')
    ee_object = aoi_io.get_aoi_ee()


In our previous example the double function is not a very useful scripts. instead we should have added it to the AOI member methods

.. code:: python 

    # component/io/my_io.py

    class MyIo()

        def __init__(self, default_value = None):
            self.input = default_value
            self.output = None

        def double(self):

            return self.input * 2



