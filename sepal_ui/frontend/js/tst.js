/* set a selected map to fullscreen */
var i = 0;
const wait_unitl_element_appear = setInterval(() => {
  if (i > 50) {
    const elements = document.querySelectorAll(
      ".vuetify-styles div.v-application--wrap"
    );
    const lastElement = elements[elements.length - 1];
    lastElement.style.minHeight = "100vh";
  } else {
    i++;
  }
}, 100);
