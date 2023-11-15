# napari-rembg

Select the foreground of images using AI in Napari. This plugin is based on the [rembg](https://github.com/danielgatis/rembg) project.

<p align="center">
    <img src="https://github.com/EPFL-Center-for-Imaging/napari-rembg/blob/main/assets/demo.gif" height="400">
</p>

### Why use `napari-rembg`?
- It runs **fast** even on a laptop's CPU (a few seconds per image).
- It is **easy to install** compared to other AI tools for segmentation.
- It is a **quick and easy** solution to automatically extract the foreground of scientific and natural images.

This plugin is primarily intended for analyzing **2D** and **2D (RGB)** images, however it can also be used to segment a particular slice in a **2D + time**, **2D + channel** or **3D** image.

## Installation

You can install `napari-rembg` via [pip]:

    pip install napari-rembg

## Usage

Start `napari-rembg` from the `Plugins` menu of Napari:

```
Plugins > Select foreground (napari-rembg)
```

**Regions of Interest**

You can insert a `Shapes` layer and **draw a rectangle** to define a Region of Interest (ROI) in which to run the foreground selection. Make sure to have only *a single rectangle* drawn in the `Shapes` layer 😉.

*Minor issue*: until [#5505](https://github.com/napari/napari/issues/5505) is fixed it won't be possible to use ROIs drawn in planes other than the default (XY).

**Multiple objects selection**

You can select the `Labels` layer in which to write the output of the foreground segmentation. The output label of the foreground will be the selected label of that `Labels` layer. This makes it possible to run the foreground selection multiple times (e.g. along different channels or in multiple ROIs) and to combine the results in a single `Labels` layer.


## Contributing

Contributions are very welcome. Please get in touch if you'd like to be involved in improving or extending the package.

## License

Distributed under the terms of the [BSD-3] license,
"napari-rembg" is free and open source software.

## Issues

If you encounter any problems, please file an issue along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.
