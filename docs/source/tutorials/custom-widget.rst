Create a custom widget
======================

In this tutorial we will show how to create a custom reusable widget. It will be then possible to use this widget in any tile. 

Requirements
------------

Vuetify has a huge number of component that can serve many purposes. Several others have been build in the sepal_ui librairi and can be found here. 
Sometimes a specific situation require complex assembly of multiple components. In this case it is better to create a custom widget rather than write numerous lines of code in your tile.  

Let's assume that you want to create a worklfow that require your end-user to fill credentials to access an API. for the username you'll surely decide to use a Textfield as : 

.. code-block:: python 

   import ipyvuetfy as v 

   username_field = v.TextField(
       label = "Username",
       placeholder = "Your API username",
       v_model = None
   )

But for the password you will have no built-in vuetify object to use. let's build a custom password widget that will be then use in our tile. We want : 

* a TextField like input 
* a eye btn to hide or show the password 
* a direct link to the io object to not display the password with the bind

.. note:: 

   When using the sepalwidgets.Alert.bind method, the value is displayed on the screen in plain text. If we want to keep the password secret, we need to bypass the use of this method

Design the object
-----------------

Create the file
^^^^^^^^^^^^^^^

Widget package is currently empty so we will create an extra :code:`password_field.py`. and add this file to the __init__.py file : 

.. code-block:: python 

    # component/widget/__init__.py 

    from .paswword_field import *

.. note::
    **Advanced user**  

    We here decided to use the web convention 1 file 1 object, which may sound weird for the most pythonic freeks. 
    If you prefer to use the **PEP 8** module convention. delete the widget folder and write everything in a widget.py module.

initialize the object
^^^^^^^^^^^^^^^^^^^^^

Here we will create the object with its expected attributes 

.. code-block:: python

    # component/widget/password_field.py

    import ipyvuetify as v 
    import sepal_ui.sepalwidgets as sw 

    class PasswordField(sw.SepalWidget, v.Layout):
   
        def __init__(self, label="Password", **kwargs):

            # create the eye icon
            self.eye = v.Icon(class_ = 'ml-1', children=['mdi-eye'])

            # create the texfied 
            self.text_field = v.TextField(
                type = 'password',
                label = label,
                v_model = None
            )

            # create the layout 
            super().__init__(
                row = True,
                children = [self.eye, self.text_field],
                **kwargs
            )


.. tip::

    Respect the writting convetion of python : :code:`CamelCase` for class and :code:`snake_case` for variables. 

Here we embed our widget in a line layout. In this layout I used 2 widgets, a :code:`v.TextField` and a :code:`v.Icon`. The eye is an eye icon from the `material design icon list <https://materialdesignicons.com>`_. 
I used the class "ml-1" (margin left 1) to let some room between the textfield and the password.
The text_field is using the keyword :code:`type` to display a :code:`password` in the HTML convention. it means that the input will no be displayed. 

toggle the visibility 
^^^^^^^^^^^^^^^^^^^^^

Now we want to add a behaviour to our object. When we click on the eye, the passwordField should toggle its visibility : 

* The eye should switch from :code:`mdi-eye` and :code:`mdi-eye-off`
* The text_field should switch from type :code:`password` to :code:`text`

To do so we will first add 2 class static variable (capslock) to list the 2 types and icon and set them on the two attributes of my class. a new attribute needs to be created to remind the current state of the password. 
I'll call it :code:`password_viz` as the :code:`viz` parameter is already an attribute of :code;`SepalWidget`. 

.. code-block:: python

    # component/widget/password_field.py

    import ipyvuetify as v 
    import sepal_ui.sepalwidgets as sw 

    class PasswordField(sw.SepalWidget, v.Layout):

        EYE_ICONS = ['mdi-eye', 'mdi-eye-off'] # new icon list
        TYPES = ['password', 'text'] # new type list
   
        def __init__(self, label="Password", **kwargs):

            # the viz attribute
            self.password_viz = False

            # create the eye icon
            self.eye = v.Icon(class_ = 'ml-1', children=[EYE_ICON[False]])

            # create the texfied 
            self.text_field = v.TextField(
                type = TYPES[False],
                label = label,
                v_model = None
            )

            # create the layout 
            super().__init__(
                row = True,
                children = [self.eye, self.text_field],
                **kwargs
            )

