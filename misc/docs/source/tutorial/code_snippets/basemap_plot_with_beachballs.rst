============================
Basemap Plot with Beachballs
============================

Basemap Plot of a Local Area
============================

The following example shows how to plot beachballs into a basemap plot together
with some stations. The example requires the basemap_ package (download_ site)
to be installed. The SRTM file used can be downloaded here_.

.. include:: basemap_plot_with_beachballs.py
   :literal:

The first lines of our SRTM data file (from
`CGIAR <http://srtm.csi.cgiar.org/>`_) look like this::

    ncols         400
    nrows         200
    xllcorner     12°40'E
    yllcorner     47°40'N
    xurcorner     13°00'E
    yurcorner     47°50'N
    cellsize      0.00083333333333333
    NODATA_value  -9999
    682 681 685 690 691 689 678 670 675 680 681 679 675 671 674 680 679 679 675 671 668 664 659 660 656 655 662 666 660 659 659 658 ....

.. plot:: source/tutorial/code_snippets/basemap_plot_with_beachballs.py

**Some notes:**

* The Python package GDAL_ allows you to directly read a GeoTiff into NumPy_
  :class:`~numpy.ndarray`

      >>> geo = gdal.Open("file.geotiff")  # doctest: +SKIP
      >>> x = geo.ReadAsArray()  # doctest: +SKIP

* GeoTiff elevation data is available e.g. from ASTER_
* Shading/Illumination can be added. See the basemap example plotmap_shaded.py_
  for more info.

.. _basemap: http://matplotlib.sourceforge.net/basemap/doc/html/index.html
.. _download: http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/
.. _here: http://examples.obspy.org/srtm_1240-1300E_4740-4750N.asc.gz
.. _NumPy: http://numpy.scipy.org/
.. _GDAL: http://trac.osgeo.org/gdal/wiki/GdalOgrInPython
.. _ASTER: http://www.gdem.aster.ersdac.or.jp/search.jsp
.. _plotmap_shaded.py: http://matplotlib.svn.sourceforge.net/viewvc/matplotlib/trunk/toolkits/basemap/examples/plotmap_shaded.py


Basemap Plot of the Globe
=========================

.. include:: basemap_plot_with_beachballs2.py
   :literal:

.. plot:: source/tutorial/code_snippets/basemap_plot_with_beachballs2.py
