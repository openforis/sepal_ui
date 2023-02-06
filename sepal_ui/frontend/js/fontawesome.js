/*******************************************************************************
 * remove any links from fontawesome 5 created by jupyter in favor of
 * fontawesome 6. to be removed when Jupyter updates it
 */

function remove_fa5() {
  links = document.querySelectorAll(
    "link[href^='https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@^5']"
  );

  links.forEach((link) => link.remove());
}

if (document.readyState != "loading") remove_fa5();
else document.addEventListener("DOMContentLoader", remove_fa5());