now I will create a funcion to dynamically switch the state of my password visibility. this class method should never be called outside the object so I'll add a '_' to start its name. 
It will be used as a callback function in a click event, so it will have the following 3 attributes : :code:`widget`, :code:`data`, :code:`event`.

.. code-block:: python

    def _toggle_viz(self, widget, event, data):

        viz = not self.password_viz

        # change the password viz
        self.password_viz = viz
        self.eye.children = [EYE_ICONS[viz]]
        self.text_field.type = self.TYPES[viz]

        return

called in the end of my :code:`__init__` method by 

.. code-block:: python 

    self.eye.on_event('click', self._toggle_viz)
   
link to the io_object
^^^^^^^^^^^^^^^^^^^^^

In it's current state I could be tempted to use my new object in a tile as such 

.. code-block:: python 

    # component/tile/my_tile.py

    from sepal_ui import sepalwidgets as sw 

    from component.widget import * 

    class MyTile(sw.Tile):

        def __init__(self, io, **kwargs):

            # create a password 
            self.password_field = PasswordField(label = 'PasswordField')

            # link it to io 
            self.output = sw.Alert().bind(self.password.text_field, io, 'password')

    # [...]

but then the password would be systematically displayed in the output. which is not what we want for a password. So instead we'll deal with the io injection inside our custom widget.
First we need to add the io to the widget attributes

.. code-block:: python 

    # component/widget/password_field.py

    def __init__(self, io, label="Password", **kwargs):

            # add the io to the attributes 
            self.io = io

    # [...]

and then observe the evolution of the text_field to update the io 'password' attribute. a complete documentation of the observe method can be found in the `Traitlet lib documentation <https://traitlets.readthedocs.io/en/stable/using_traitlets.html>`_.

def _on_change(self, change):

    self.io.password = change['new']

    return 

final password widget 
^^^^^^^^^^^^^^^^^^^^^

finally we obtain the following reusable widget : 

.. code-block:: python

    # component/widget/password_field.py

    import ipyvuetify as v 
    import sepal_ui.sepalwidgets as sw 

    class PasswordField(sw.SepalWidget, v.Layout):

        EYE_ICONS = ['mdi-eye', 'mdi-eye-off'] # new icon list
        TYPES = ['password', 'text'] # new type list
   
        def __init__(self, io, label="Password", **kwargs):

            # add the io to the attributes 
            self.io = io

            # the viz attribute
            self.password_viz = False

            # create the eye icon
            self.eye = v.Icon(class_ = 'ml-1', children=[EYE_ICON[False]])

            # create the texfied 
            self.text_field = v.TextField(
                type = TYPES[False],
                label = label,
                v_model = None
            )

            # create the layout 
            super().__init__(
                row = True,
                children = [self.eye, self.text_field],
                **kwargs
            )  

            # link the different functions 
            self.eye.on_event('click', self._toggle_viz) 
            self.text_field.observe(self._on_change, 'v_model')

        def _toggle_viz(self, widget, event, data):

            viz = not self.password_viz

            # change the password viz
            self.password_viz = viz
            self.eye.children = [EYE_ICONS[viz]]
            self.text_field.type = self.TYPES[viz]

            return 

        def _on_change(self, change):

            self.io.password = change['new']

            return


Usage 
-----

To reuse my object in a tile I should first import the widget component and then initialize it with all the other widgets 

.. code-block:: python 

    # component/tile/my_tile.py

    from sepal_ui import sepalwidgets as sw 

    from component.widget import * 

    class MyTile(sw.Tile):

        def __init__(self, io, **kwargs):

            # create a password 
            self.password_field = PasswordField(io, label = 'PasswordField')

            # create a username 
            username_field = v.TextField(
                label = "Username",
                placeholder = "Your API username",
                v_model = None
            )

            # link it to io 
            self.output = sw.Alert().bind(self.password.username_field, io, 'username')

    # [...]





