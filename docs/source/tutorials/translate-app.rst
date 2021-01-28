Translate my application 
========================

Sepal tries to be as inclusive as possible. To do so the plateform is translated in 3 languages : English, Français and español. 
To reflect the diversity of language available, :code:`sepal_ui` embed an translator tool and help you manage your messages for differents languages. 


Update the main dictionary 
--------------------------

I assume that since you started using the lib you hard-coded in your files every single message displayed to the end user. 
The first thing you'll need to do is to update the main dictionnary as it will be your reference for the rest of the app. 

if you removed every message relative to the default functions, your dictionnary should look like the following : 

.. code-block:: python 

    # component/message/en.json

    {
        "not_translated": "this message only exist in the en dict",
        "app": {
            "title": "My first module",
            "footer": "The sky is the limit \u00a9 {}",
            "drawer_item": {
                "aoi": "AOI selection",
                "about": "About"
            }
        }
    }

Add new message 
^^^^^^^^^^^^^^^

here you gather and add every message you display in your app. 
For example if I want to display an error when no_aoi is set i can add the following input in the dictionnary : 

.. code-block:: python 

    # component/message/en.json

    {
        "error": {
            "no_aoi":  "No AOI have been set, please provide one in step 1"
        }
    }

.. danger::

    remember that JSON format does only accept " (double quote)

and to call in any of your component you just need to import the ms Translator and use the names you gave as namespaces : 

.. code-block:: python 

    # component/tile.my_tile.py

    from component.message import ms

    print(ms.error.no_aoi)

add message with parameter 
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to keep the possibility to use parameter in your message you can use the .format() method of Python string.  

.. note::

    The :code:`format()` method formats the specified value(s) and insert them inside the string's placeholder. The placeholder is defined using curly brackets: :code:`{}`. 
    Read more about the placeholders in the Placeholder `official documentation <https://docs.python.org/fr/3.5/library/string.html>`_. The :code:`format()` method returns the formatted string.

In our dictionnary that could be use in the following way:

.. code-block:: python 

    # component/message/en.json

    {
        "error": {
            "error_occured":  "The following error occured: {}"
        }
    }

and call it in your components for example in a try/Except statement : 

.. code-block:: python 

    # component/tile/my_tile.py

    try:
        # do stuff 
    except Exception as e:
        print(ms.error.error_occured.format(e))


Update the translated dictionnaries
-----------------------------------

If this is the first time you translate your app, the easyest way is to simply copy/paste all the english dictionnary (:code:`en.json`) into the target one (:code:`fr.json` or :code:`es.json`) and replace all the message with their accurate translation. 


If it's not the first translation you make you don't want to erase all you're already translated message. You only want to update the dictionnary with the new key. 
To pinpoint the missing keys you can use your memory or one of the Translator method. 
Open the :code:`component/message/test_translation.ipynb` notebook. change the :code:`locale` variable into your target language. Then run all cells. The last one will display all the missing keys in the dictionnary hierarchy.

.. code-block:: python 

    # component/message/test_translation.ipynb

    from pathlib import Path
    from sepal_ui.translator import Translator

    # select the language you want to test 
    locale = 'fr'

    # normally there is only one key lissing ('not_tranlated') in the default module
    # at the root of the file 
    print(ms.missing_keys())

    >>>>> root['not_translated']

Once your output message is "All messages are translated" it means that all the dictionnaries have the same keys and the same shape. if someone open your application in another language the translated message will be used instead of the english one.

.. note::

    If a key is missing in the target language dictionnary, the :code:`Translator` (:code:`ms`) will automattically fallback to the en key in order to avoid error or non displayed messages