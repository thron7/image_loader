============
image_loader
============


A tool to load images from the internet.

Description
===========

- The tool will load images from the internet, the URLs of which are stored in a
  file, one URL per line. Empty lines are skipped.
- It uses both a thread and a connection pool, to make downloads more efficient.
- As a default, it checks for freshness of a local copy if there is already one,
  so an up-to-date image is not re-downloaded. Use the ``--force`` switch to force
  downloading images anyway.
- On downloading the ``Content-Type`` is checked and only ``image/*`` is
  accepted.
- Images are downloaded to a local directory. The path for that given on the
  command line is checked and created if it does not already exist. If the path
  already exists it must be a directory and must be writeable for the loader
  process.
- On downloading an image the local file is locked, so concurrent downloads of the same
  file will not interfer with each other. (This might be interesting if one
  instance of the script is started while another is still running with the same
  arguments.) If a lock cannot be obtained the particular URL is skipped.


Instructions
============

Installing
----------
- The script requires Python > 3.3.
- I recommend setting up a virtualenv.
- Run ``pip install -r requirements.txt`` to install dependencies.

Running
-------

- Basic invocation: ``'python src/image_loader/loader.py <urls file> <outdir>'``. 
  Use ``--help`` for full syntax.
- I recommend using at least the ``-v`` flag, otherwise the script will run silently.
- Constants, like the number of threads or connections, are in a dedicated section
  at the top of the script.
- Run ``pytest tests`` to run the automatic tests.

Deploying
---------

- Use ``'python setup.py install'`` from the root directory to create distribution for the tool.


Note
====

This project has been set up using PyScaffold 3.0.3. For details and usage
information on PyScaffold see http://pyscaffold.org/.
