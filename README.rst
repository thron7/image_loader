============
image_loader
============


A tool to download images from the internet.

Description
===========

- The tool will load images from the internet, the URLs of which are stored in a
  file, one URL per line. Empty lines are skipped.
- On downloading the ``Content-Type`` is checked and only ``image/*`` is
  accepted.
- Images are downloaded to a local directory. The path for that is given on the
  command line, checked and created if it does not already exist. If the path
  exists it must be a directory and must be writeable for the loader
  process.
- If the number of downloaded files exceeds the number of available inodes of the target
  directory, an exception will be thrown.
- The tool does not take specific actions to set the access rights of the
  downloaded file. If the images are e.g. saved in a Web server's document tree
  it is the user's responsibility that the files are readable by the Web server.
- It also does not check for ``robots.txt`` files on the server side.
- Scaling
  - The runtime complexity of the tool directly depends on the size of the input
    file and to some extend on the diversity and responsiveness of the servers
    that host the source images.
  - I've implemented some defensive features to make sure the tool is
    well-behaved in demanding situations. Parameters to customize runtime
    behavior like memory and socket consumption are in a dedicated section in the script file. 
  - On downloading an image the local file is locked, so concurrent downloads of the same
    file will not interfer with each other. This might be interesting if one
    instance of the script is started while another is still running with the same
    arguments, e.g. when it is invoked via cron and a single
    run takes longer than the time until the next invocation. If a lock cannot 
    be obtained the particular URL is skipped.
  - It uses both a thread and a connection pool, to make downloads more efficient.
  - It does not, though, manage server load other than through the connection
    pools (e.g. no throttling).
  - As a default, it checks for freshness of a local copy if there already is one,
    so an up-to-date image is not re-downloaded. Use the ``--force`` switch to force
    downloading images anyway.
  - Having said that, you might run into issues with URL files with
    hundreds of thousand or even millions of entries.


Instructions
============

Installation
-------------
- The script requires Python > 3.3.
- I recommend setting up a virtualenv.
- Run ``pip install -r requirements.txt`` to install dependencies.

Running
-------

- Basic invocation
  - in a source environment: ``'python src/image_loader/loader.py <urls_file> <outdir>'`` 
  - in a deploy environment: ``'loader <urls_file> <outdir>'``

  Use ``--help`` for full syntax.
- I recommend using at least the ``-v`` flag, otherwise the script will run silently.
- Customizable constants, like the number of threads or connections, are in a dedicated section
  at the top of the script.
- Run ``'pip install pytest pytest-cov'`` and ``'pytest tests'`` in a source
  environment to run the automated tests.

Deployment
----------

- Use ``'python setup.py bdist_egg'`` or ``'... bdist_wheel'``, depending on
  your preferences, from the root directory to create a distribution for the tool.
- Copy the resulting ``dist/image_loader-*.{egg|whl}`` to a target machine.
- Install it there with ``easy_install`` or ``pip``, respectively.


Note
====

This project has been set up using PyScaffold 3.0.3. For details and usage
information on PyScaffold see http://pyscaffold.org/.
